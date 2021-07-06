import Role as role_class
import ActorHistory as actor_history_class
import RoleHistory as role_history_class

class Slider:
    def __init__(self, db_control):
        self._db_control = db_control
    
    #TODO each select returns a list of tuples. Check that the data is procesed at the right layer.
    #for example, ID's are probably roles[x][0]

    def select_roles_where_parent_meta(self, parent_meta_ID):
        roles = self._db_control.select("*", "roles", "parent_meta", parent_meta_ID)
        roles_test = []
        for role in roles:
            roles_test.append(role_class(role[0], role[1], role[2], role[3], role[4], role[5]))
        return roles_test

    def select_roles_where_parent_actor(self, parent_actor_ID):
        roles = self._db_control.select("*", "roles", "parent_actor", parent_actor_ID)
        roles_test = []
        for role in roles:
            roles_test.append(role_class(role[0], role[1], role[2], role[3], role[4], role[5]))
        return roles_test

    #TODO replace sql
    def get_history(self, id, type):
        revision_list = []
        if type== 'actor':
            history = self._db_control.select("name, description, timestamp", "actors_history", "id", id)
            for revision in history:
                revision_list.append(actor_history_class(revision[0], revision[1], revision[2]))
        elif type == 'role':
            history = self._db_control.select("name, description, timestamp", "roles", "id", id)
            for revision in history:
                revision_list.append(role_history_class(revision[0], revision[1], revision[2]))
        elif type == 'mr':
            getHistorySql = "SELECT name, description, timestamp FROM meta_roles_history WHERE id=?"
            history = cursor.execute(getHistorySql,(id,))
            history = self._db_control.select("name, description, timestamp", )
            for revision in history:
                revision_list.append(role_history_class(revision[0], revision[1], revision[2]))
        
        return revision_list

    #TODO replace sql
    def select_bios_where_actor_id(actor_id):
        getBioSql = "SELECT bio, name FROM actors WHERE id=?"
        #TODO probably will hve to expand this bio into multiple sections (Relationships, DOB, Photo, etc)
        cursor.execute(getBioSql,(actor_id,))
        generated_bio, actor_name = cursor.fetchone()
        actor_bio = actor_bio_class(generated_bio, int(actor_id), actor_name) 
        
        return actor_bio

    #TODO replace sql
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

    #TODO maybe create a page generator class?
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

    #TODO replace sql
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

    #TODO move to a class?
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