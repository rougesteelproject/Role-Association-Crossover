#TODO a hsitory in each role of it's prior Mr's name, including an option to revert the whole change. Changes have change Id's. 
# You can revert an mr change by ID without changing the ID's

#TODO replace some of these repeated sql (parent meta, for exapmple) with functions/methods

def changeMR(role_id, mr_id):
    #changes the meta of role_id to mr_id, then checks the old one to see if it has no children
    mr_id = str(mr_id)
    sql = "UPDATE roles SET parent_meta=? WHERE id=?"
    cursor.execute(sql, (mr_id, role_id,))
    conn.commit()

def resetMR(roleID1):
    sql = "UPDATE roles SET parent_meta=first_parent_meta WHERE id=?"
    cursor.execute(sql, (roleID1,))
    conn.commit()

    
def mergeMR(metaID1, metaID2):
    metaID1 = str(metaID1)
    metaID2 = str(metaID2)
    if (metaID1 != metaID2):
        lowest = min(metaID1, metaID2)
        highest = max(metaID1, metaID2)
        sql = "UPDATE roles SET parent_meta=? WHERE parent_meta=?"
        cursor.execute(sql, (highest,lowest))

def actorSwap(roleID1, roleID2):
    if roleID1 != roleID2:
        get_parent_meta = "SELECT parent_meta FROM roles WHERE id=?"
        cursor.execute(get_parent_meta, (roleID1,))
        parent_meta_1 = cursor.fetchall()[0][0]
        cursor.execute(get_parent_meta, (roleID2,))
        parent_meta_2 = cursor.fetchall()[0][0]
        
        if parent_meta_1 != parent_meta_2:
            mergeMR(parent_meta_1, parent_meta_2)
        
        sql = "SELECT parent_meta FROM roles WHERE id=?"
        cursor.execute(sql, (roleID1,))
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
        cursor.execute(sql, (swap_id, roleID1, roleID2))
        conn.commit()
    else:
        print("Actor Swap Error: IDs are the same.")
    
def removeActorSwap(roleID1):
    sql = "SELECT actor_swap_id, parent_meta FROM roles WHERE id=?"
    cursor.execute(sql, (roleID1,))
    actor_swap_data = cursor.fetchall()[0]
    actor_swap_id = actor_swap_data[0]
    actor_swap_parent = actor_swap_data[1]
    
    #get the id  so we can check if we orphaned an actor-swap
    
    sql = "UPDATE roles SET actor_swap_id=0 WHERE id=?"
    cursor.execute(sql, (roleID1,))
    conn.commit()
    
    #we don't need to redo the actor-swap ids if a number is skipped
    
    #This will set any orphaned (one-child) actor_swaps to 0
    if actor_swap_id != 0:
        sql = "SELECT id FROM roles WHERE actor_swap_id=? AND parent_meta=?"
        cursor.execute(sql, (actor_swap_id, actor_swap_parent))
        result = cursor.fetchall()
        if len(result) < 2 and len(result) != 0:
            swap_id_to_clear = result[0][0]
            sql = "UPDATE roles SET actor_swap_id=0 WHERE id=?"
            cursor.execute(sql, (swap_id_to_clear,))
            conn.commit()