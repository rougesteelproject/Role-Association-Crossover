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

#TODO a hsitory in each role of it's prior Mr's name, including an option to revert the whole change. Changes have change Id's. 
# You can revert an mr change by ID without changing the ID's
#TODO mr id's need to ascend without replacement.

#TODO replace some of these repeated sql (parent meta, for exapmple) with functions/methods

#TODO merging MRS doesn't work how I expect
def orphanedMR(meta_id):
    #delete MR from the db if they have no children
    sql = "SELECT id FROM roles WHERE parent_meta=?"
    cursor.execute(sql, (meta_id,))
    orphans = cursor.fetchall()
    if len(orphans) == 0:
        sql = "DELETE FROM meta_roles WHERE id=? "
        cursor.execute(sql, (meta_id,))
        conn.commit()

def addMR(role_id, mr_id):
    #changes the meta of role_id to mr_id, then checks the old one to see if it has no children
    get_orphan_mr = "SELECT parent_meta FROM roles WHERE id=?"
    cursor.execute(get_orphan_mr, (role_id,))
    orphan_mr = cursor.fetchall()[0]

    sql = "UPDATE roles SET parent_meta=? WHERE id=?"
    cursor.execute(sql, (mr_id, role_id,))
    conn.commit()
    orphan_mr=orphan_mr[0]
    print(orphan_mr)
    orphanedMR(orphan_mr)

def auto_generate():
    # get one role with an mr of 0 #get just the name and id
    sql = "SELECT name, id FROM roles WHERE parent_meta=0"
    cursor.execute(sql)
    names_and_ids = cursor.fetchall()
    for role in names_and_ids:
        role_name = role[0].split("(")[0]
        role_id = role[1]

        #create an auto mr with that name

        cursor.execute("SELECT MAX(id) FROM meta_roles")
        mr_id = cursor.fetchone()[0]
        if mr_id is not None:
            mr_id += 1
        else:
            mr_id = 1
        #Select Max() gets the highest in that column

        #set he mr to the auto where the role id is the role id we got before
        sql = '''INSERT OR IGNORE INTO meta_roles(id, name, description, is_biggest) VALUES (?,?,?,?) '''
        cursor.execute(sql,(mr_id, role_name, 'auto-generated', 0,))
        conn.commit()
        addMR(role_id, mr_id)

def removeMR(id1):
    #remove mr from a role
    get_parent_meta = "SELECT parent_meta FROM roles WHERE id=?"
    cursor.execute(get_parent_meta, (id1,))
    meta_id = cursor.fetchall()
    #print (meta_id)
    sql = "UPDATE roles SET parent_meta=0 WHERE id=?"
    cursor.execute(sql, (id1,))
    conn.commit()
    orphanedMR(meta_id)
    auto_generate()
    
def mergeMR(id1, id2):
    if (id1 != id2):
        lowest = min(id1, id2)
        highest = max(id1, id2)
        
        sql = "UPDATE roles SET parent_meta=? WHERE parent_meta=?"
        cursor.execute(sql, (lowest, highest))
        orphanedMR(highest)

def actorSwap(id1, id2):
    get_parent_meta = "SELECT parent_meta FROM roles WHERE id=?"
    cursor.execute(get_parent_meta, (id1,))
    parent_meta_1 = cursor.fetchall()[0][0]
    cursor.execute(get_parent_meta, (id2,))
    parent_meta_2 = cursor.fetchall()[0][0]
     
    if parent_meta_1 != parent_meta_2:
        mergeMR(parent_meta_1, parent_meta_2)
    
    sql = "SELECT parent_meta FROM roles WHERE id=?"
    cursor.execute(sql, (id1,))
    parent_meta = cursor.fetchone()[0]
    sql = "SELECT MAX(actor_swap_id) FROM roles WHERE parent_meta=?"
    cursor.execute(sql, (parent_meta,))
    swap_id = cursor.fetchone()[0]
    if swap_id is not None:
        swap_id += 1
    else:
        swap_id = 1
    #Select Max() gets the highest in that column
    sql = "UPDATE roles SET actor_swap_id=? WHERE id=? OR id =?"
    cursor.execute(sql, (swap_id, id1, id2))
    conn.commit()
    
def removeActorSwap(id1):
    sql = "SELECT actor_swap_id, parent_meta FROM roles WHERE id=?"
    cursor.execute(sql, (id1,))
    actor_swap_data = cursor.fetchall()[0]
    as_id = actor_swap_data[0]
    as_parent = actor_swap_data[1]
    
    #get the id  so we can check if we orphaned an actor-swap
    
    sql = "UPDATE roles SET actor_swap_id=0 WHERE id=?"
    cursor.execute(sql, (id1,))
    conn.commit()
    
    #we don't need to redo the actor-swap ids if a number is skipped
    
    #This will set any orphaned (one-child) actor_swaps to 0
    if as_id != 0:
        sql = "SELECT id FROM roles WHERE actor_swap_id=? AND parent_meta=?"
        cursor.execute(sql, (as_id, as_parent))
        result = cursor.fetchall()
        if len(result) < 2 and len(result) != 0:
            clear_id = result[0][0]
            sql = "UPDATE roles SET actor_swap_id=0 WHERE id=?"
            cursor.execute(sql, (clear_id,))
            conn.commit()