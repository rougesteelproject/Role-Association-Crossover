from flask import Flask, render_template, request, redirect
app = Flask(__name__)

import distutils
import distutils.util

# create a database connection#
import sqlite3
database = r'C:/MAMP/db/sqllite/rac.db'

#create a connection to the db with address db_file
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except sqlite3.Error as e:
        print(e)

    return conn

conn = create_connection(database)
cursor = conn.cursor()

#slider #

#TODO each select returns a list of tuples. Check that the data is procesed at the right layer.
#for example, ID's are probably roles[x][0]

class MR_class:
    #class > tuple because it isn't fixed
    def __init__(self, roles, MR_class_id, name, description):
        self.roles = roles
        self.id = MR_class_id
        self.name = name
        self.description = description

def select_roles_where_parent_meta(parent_ID):
    sql = "SELECT * FROM roles WHERE parent_meta=?"
    cursor.execute(sql,(parent_ID,))
    roles = cursor.fetchall()
    roles_test = []
    for role in roles:
        roles_test.append(role_class(role[0], role[1], role[2], role[3], role[4], role[5]))
    return roles_test

def select_roles_where_parent_actor(parent_ID):
    sql = "SELECT * FROM roles WHERE parent_actor=?"
    cursor.execute(sql,(parent_ID,))
    roles = cursor.fetchall()
    roles_test = []
    for role in roles:
        roles_test.append(role_class(role[0], role[1], role[2], role[3], role[4], role[5]))
    return roles_test

class image_class:
    def __init__(self, file, caption):
        self.file = file
        self.caption = caption

class role_class:
    def __init__(self, role_id, role_name, role_description, parent_actor, parent_meta, actor_swap_id):
        self.id = role_id
        self.name = role_name
        self.description = role_description
        self.parent_actor = parent_actor
        self.parent_meta = parent_meta
        self.actor_swap_id = actor_swap_id
        self.gallery = self.get_Images(role_id)

    def get_Images(self, role_id):
        get_Images_Sql = "SELECT file, caption FROM gallery WHERE role=?"
        cursor.execute(get_Images_Sql,(role_id,))
        images = cursor.fetchall()
        gallery = []
        for image in images:
            gallery.append( image_class(image[0], image[1]))
        return gallery

class actor_bio_class:
    def __init__(self, actor_class_bio, actor__class_id, actor_name):
        self.bio = actor_class_bio
        self.id = actor__class_id
        self.name = actor_name
        self.gallery = self.get_Images(actor__class_id)
        
    def get_Images(self, actor__class_id):
        get_Images_Sql = "SELECT file, caption FROM gallery WHERE actor=?"
        cursor.execute(get_Images_Sql,(actor__class_id,))
        images = cursor.fetchall()
        gallery = []
        for image in images:
            gallery.append(image_class(image[0], image[1]))
        return gallery

class mr_desc_class:
    def __init__(self, mr_class_desc, mr_class_id, mr_name):
        self.bio = mr_class_desc
        self.id = mr_class_id
        self.name = mr_name

class actor_history_class:
    def __init__(self, name,description,timestamp):
        self.name=name
        self.description=description
        self.timestamp = timestamp

class role_history_class:
    def __init__(self, name, description, timestamp):
        self.name=name
        self.description=description
        self.timestamp = timestamp

class mr_history_class:
    def __init__(self, name, description, timestamp):
        self.name=name
        self.description=description
        self.timestamp = timestamp

def get_history(id, type):
    revision_list = []
    if type== 'actor':
        getHistorySql = "SELECT name, description, timestamp FROM actors_history WHERE id=?"
        history = cursor.execute(getHistorySql,(id,))
        for revision in history:
            revision_list.append(actor_history_class(revision[0], revision[1], revision[2]))
    elif type == 'role':
        getHistorySql = "SELECT name, description, timestamp FROM roles_history WHERE id=?"
        history = cursor.execute(getHistorySql,(id,))
        for revision in history:
            revision_list.append(role_history_class(revision[0], revision[1], revision[2]))
    elif type == 'mr':
        getHistorySql = "SELECT name, description, timestamp FROM meta_roles_history WHERE id=?"
        history = cursor.execute(getHistorySql,(id,))
        for revision in history:
            revision_list.append(role_history_class(revision[0], revision[1], revision[2]))
    
    return revision_list

def select_bios_where_actor_id(actor_id):
    getBioSql = "SELECT bio, name FROM actors WHERE id=?"
    #TODO probably will hve to expand this bio into multiple sections (Relationships, DOB, Photo, etc)
    cursor.execute(getBioSql,(actor_id,))
    generated_bio, actor_name = cursor.fetchone()
    actor_bio = actor_bio_class(generated_bio, int(actor_id), actor_name) 
     
    return actor_bio

def select_mrs_where_id(mr_id):
    sql = "SELECT name, description FROM meta_roles WHERE id=?"
    cursor.execute(sql,(mr_id,))
    mr = cursor.fetchall()
    
    return mr

def check_mr_exists_already(mr_id, mr_list):
    mr_exists_already = False
    for mr_class in mr_list:
        if mr_class.id == mr_id:
            mr_exists_already = True
    return mr_exists_already
    
def append_role_to_mr(mr_id, mr_list, role):
    id_to_match = mr_id
    for mr_class in mr_list:
        if mr_class.id == id_to_match:
            mr_contains_role = False
            for mr_role in mr_class.roles:
                if role.id== mr_role.id:
                    mr_contains_role = True
            if mr_contains_role == False:
                mr_class.roles.append(role)

def get_layer_roles_actor(inactive, actor_bios, layer_number, last_layer_string, displayed_MRs, new_displayed_MRs, new_inactive):
    for inactive_ID in inactive:
        #inactives are Actors, here
            roles = select_roles_where_parent_actor(inactive_ID)
            #get all the roles of each inactive (ie, partially represented) actor
            actor_bios.append(select_bios_where_actor_id(inactive_ID))
            for role in roles:
                exists_already_in_main = check_mr_exists_already(role.parent_meta, displayed_MRs)
                exists_already_in_new = check_mr_exists_already(role.parent_meta, new_displayed_MRs)
                role.name = f'{role.name} ({layer_number}{last_layer_string})'
                if exists_already_in_new == False and exists_already_in_main == False:
                    #IE, we don't have this mr, already, and aren't about to add it here in new_displayed
                    fetched_mr = select_mrs_where_id(role.parent_meta)[0]
                    new_MR = MR_class([role], role.parent_meta, fetched_mr[0], fetched_mr[1])
                    #creates an MR class in python from the mr that's the parent of each role
                    new_displayed_MRs.append(new_MR)
                elif exists_already_in_new:
                    append_role_to_mr(role.parent_meta, new_displayed_MRs, role)
                else:
                    append_role_to_mr(role.parent_meta, displayed_MRs, role)
                new_inactive.append(role.parent_meta)
                list(dict.fromkeys(new_inactive))
                #appending parent_meta id
            displayed_MRs.extend(new_displayed_MRs)
    return roles

def get_layer_roles_mr(inactive, displayed_MRs, layer_number, last_layer_string, new_inactive):
    #TODO add bios for roles with powers and relationships
    #make a table for fusion_parent or something for fusions, combiners, etc
    #Have them be a relationship like husband/wife
    for inactive_mr in inactive:
        new_roles = select_roles_where_parent_meta(inactive_mr)
        exists_already_in_main = check_mr_exists_already(inactive_mr, displayed_MRs)
        if exists_already_in_main == False:
            #IE, we don't have this mr, already, and aren't about to add it here in new_displayed
            fetched_mr = select_mrs_where_id(inactive_mr)[0]
            new_MR = MR_class(new_roles, inactive_mr, fetched_mr[0], fetched_mr[1])
            displayed_MRs.append(new_MR)
        else:
            for role in new_roles:
                append_role_to_mr(inactive_mr, displayed_MRs, role)
        for role in new_roles:
            role.name = f'{role.name} ({layer_number}{last_layer_string})'
            new_inactive.append(role.parent_actor)
            #appending the parent id
        return new_roles

def getLayerRoles(inactive, layer_is_actor, displayed_MRs, layer_number, level):
    new_displayed_MRs = []
    new_inactive = []
    actor_bios = []
    roles=[]
    if layer_number == level:
        last_layer_string = '*'
    else:
        last_layer_string = ''
    if layer_is_actor:
        roles = get_layer_roles_actor(inactive, actor_bios, layer_number, last_layer_string, displayed_MRs, new_displayed_MRs, new_inactive)
    else:
        roles = get_layer_roles_mr(inactive, displayed_MRs, layer_number, last_layer_string, new_inactive)
    actor_bios = removeBioDuplicates(actor_bios)
    new_inactive = list(dict.fromkeys(new_inactive))
    return roles, new_inactive, actor_bios

def removeBioDuplicates(actor_bios):
    new_bio_list = []
    for bio in actor_bios:
        exists_already = False
        for new_bio in new_bio_list:
            if bio.id == new_bio.id:
                exists_already = True
        if exists_already == False:
            new_bio_list.append(bio)
    return new_bio_list

def get_point_five(point_five_roles, level, displayed_MRs):
    #have point_five go through the meta from point_five_roles looking for ones with the same actor_swap_id
    point_five_sql = "SELECT * FROM roles WHERE parent_meta=? AND actor_swap_id=?"
    new_point_five = []
    #drop the ones that don't have point fives
    [new_point_five.append(role) for role in point_five_roles if role.actor_swap_id != 0]
    for role in new_point_five:
        cursor.execute(point_five_sql,(role.parent_meta,role.actor_swap_id,))
        fetched_point_five_roles = cursor.fetchall()
        #add them if we don't already have them
        fetched_role_class_es = []
        for fetched_role in fetched_point_five_roles:
            fetched_role_class_es.append(role_class(fetched_role[0], fetched_role[1], fetched_role[2], fetched_role[3], fetched_role[4],fetched_role[5]))
        for fetched_role_class in fetched_role_class_es:
            if fetched_role_class.id != role.id:
                fetched_role_class.name = f'{fetched_role_class.name} ({level}.5)'
                append_role_to_mr(role.parent_meta,displayed_MRs,fetched_role_class)

def getContent(baseID, base_is_actor, level = 1):
    layer_is_actor = base_is_actor #this way it changes each layer, but doesn't mess up the base site
    displayed_MRs = []
    inactive = [baseID] #these will be the next layer (Mrs or Actors who have only some children here)
    point_five_roles = [] #the last layer we added to the content, we're gonna search it for roles with actor-swap id's
    actor_bios = [] #The Bios of each actor that's displayed in full
    if base_is_actor:
        get_name_sql="SELECT name FROM actors WHERE id=?"
    else:
        get_name_sql="SELECT name FROM meta_roles WHERE id=?"
    cursor.execute(get_name_sql, (baseID,))
    base_name = cursor.fetchone()[0]
    point_five = False
    if (level*10 // 1 % 10) == 5:
    #if the last digit is five when you move the decimal
        point_five = True
        level -= 0.5
    level = int(level)
    layer = 0
    while layer < level:
        #on each layer, get more roles (roles with inactive as a parent)
        #on every layer, we override pint_five_roles with the list of new roles (the ones we'll append to the big roles list)
        point_five_roles, inactive, new_actor_bios = getLayerRoles(inactive,layer_is_actor, displayed_MRs, layer+1, level)
        actor_bios.extend(new_actor_bios)
        actor_bios = removeBioDuplicates(actor_bios)
        layer_is_actor = not layer_is_actor
        layer += 1
    if point_five and base_is_actor:
        get_point_five(point_five_roles, level, displayed_MRs)
    #TODO maybe a flag for characters who are fictional in-universe & a flag for historical or religious figures
    return displayed_MRs, actor_bios, base_name

#TODO we'l have to return the Hub Sigils (when we integrate into flask/ the graphviz)

#TODO more intuitive variable names, a sweep to make it pythonic
#   functions modify lists, so we don't neet to return them. 

# Create  MR table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT, is_biggest INT )''')
conn.commit()

#TODO replace some of these repeated sql (parent meta, for exapmple) with functions/methods

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

def cleanup():
    auto_generate()
    cursor.execute("SELECT MAX(id) FROM meta_roles")
    mr_id = cursor.fetchone()[0]
    for id in range(mr_id):
        orphanedMR(id)

#TODO replace some of the url variables and redirects to other pages with a 
# if request.method == 'POST':
#and get the values of the form

#create history table and pending changes
cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS roles_history(id TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS actors_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT)''')
conn.commit()

def add_image(page_type, page_id, image_url, caption):
    if page_type == 'actor':
        sql = '''INSERT INTO gallery (file, actor, caption) VALUES (?,?,?)'''
    else:
        sql = '''INSERT INTO gallery (file, role, caption) VALUES (?,?,?)'''
    cursor.execute(sql,(image_url,page_id,caption,))
    conn.commit()

@app.route('/')
def index():
    cleanup()
    #TODO generate features based off of hits or connections (after the webview/ hub sigils works)
    return render_template('index.html')

@app.route('/roles/', methods = ['GET', 'POST'])
def roles():
    cleanup()
    #?my_var=my_value
    level = float(request.args['level'])
    baseID = request.args['baseID']
    base_is_actor = bool(distutils.util.strtobool(request.args['base_is_actor']))
    displayed_MRs, actor_bios, base_name = getContent(baseID, base_is_actor, level)
    return render_template('actor_template.html', base_name=base_name, blurb_editor_link="", hub_sigils="", actor_bios = actor_bios, displayed_MRs = displayed_MRs, baseID=baseID, base_is_actor=base_is_actor, level=level)

@app.route('/roles/editor', methods = ['GET', 'POST'])
def editor():
    cleanup()
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
    cleanup()
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
    cleanup()
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
    cleanup()
    query = request.args['query']
    search_mrs, search_actors = searchBar(query)
    return render_template('search.html', search_mrs=search_mrs, search_actors=search_actors)