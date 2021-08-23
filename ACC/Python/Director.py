from os import name
from character_connector import CharacterConnector
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

character_connector = CharacterConnector(db_control)

#TODO more intuitive variable names, a sweep to make it pythonic
#   functions modify lists, so we don't neet to return them. 


#TODO replace some of the url variables and redirects to other pages with a 
# if request.method == 'POST':
#and get the values of the form

#TODO a page with everybody, alphabetically

@app.route('/')
def index():
    #TODO generate featured articles based off of hits or connections (after the webview/ hub sigils works)
    return render_template('index.html')

@app.route('/roles/', methods = ['GET', 'POST'])
def roles():
    #?my_var=my_value
    level = float(request.args['level'])
    baseID = request.args['baseID']
    base_is_actor = bool(distutils.util.strtobool(request.args['base_is_actor']))
    
    wiki_page_generator = WikiPageGenerator(db_control, baseID, base_is_actor=base_is_actor, level=level)
    wiki_page_generator.set_content()
    return render_template('actor_template.html', base_name=wiki_page_generator.base_name, blurb_editor_link="", hub_sigils="", displayed_actors= wiki_page_generator.displayed_actors, displayed_MRs = wiki_page_generator.displayed_MRs, halfway = wiki_page_generator.halfway_mrs,baseID=wiki_page_generator.baseID, base_is_actor=wiki_page_generator.base_is_actor, level=wiki_page_generator.level)
       
@app.route('/role/editor/actor', methods = ['GET','POST'])
def actor_editor():
    #TODO editors for powers, relationships (just like the history)
    #WHen the user presses 'Submit'
    if request.method == 'POST':
        #TODO get the other database elements here
        new_description  = request.form['description']
        editorID = request.form['editorID']
        goBackUrl = request.form['goBackUrl']
        #gets the old desc, plops it into history, then replaces it with the new
        db_control.create_actor_history(editorID,new_description)
        db_control.commit()
        return redirect(goBackUrl)
    else:
        editorID = request.args['editorID']
        goBackUrl = request.referrer
        history = db_control.get_history(editorID, "actor")
        #a list of all histry entries

        person = db_control.get_actor(editorID)

        #TODO new tamplates for all three
        return render_template('blurb_editor.html', goBackUrl=goBackUrl, person=person, history=history)


@app.route('/character_connector/', methods = ['GET','POST'])
def character_connector():
    return render_template('cc_search.html')
    
@app.route('/character_connector/results/', methods = ['GET', 'POST'])
def results(): 
    #TODO have this display the parent mrs, too, so you see what you're dealing with
    #TODO make this drag and drop
    name_1 = request.args.get('role1')
    name_2 = request.args.get('role2')
    search_1 = Search(db_control)
    search_2 = Search(db_control)
    search_1.mrSearchResults(name_1)
    search_2.mrSearchResults(name_2)
    results_1 = search_1.displayed_mrs
    results_2 = search_2.displayed_mrs

    return render_template('character_combiner.html', connector_mrs=results_1, connector_mrs2=results_2, name_1=name_1, name_2=name_2)
    
@app.route('/character_connector/submit', methods = ['GET', 'POST'])
def submit():
    
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    mode = request.args.get('mode')

    if id1 != None and id2 != None:
        #TODO create a splitter function that makes two MR's with roles divided based on their id (maybe two lists of id's to check against?)
        if mode == "addMR":
            id1 = id1.split('|')[0] #0 is the role of id 1
            id2 = id2.split('|')[1] #the mr of id2
            try:
                int(id2)
            except ValueError:
                print (f'Invalid ID for opperation: {mode}')
            else:
                #code to run on sucessful try
                character_connector.addMR(id1, id2)
        elif mode == "resetMR":
            id1 = id1.split('|')[0] #0 is the role of id 1
            character_connector.resetMR(id1)
        elif mode == "mergeMR":
            id1 = id1.split('|')[1] #1 is the mr of id 1
            id2 = id2.split('|')[1] #the mr of id2
            try:
                int(id2)
            except ValueError:
                print (f'Invalid ID for opperation: {mode}')
            else:
                try:
                    int(id1)
                except ValueError:
                    print (f'Invalid ID for opperation: {mode}')
                else:
                    character_connector.mergeMR(id1, id2)
        elif mode == "actorSwap":
            id1 = id1.split('|')[0] #0 is the role of id 1
            id2 = id2.split('|')[0] #0 is the role of id 2
            #Actor swaps are also first-come for ids.
            #Creating an actor_swap adds a swap ID to both roles
            character_connector.actorSwap(id1, id2)
        elif mode == "removeActorSwap":
            id1 = id1.split('|')[0] #0 is the role of id 1
            character_connector.removeActorSwap(id1)
        else:
            print(f'Opperation \'{mode}\' does not exist.')

    return render_template('cc_search.html')

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
    query = request.args['query']
    search_mrs, search_actors = cb_search.searchBar(query)
    return render_template('search.html', search_mrs=search_mrs, search_actors=search_actors)

app.run(port=5000)