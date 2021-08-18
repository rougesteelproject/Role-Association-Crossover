from role import Role
from actor_history import ActorHistory
from role_history import RoleHistory
from meta_role_history import MetaRoleHistory
from actor_bio import ActorBio
from meta_role import MetaRole

class WikiPageGenerator:
    def __init__(self, db_control):
        self._db_control = db_control
    
    #TODO each select returns a list of tuples. Check that the data is procesed at the right layer.
    #for example, ID's are probably roles[x][0]

    def select_roles_where_parent_meta(self, parent_meta_ID):
        roles = self._db_control.select("*", "roles", "parent_meta", parent_meta_ID)
        roles_test = []
        for role in roles:
            roles_test.append(Role(*role,self._db_control))
        return roles_test

    def select_roles_where_parent_actor(self, parent_actor_ID):
        roles = self._db_control.select("*", "roles", "parent_actor", parent_actor_ID)
        roles_test = []
        for role in roles:
            roles_test.append(Role(*role, self._db_control))
        return roles_test

    def get_history(self, id, type):
        revision_list = []
        if type== 'actor':
            history = self._db_control.select("name, description, timestamp", "actors_history", "id", id)
            for revision in history:
                revision_list.append(ActorHistory(*revision))
        elif type == 'role':
            history = self._db_control.select("name, description, alive_or_dead, alignment, timestamp", "roles", "id", id)
            for revision in history:
                revision_list.append(RoleHistory(*revision))
        elif type == 'mr':
            history = self._db_control.select("name, description, timestamp", "meta_roles_history", "id", id)
            for revision in history:
                revision_list.append(MetaRoleHistory(*revision))
        
        return revision_list

    def select_bios_where_actor_id(self, actor_id):
        #TODO probably will hve to expand this bio into multiple sections (Relationships, DOB, Photo, etc)
        results = self._db_control.select("bio, name", "actors", "id", actor_id)
        generated_bio, actor_name = results[0]
        actor_bio = ActorBio(generated_bio, actor_id, actor_name, self._db_control) 
        return actor_bio

    def select_mrs_where_id(self, mr_id):
        mr = self._db_control.select("name,description", "meta_roles", "id", mr_id)
        return mr

    def check_mr_exists_already(self, mr_id, mr_list):
        mr_exists_already = False
        for mr_class in mr_list:
            if mr_class.id == mr_id:
                mr_exists_already = True
        return mr_exists_already
        
    def append_role_to_mr(self, mr_id, mr_list, role):
        id_to_match = mr_id
        for mr_class in mr_list:
            if mr_class.id == id_to_match:
                mr_contains_role = False
                for mr_role in mr_class.roles:
                    if role.id== mr_role.id:
                        mr_contains_role = True
                if mr_contains_role == False:
                    mr_class.roles.append(role)

    def get_layer_roles_actor(self, inactive, actor_bios, layer_number, last_layer_string, displayed_MRs, new_displayed_MRs, new_inactive):
        for inactive_ID in inactive:
            #inactives are Actors, here
                roles = self.select_roles_where_parent_actor(inactive_ID)
                #get all the roles of each inactive (ie, partially represented) actor
                actor_bios.append(self.select_bios_where_actor_id(inactive_ID))
                for role in roles:
                    exists_already_in_main = self.check_mr_exists_already(role.parent_meta, displayed_MRs)
                    exists_already_in_new = self.check_mr_exists_already(role.parent_meta, new_displayed_MRs)
                    role.name = f'{role.name} ({layer_number}{last_layer_string})'
                    if exists_already_in_new == False and exists_already_in_main == False:
                        #IE, we don't have this mr, already, and aren't about to add it here in new_displayed
                        fetched_mr = self.select_mrs_where_id(role.parent_meta)[0]
                        new_MR = MetaRole([role], role.parent_meta, fetched_mr[0], fetched_mr[1])
                        #creates an MR class in python from the mr that's the parent of each role
                        new_displayed_MRs.append(new_MR)
                    elif exists_already_in_new:
                        self.append_role_to_mr(role.parent_meta, new_displayed_MRs, role)
                    else:
                        self.append_role_to_mr(role.parent_meta, displayed_MRs, role)
                    new_inactive.append(role.parent_meta)
                    list(dict.fromkeys(new_inactive))
                    #appending parent_meta id
                displayed_MRs.extend(new_displayed_MRs)
        return roles

    def get_layer_roles_mr(self,inactive, displayed_MRs, layer_number, last_layer_string, new_inactive):
        for inactive_mr in inactive:
            new_roles = self.select_roles_where_parent_meta(inactive_mr)
            exists_already_in_main = self.check_mr_exists_already(inactive_mr, displayed_MRs)
            if exists_already_in_main == False:
                #IE, we don't have this mr, already, and aren't about to add it here in new_displayed
                fetched_mr = self.select_mrs_where_id(inactive_mr)[0]
                new_MR = MetaRole(new_roles, inactive_mr, fetched_mr[0], fetched_mr[1])
                displayed_MRs.append(new_MR)
            else:
                for role in new_roles:
                    self.append_role_to_mr(inactive_mr, displayed_MRs, role)
            for role in new_roles:
                role.name = f'{role.name} ({layer_number}{last_layer_string})'
                new_inactive.append(role.parent_actor)
                #appending the parent id
            return new_roles

    def getLayerRoles(self,inactive, layer_is_actor, displayed_MRs, layer_number, level):
        new_displayed_MRs = []
        new_inactive = []
        actor_bios = []
        roles=[]
        if layer_number == level:
            last_layer_string = '*'
        else:
            last_layer_string = ''
        if layer_is_actor:
            roles = self.get_layer_roles_actor(inactive, actor_bios, layer_number, last_layer_string, displayed_MRs, new_displayed_MRs, new_inactive)
        else:
            roles = self.get_layer_roles_mr(inactive, displayed_MRs, layer_number, last_layer_string, new_inactive)
        actor_bios = self.removeBioDuplicates(actor_bios)
        new_inactive = list(dict.fromkeys(new_inactive))
        return roles, new_inactive, actor_bios

    #TODO actor bios need redone. They can be part of the actor class, I think, so we don't need a seperate class for just descriptions
    #instead, get actor.bio actor.relationships, etc, for actor in displayed_actors
    #only bios are handled how they are right now
    def removeBioDuplicates(self, actor_bios):
        new_bio_list = []
        for bio in actor_bios:
            exists_already = False
            for new_bio in new_bio_list:
                if bio.id == new_bio.id:
                    exists_already = True
            if exists_already == False:
                new_bio_list.append(bio)
        return new_bio_list

    def get_point_five(self, point_five_roles, level, displayed_MRs):
        #have point_five go through the meta from point_five_roles looking for ones with the same actor_swap_id
        point_five_sql = "SELECT * FROM roles WHERE parent_meta=? AND actor_swap_id=?"
        new_point_five = []
        #drop the ones that don't have point fives
        [new_point_five.append(role) for role in point_five_roles if role.actor_swap_id != 0]
        for role in new_point_five:
            fetched_point_five_roles = self._db_control.select("*", "roles","parent_meta", role.parent_meta, bool_and = True, second_argument_column = "actor_swap_id", second_argument_value = role.actor_swap_id)
            #add them if we don't already have them
            fetched_role_class_es = []
            for fetched_role in fetched_point_five_roles:
                fetched_role_class_es.append(Role(fetched_role[0], fetched_role[1], fetched_role[2], fetched_role[3], fetched_role[4],fetched_role[5],self._db_control))
            for fetched_role_class in fetched_role_class_es:
                if fetched_role_class.id != role.id:
                    fetched_role_class.name = f'{fetched_role_class.name} ({level}.5)'
                    self.append_role_to_mr(role.parent_meta,displayed_MRs,fetched_role_class)

    #TODO move to a class?
    def getContent(self, baseID, base_is_actor, level = 1):
        layer_is_actor = base_is_actor #this way it changes each layer, but doesn't mess up the base site
        displayed_MRs = []
        inactive = [baseID] #these will be the next layer (Mrs or Actors who have only some children here)
        point_five_roles = [] #the last layer we added to the content, we're gonna search it for roles with actor-swap id's
        actor_bios = [] #The Bios of each actor that's displayed in full
        if base_is_actor:
            base_name = self._db_control.select("name","actors","id",baseID)[0][0]
        else:
            base_name = self._db_control.select("name","meta_roles","id",baseID)[0][0]
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
            point_five_roles, inactive, new_actor_bios = self.getLayerRoles(inactive,layer_is_actor, displayed_MRs, layer+1, level)
            actor_bios.extend(new_actor_bios)
            actor_bios = self.removeBioDuplicates(actor_bios)
            layer_is_actor = not layer_is_actor
            layer += 1
        if point_five and base_is_actor:
            self.get_point_five(point_five_roles, level, displayed_MRs)
        #TODO maybe a flag for characters who are fictional in-universe & a flag for historical or religious figures
        return displayed_MRs, actor_bios, base_name

        #TODO get and return displayed_actors so we can filter people form relationships if that person is already here

    #TODO we'l have to return the Hub Sigils (when we integrate into flask/ the graphviz)