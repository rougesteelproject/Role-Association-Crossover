from flask import Flask, render_template, request, redirect
app = Flask(__name__)

#TODO replace exceptions with traceback.print_exc()
#TODO split classes to their own pages w/ their related funtions

import distutils
import distutils.util
import DatabaseControler
import Role as role_class
import Image as image_class
import CharacterConnector
import ActorBio as actor_bio_class

db_control = DatabaseControler
db_control.create_connection()

#TODO more intuitive variable names, a sweep to make it pythonic
#   functions modify lists, so we don't neet to return them. 

#TODO replace sql
def mrSearchResults(query):
    query = f'%{query}%'
    displayed_connector_mrs = []
    connector_class_roles = []
    sql = "SELECT * FROM roles WHERE name LIKE ?"
    cursor.execute(sql, (query,))
    
    connector_roles = cursor.fetchall()
    for role in connector_roles:
        connector_class_roles.append(role_class(role[0],role[1],role[2],role[3],role[4],role[5]))
    for connector_role_class in connector_class_roles:
        connector_mr_exists = check_mr_exists_already(connector_role_class.parent_meta,displayed_connector_mrs)
        if connector_mr_exists:
            append_role_to_mr(connector_role_class.name, displayed_connector_mrs, connector_role_class)
        else:
            sql = "SELECT name, description FROM meta_roles WHERE id=?"
            cursor.execute(sql, (role[2],))
            mrs = cursor.fetchone()
            new_connector_mr = MR_class([role], role[2], mrs[0], mrs[1])
            displayed_connector_mrs.append(new_connector_mr)
    
    return displayed_connector_mrs

#TODO make the search bar it's own class?
def searchBarRemoveMRDuplicates(mr_list):  
    new_mr_list = []
    for mr in mr_list:
        exists_already = False
        for new_mr in new_mr_list:
            if mr.id == new_mr.id:
                exists_already = True
        if exists_already == False:
            new_mr_list.append(mr)    
    return new_mr_list

def searchBarRemoveActorDuplicates(actor_list):
    new_actor_list = []
    for actor in actor_list:
        exists_already = False
        for new_actor in new_actor_list:
            if actor.id == new_actor.id:
                exists_already = True
        if exists_already ==False:
            new_actor_list.append(actor)
    return new_actor_list

#TODO replace sql
def searchBar(query):
    query = f'%{query}%'
    displayed_search_mrs = []
    displayed_search_actors = []
    search_actors= []
    search_mrs = []

    searchRolesSql = "SELECT parent_actor, parent_meta FROM roles WHERE name LIKE ?"
    cursor.execute(searchRolesSql, (query,))
    search_actors_and_mrs = cursor.fetchall()
    
    for result in search_actors_and_mrs:
        search_actors.append(result[0])
        search_mrs.append(result[1])
    list(dict.fromkeys(search_actors))
    list(dict.fromkeys(search_mrs))
    searchActorsSql = "SELECT name, bio FROM actors WHERE id=?"
        
    for actor_id in search_actors:
        cursor.execute(searchActorsSql, (actor_id,))
        actor_names_bios = cursor.fetchall()
        for actor_name_bio in actor_names_bios:
            search_actor_name = actor_name_bio[0]
            search_actor_bio = actor_name_bio[1]
            new_search_actor = actor_bio_class(search_actor_bio,actor_id,search_actor_name)
            displayed_search_actors.append(new_search_actor)
    
    searchMrsSql = "SELECT name, description FROM meta_roles WHERE id=?"
    for mr_id in search_mrs:
        cursor.execute(searchMrsSql, (mr_id,))
        search_mr_names_descs = cursor.fetchall()
        for search_mr_name_desc in search_mr_names_descs:
            search_mr_name = search_mr_name_desc[0]
            search_mr_desc = search_mr_name_desc[1]
            new_search_mr = mr_desc_class(search_mr_desc,mr_id,search_mr_name)
            displayed_search_mrs.append(new_search_mr)

    searchActorsSql = "SELECT bio, id, name FROM actors WHERE name LIKE ?"
    cursor.execute(searchActorsSql, (query,))
    like_search_actors = cursor.fetchall()
    for like_actor in like_search_actors:
        new_search_actor = actor_bio_class(like_actor[0], like_actor[1], like_actor[2])
        displayed_search_actors.append(new_search_actor)

    searchMrsSql = "SELECT description, id, name FROM meta_roles WHERE name LIKE ?"
    cursor.execute(searchMrsSql, (query,))
    like_search_mrs = cursor.fetchall()
    for like_mr in like_search_mrs:
        new_search_mr = mr_desc_class(like_mr[0], like_mr[1], like_mr[2])
        displayed_search_mrs.append(new_search_mr)

    
    displayed_search_mrs = searchBarRemoveMRDuplicates(displayed_search_mrs)
    displayed_search_actors = searchBarRemoveActorDuplicates(displayed_search_actors)

    return displayed_search_mrs, displayed_search_actors

#TODO replace some of the url variables and redirects to other pages with a 
# if request.method == 'POST':
#and get the values of the form

#TODO what does this go to, the editor?
def add_image(page_type, page_id, image_url, caption):
    if page_type == 'actor':
        sql = '''INSERT INTO gallery (file, actor, caption) VALUES (?,?,?)'''
    else:
        sql = '''INSERT INTO gallery (file, role, caption) VALUES (?,?,?)'''
    cursor.execute(sql,(image_url,page_id,caption,))
    conn.commit()

#TODO each route could reference a class 
#TODO routing itself should be it's own class
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
    displayed_MRs, actor_bios, base_name = getContent(baseID, base_is_actor, level)
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
            getDescSQL= "SELECT description FROM roles WHERE id=?"
            cursor.execute(getDescSQL,(editorID,))
            editor_description = cursor.fetchall()[0][0]
            historySql = '''INSERT INTO roles_history(id, name, description) VALUES (?,?,?) '''
            cursor.execute(historySql,(editorID, editorName, editor_description))
            changeDescSql='''UPDATE roles SET description=? WHERE id=?'''
            cursor.execute(changeDescSql,(new_description,editorID,))
        elif editorType == 'actor':
            getDescSQL= "SELECT bio FROM actors WHERE id=?"
            cursor.execute(getDescSQL,(editorID,))
            editor_description = cursor.fetchall()[0][0]
            historySql = '''INSERT INTO actors_history(id, name, description) VALUES (?,?,?) '''
            cursor.execute(historySql,(editorID, editorName, editor_description))
            changeDescSql='''UPDATE actors SET bio=? WHERE id=?'''
            cursor.execute(changeDescSql,(new_description,editorID,))
        elif editorType == 'mr':
            getDescSQL= "SELECT description FROM meta_roles WHERE id=?"
            cursor.execute(getDescSQL,(editorID,))
            editor_description = cursor.fetchall()[0][0]
            historySql = '''INSERT INTO meta_roles_history(id, name, description) VALUES (?,?,?) '''
            cursor.execute(historySql,(editorID, editorName, editor_description))
            changeDescSql='''UPDATE meta_roles SET description=? WHERE id=?'''
            cursor.execute(changeDescSql,(new_description,editorID,))
        else:
            pass
        conn.commit()
        return redirect(goBackUrl)
    else:
        editorID = request.args['editorID']
        editorType= request.args['editorType']
        goBackUrl = request.referrer
        name = request.args['name']
        history = get_history(editorID, editorType)
        if editorType == 'actor':
            getDescSQL= "SELECT bio FROM actors WHERE id=?"
            cursor.execute(getDescSQL,(editorID,))
        elif editorType == 'mr':
            getDescSQL= "SELECT description FROM meta_roles WHERE id=?"
            cursor.execute(getDescSQL,(editorID,))
        elif editorType == 'role':
            getDescSQL= "SELECT description FROM roles WHERE id=?"
            cursor.execute(getDescSQL,(editorID,))
        else:
            pass
        editor_description = cursor.fetchall()[0][0]

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
    connector_mrs = mrSearchResults(name_1)
    connector_mrs2 = mrSearchResults(name_2)

    return render_template('character_combiner.html', connector_mrs=connector_mrs, connector_mrs2=connector_mrs2, name_1=name_1, name_2=name_2)
    
@app.route('/character_connector/submit', methods = ['GET', 'POST'])
def submit():
    
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    mode = request.args.get('mode')

    if id1 != None and id2 != None:
        #TODO create a split function that makes two MR's with roles divided based on their id (maybe two lists of id's to check against?)
        if mode == "addMR":
            id1 = id1.split('|')[0] #0 is the role of id 1
            id2 = id2.split('|')[1] #the mr of id2
            try:
                int(id2)
            except ValueError:
                print (f'Invalid ID for opperation: {mode}')
            else:
                #code to run on sucessful try
                addMR(id1, id2)
        elif mode == "removeMR":
            id1 = id1.split('|')[0] #0 is the role of id 1
            removeMR(id1)
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
                    mergeMR(id1, id2)
        elif mode == "actorSwap":
            id1 = id1.split('|')[0] #0 is the role of id 1
            id2 = id2.split('|')[0] #0 is the role of id 2
            #Actor swaps are also first-come for ids.
            #Creating an actor_swap adds a swap ID to both roles
            actorSwap(id1, id2)
        elif mode == "removeActorSwap":
            id1 = id1.split('|')[0] #0 is the role of id 1
            removeActorSwap(id1)
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
    search_mrs, search_actors = searchBar(query)
    return render_template('search.html', search_mrs=search_mrs, search_actors=search_actors)