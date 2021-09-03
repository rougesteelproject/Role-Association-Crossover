from os import name
from wiki_page_generator import WikiPageGenerator
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
#   functions modify lists, so we don't neet to return them. 


#TODO replace some of the url variables and redirects to other pages with a 
# if request.method == 'POST':
#get from the POST using request.form

#TODO a page with everybody, alphabetically



@app.route('/')
def index():
    #TODO generate featured articles based off of hits or connections (after the webview/ hub sigils works)
    return render_template('index.html')

@app.route('/roles/', methods = ['GET', 'POST'])
def wiki():
    #?my_var=my_value
    level = float(request.args['level'])
    baseID = request.args['baseID']
    base_is_actor = bool(distutils.util.strtobool(request.args['base_is_actor']))
    
    wiki_page_generator = WikiPageGenerator(db_control, baseID, base_is_actor=base_is_actor, level=level)
    wiki_page_generator.set_content()
    return render_template('wiki_template.html', generator=wiki_page_generator, blurb_editor_link="", hub_sigils="" )
       
@app.route('/role/editor/actor', methods = ['GET','POST'])
def actor_editor():
    #TODO relationship editor similar to character connector
    #TODO power edotor similar to char connector
    if request.method == 'POST':
        #'Submit'
        new_bio  = request.form['bio']
        editorID = request.form['editorID']
        goBackUrl = request.form['goBackUrl']
        #gets the old desc, plops it into history, then replaces it with the new
        db_control.create_actor_history(editorID,new_bio)
        db_control.commit()
        return redirect(goBackUrl)
    else:
        editorID = request.args['editorID']
        goBackUrl = request.referrer
        history = db_control.get_actor_history(editorID)
        #a list of all histry entries

        actor = db_control.get_actor(editorID)

        return render_template('actor_editor.html', goBackUrl=goBackUrl, actor=actor, history=history)

@app.route('/role/editor/meta', methods = ['GET','POST'])
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

@app.route('/role/editor/role', methods = ['GET','POST'])
def role_editor():
    #TODO relationship editor similar to character connector
    #TODO power edotor similar to char connector
    #WHen the user presses 'Submit'
    if request.method == 'POST':
        new_description  = request.form['description']
        editorID = request.form['editorID']
        goBackUrl = request.form['goBackUrl']
        alignment = request.form['alignment']
        alive_or_dead = request.form['alive_or_dead']
        #gets the old desc, plops it into history, then replaces it with the new
        db_control.create_role_history(editorID,new_description)
        db_control.commit()
        return redirect(goBackUrl)
    else:
        editorID = request.args['editorID']
        goBackUrl = request.referrer
        history = db_control.get_role_history(editorID)
        #a list of all histry entries

        role = db_control.get_role(editorID)

        return render_template('role_editor.html', goBackUrl=goBackUrl, role=role, history=history)
        
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

        name_1 = request.form['role1']
        name_2 = request.form['role2']
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

@app.route('/search')
def search():
    search_bar = Search(db_control)
    query = request.args['query']
    search_bar.searchBar(query)
    return render_template('search.html', search_bar.displayed_mrs, search_bar.displayed_actors)

@app.route('/ability')
def ability_editor():
    goBackUrl = request.referrer
    ability_id = request.args['id']
    ability = db_control.get_ability(ability_id)
    history = db_control.get_ability_history(ability_id)
    return render_template('ability_editor.html',ability, history, goBackUrl)

app.run(port=5000)