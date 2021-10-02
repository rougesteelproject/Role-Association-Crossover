from os import name

from flask.helpers import url_for
from new_wiki_page_gen import WikiPageGenerator
from search import Search
from database_controller import DatabaseController
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

#TODO replace exceptions with traceback.print_exc()

import distutils
import distutils.util

db_control = DatabaseController()
db_control.create_connection()
db_control.create_db_if_not_exists()

#TODO more intuitive variable names, a sweep to make it pythonic
#TODO variable types with (name: type)
#   functions modify lists, so we don't neet to return them. 

#TODO a page with everybody, alphabetically

#TODO a way to add user-made roles to replace the ... or 'additional voices' for actorw w/ multiple roles, like in skyrim

@app.route('/')
def index():
    #TODO generate featured articles based off of hits or connections (after the webview/ hub sigils works)
    return render_template('index.html')

@app.route('/roles/', methods = ['GET', 'POST'])
def wiki():
    #?my_var=my_value
    level = int(request.args['level'])
    baseID = request.args['base_id']
    base_is_actor = bool(distutils.util.strtobool(request.args['base_is_actor']))
    print(f'director: id to fetch: {baseID}')
    enable_actor_swap = request.form.get('enable_actor_swap')
    
    wiki_page_generator = WikiPageGenerator(baseID, level, base_is_actor, enable_actor_swap, db_control)
    wiki_page_generator.generate_content()
    return render_template('wiki_template.html', generator=wiki_page_generator, blurb_editor_link="", hub_sigils="" )
       
@app.route('/editor/actor', methods = ['GET','POST'])
def actor_editor():

    if request.method == 'POST':

        editorID = request.form['editorID']
        goBackUrl = request.form['goBackUrl']

        if "bio_editor" in request.form:
            new_bio  = request.form['bio']

            #gets the old desc, plops it into history, then replaces it with the new
            db_control.create_actor_history(editorID,new_bio)
            db_control.commit()

        if "history_reverter" in request.form:
            new_bio  = request.form['bio']
            
            db_control.create_actor_history(editorID,new_bio)
            db_control.commit()

        if "ability_remover" in request.form:
            abilities_to_remove = request.form.getlist('remove_ability')
            db_control.remove_ability_actor(editorID, abilities_to_remove)
            db_control.commit()

        if "ability_adder" in request.form:
            abilities_to_add = request.form.getlist('add_ability')
            db_control.add_ability_actor(editorID, abilities_to_add)
            db_control.commit()

        if "relationship_adder" in request.form:
            actor1_id =request.form['actor1_id']
            actor1_name = request.form['actor1_name']
            actor2_id, actor2_name = request.form['actor2'].split('|')
            type = request.form['relationship_type']
            db_control.add_relationship(actor1_id,actor1_name,actor2_id, actor2_name, type)
            db_control.commit()

        if "relationship_remover" in request.form:
            relationship_ids = request.form.getlist('remove_relationship')
            db_control.remove_relationships_actor(relationship_ids)
            db_control.commit()

        

            
    else:
        editorID = request.args['editorID']
        goBackUrl = request.referrer
        
        #a list of all histry entries

    actor = db_control.get_actor(editorID)
    history = db_control.get_actor_history(editorID)
    abilities_that_are_not_connected = db_control.get_ability_list_exclude_actor(actor.id)

    all_actors = db_control.get_all_actors()

    return render_template('actor_editor.html', goBackUrl=goBackUrl, actor=actor, history=history, abilities_that_are_not_connected=abilities_that_are_not_connected, all_actors=all_actors)

@app.route('/editor/meta', methods = ['GET','POST'])
def mr_editor():

    #WHen the user presses 'Submit'
    if request.method == 'POST':
        new_description  = request.form['description']
        editorID = request.form['editorID']
        goBackUrl = request.form['goBackUrl']
        #gets the old desc, plops it into history, then replaces it with the new
        db_control.create_mr_history(editorID,new_description)
        db_control.commit()
        return redirect(goBackUrl)
    else:
        editorID = request.args['editorID']
        goBackUrl = request.referrer
        history = db_control.get_mr_history(editorID)
        #a list of all histry entries

        mr = db_control.get_mr(editorID)

        return render_template('mr_editor.html', goBackUrl=goBackUrl, mr=mr, history=history)

@app.route('/editor/role', methods = ['GET','POST'])
def role_editor():
    #When the user presses 'Submit'
    if request.method == 'POST':
        editorID = request.form['editorID']
        goBackUrl = request.form['goBackUrl']
        
        if "description_editor" in request.form:
            new_description  = request.form['description']
            alignment = request.form['alignment']
            alive_or_dead = request.form['alive_or_dead']
            #gets the old desc, plops it into history, then replaces it with the new
            db_control.create_role_history(editorID,new_description, alive_or_dead, alignment)
            db_control.commit()

        if "history_reverter" in request.form:
            new_description  = request.form['description']
            alignment = request.form['alignment']
            alive_or_dead = request.form['alive_or_dead']
            db_control.create_role_history(editorID,new_description, alive_or_dead, alignment)
            db_control.commit()

        if "ability_remover" in request.form:
            abilities_to_remove = request.form.getlist('remove_ability')
            db_control.remove_ability_role(editorID, abilities_to_remove)
            db_control.commit()

        if "ability_adder" in request.form:
            abilities_to_add = request.form.getlist('add_ability')
            db_control.add_ability_role(editorID, abilities_to_add)
            db_control.commit()

        if "relationship_adder" in request.form:
            role1_id =request.form['role1_id']
            role1_name = request.form['role1_name']
            role2_id, role2_name = request.form['role2'].split('|')
            type = request.form['relationship_type']
            db_control.add_relationship_role(role1_id,role1_name,role2_id, role2_name, type)
            db_control.commit()

        if "relationship_remover" in request.form:
            relationship_ids = request.form.getlist('remove_relationship')
            db_control.remove_relationships_role(relationship_ids)
            db_control.commit()

    else:
        editorID = request.args['editorID']
        goBackUrl = request.referrer
    
    history = db_control.get_role_history(editorID)
    #a list of all histry entries

    role = db_control.get_role(editorID)

    abilities_that_are_not_connected = db_control.get_ability_list_exclude_role(role.id)

    all_roles = db_control.get_all_roles()

    return render_template('role_editor.html', goBackUrl=goBackUrl, role=role, history=history, abilities_that_are_not_connected=abilities_that_are_not_connected, all_roles=all_roles)
        
@app.route('/character_connector', methods = ['GET','POST'])
def character_connector():
    if "search-submit" in request.form:

        #TODO make this drag and drop?
        name_1 = request.form['name_1']
        name_2 = request.form['name_2']
        search_1 = Search(db_control)
        search_2 = Search(db_control)
        search_1.mrSearchResults(name_1)
        search_2.mrSearchResults(name_2)
        results_1 = search_1.displayed_mrs
        results_2 = search_2.displayed_mrs

        return render_template('character_connector.html',have_results=True, connector_mrs=results_1, connector_mrs2=results_2, name_1=name_1, name_2=name_2)

    if "matcher-submit" in request.form:
        id1 = request.form['id1']
        id2 = request.form['id2']
        mode = request.form['mode']

        db_control.character_connector_switch(mode,id1,id2)

        name_1 = request.form['name_1']
        name_2 = request.form['name_2']
        search_1 = Search(db_control)
        search_2 = Search(db_control)
        search_1.mrSearchResults(name_1)
        search_2.mrSearchResults(name_2)
        results_1 = search_1.displayed_mrs
        results_2 = search_2.displayed_mrs

        return render_template('character_connector.html', have_results=True ,connector_mrs=results_1, connector_mrs2=results_2, name_1=name_1, name_2=name_2)

    return render_template('character_connector.html', have_results = False)

@app.route('/webview', methods=['GET', 'POST'])
def webview():
    return render_template('webview.html')

@app.route('/submit_image', methods=['POST'])
def submit_image():
    page_type=request.form['typeImg']
    page_id = request.form['IDImg'] 
    caption = request.form['caption']
    uploaded_file = request.files['file']
    go_back_url = request.form['goBackUrlImg']
    if uploaded_file.filename != '':
        uploaded_file.save('static/' + uploaded_file.filename)

    db_control.add_image(page_type, page_id, uploaded_file.filename, caption)
    return(redirect(go_back_url))
    #TODO this needs to stay on the same page, instead
        #a form with stay_here url or something (request.referer?)

@app.route('/search')
def search():
    search_bar = Search(db_control)
    query = request.args['query']
    search_bar.searchBar(query)
    return render_template('search.html', search_mrs = search_bar.displayed_mrs, search_actors = search_bar.displayed_actors)

@app.route('/editor/ability', methods=['POST'])
def ability_editor():
    
    goBackUrl = request.referrer
    ability_id = request.args['id']
    ability = db_control.get_ability(ability_id)
    history = db_control.get_ability_history(ability_id)
    return render_template('ability_editor.html',ability=ability, history=history, goBackUrl=goBackUrl)

#TODO ability template editor

@app.route('/create_ability', methods=['POST'])
def create_ability():
    if "create_ability" in request.form:
        name = request.form['name']
        description = request.form['description']
        goBackUrl = request.form['goBackUrl']

        ability_id = db_control.create_ability(name, description)
        
        ability = db_control.get_ability(ability_id)
        history = db_control.get_ability_history(ability_id)

        return render_template('ability_editor.html', ability=ability, history=history, goBackUrl=goBackUrl)
        
        #create the ability using db_cont, then go to ability_editor
    else:
        goBackUrl = request.referrer
        #render the template with the form (the normal response to this link)
        return render_template('create_ability.html', goBackUrl=goBackUrl)

app.run(port=5000)