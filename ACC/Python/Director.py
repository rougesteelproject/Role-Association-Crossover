from flask import Flask, render_template, request, redirect
app = Flask(__name__)

#TODO replace exceptions with traceback.print_exc()
#TODO split classes to their own pages w/ their related funtions

import distutils
import distutils.util
from DatabaseControler import DatabaseControler
from CharacterConnector import CharacterConnector
from WikiPageGenerator import WikiPageGenerator
import ConnectorAndBarSearch as CB_search


db_control = DatabaseControler()
db_control.create_connection()

wiki_page_generator = WikiPageGenerator(db_control)
search = CB_search(db_control)
character_connector = CharacterConnector(db_control)

#TODO more intuitive variable names, a sweep to make it pythonic
#   functions modify lists, so we don't neet to return them. 


#TODO replace some of the url variables and redirects to other pages with a 
# if request.method == 'POST':
#and get the values of the form

#TODO what does this belong to, the editor?
def add_image(page_type, page_id, image_url, caption):
    db_control.add_image(page_type, page_id, image_url, caption)

#TODO each route could reference a class 

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
    displayed_MRs, actor_bios, base_name = wiki_page_generator.getContent(baseID, base_is_actor, level)
    return render_template('actor_template.html', base_name=base_name, blurb_editor_link="", hub_sigils="", actor_bios = actor_bios, displayed_MRs = displayed_MRs, baseID=baseID, base_is_actor=base_is_actor, level=level)

@app.route('/roles/editor', methods = ['GET', 'POST'])
def editor():
    if request.method == 'POST':
        new_description  = request.form['description']
        editorName = request.form['name']
        editorID = request.form['editorID']
        editorType = request.form['type']
        goBackUrl = request.form['goBackUrl']
        if editorType == 'role':
            editor_description = db_control.select("description", "roles", "id", editorID)
            getDescSQL= "SELECT description FROM roles WHERE id=?"
            db_control.cursor.execute(getDescSQL,(editorID,))
            editor_description = db_control.cursor.fetchall()[0][0]
            historySql = '''INSERT INTO roles_history(id, name, description) VALUES (?,?,?) '''
            db_control.cursor.execute(historySql,(editorID, editorName, editor_description))
            changeDescSql='''UPDATE roles SET description=? WHERE id=?'''
            db_control.cursor.execute(changeDescSql,(new_description,editorID,))
        elif editorType == 'actor':
            getDescSQL= "SELECT bio FROM actors WHERE id=?"
            db_control.cursor.execute(getDescSQL,(editorID,))
            editor_description = db_control.cursor.fetchall()[0][0]
            historySql = '''INSERT INTO actors_history(id, name, description) VALUES (?,?,?) '''
            db_control.cursor.execute(historySql,(editorID, editorName, editor_description))
            changeDescSql='''UPDATE actors SET bio=? WHERE id=?'''
            db_control.cursor.execute(changeDescSql,(new_description,editorID,))
        elif editorType == 'mr':
            getDescSQL= "SELECT description FROM meta_roles WHERE id=?"
            db_control.cursor.execute(getDescSQL,(editorID,))
            editor_description = db_control.cursor.fetchall()[0][0]
            historySql = '''INSERT INTO meta_roles_history(id, name, description) VALUES (?,?,?) '''
            db_control.cursor.execute(historySql,(editorID, editorName, editor_description))
            changeDescSql='''UPDATE meta_roles SET description=? WHERE id=?'''
            db_control.cursor.execute(changeDescSql,(new_description,editorID,))
        else:
            pass
        db_control.commit()
        return redirect(goBackUrl)
    else:
        editorID = request.args['editorID']
        editorType= request.args['editorType']
        goBackUrl = request.referrer
        name = request.args['name']
        history = wiki_page_generator.get_history(editorID, editorType)
        if editorType == 'actor':
            getDescSQL= "SELECT bio FROM actors WHERE id=?"
            db_control.cursor.execute(getDescSQL,(editorID,))
        elif editorType == 'mr':
            getDescSQL= "SELECT description FROM meta_roles WHERE id=?"
            db_control.cursor.execute(getDescSQL,(editorID,))
        elif editorType == 'role':
            getDescSQL= "SELECT description FROM roles WHERE id=?"
            db_control.cursor.execute(getDescSQL,(editorID,))
        else:
            pass
        editor_description = db_control.cursor.fetchall()[0][0]

        #TODO as the database gets bigger (pictures, bio, etc, blurb_editor will have to, also)
        return render_template('blurb_editor.html', editorID=editorID, editorType=editorType, goBackUrl=goBackUrl, name=name, description=editor_description, history=history)
       
@app.route('/character_connector/', methods = ['GET','POST'])
def character_connector():
    return render_template('cc_search.html')
    
@app.route('/character_connector/results/', methods = ['GET', 'POST'])
def results(): 
    #TODO have this display the parent mrs, too, so you see what you're dealing with
    #TODO make this drag and drop
    name_1 = request.args.get('role1')
    name_2 = request.args.get('role2')
    connector_mrs = search.mrSearchResults(name_1)
    connector_mrs2 = search.mrSearchResults(name_2)

    return render_template('character_combiner.html', connector_mrs=connector_mrs, connector_mrs2=connector_mrs2, name_1=name_1, name_2=name_2)
    
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
        elif mode == "removeMR":
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

    add_image(page_type, page_id, uploaded_file.filename, caption)
    return(redirect(go_back_url))

@app.route('/search')
def search():
    query = request.args['query']
    search_mrs, search_actors = search.searchBar(query)
    return render_template('search.html', search_mrs=search_mrs, search_actors=search_actors)

app.run(port=5000)