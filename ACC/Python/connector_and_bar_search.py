from meta_role_description import MetaRoleDescription
from meta_role import MetaRole
from actor_bio import ActorBio
from role import Role

class ConnectorAndBarSearch():
    def __init__(self, db_control):
        self._db_control = db_control

    def mrSearchResults(self, query):
        query = f'%{query}%'
        displayed_connector_mrs = []
        connector_class_roles = []
        connector_roles = self._db_control.select_like("*","roles","name",query)

        for role in connector_roles:
            connector_class_roles.append(Role(role[0],role[1],role[2],role[3],role[4],role[5]))
            for connector_role_class in connector_class_roles:
                connector_mr_exists = self.check_mr_exists_already(connector_role_class.parent_meta,displayed_connector_mrs)
                if connector_mr_exists:
                    self.append_role_to_mr(connector_role_class.name, displayed_connector_mrs, connector_role_class)
                else:
                    mrs = self._db_control.select("name, description", "meta_roles", "id", connector_role_class.parent_meta)
                    new_connector_mr = MetaRole([role], role[2], mrs[0], mrs[1])
                    displayed_connector_mrs.append(new_connector_mr)
        
        return displayed_connector_mrs

    def searchBarRemoveMRDuplicates(self, mr_list):  
        new_mr_list = []
        for mr in mr_list:
            exists_already = False
            for new_mr in new_mr_list:
                if mr.id == new_mr.id:
                    exists_already = True
            if exists_already == False:
                new_mr_list.append(mr)    
        return new_mr_list

    def searchBarRemoveActorDuplicates(self, actor_list):
        new_actor_list = []
        for actor in actor_list:
            exists_already = False
            for new_actor in new_actor_list:
                if actor.id == new_actor.id:
                    exists_already = True
            if exists_already ==False:
                new_actor_list.append(actor)
        return new_actor_list

    def searchBar(self, query):
        query = f'\'%{query}%\''
        displayed_search_mrs = []
        displayed_search_actors = []
        search_actors= []
        search_mrs = []

        search_actors_and_mrs = self._db_control.select_like("parent_actor, parent_meta","roles","name",query)
        
        for result in search_actors_and_mrs:
            search_actors.append(result[0])
            search_mrs.append(result[1])
        list(dict.fromkeys(search_actors))
        list(dict.fromkeys(search_mrs))
            
        for actor_id in search_actors:
            actor_names_bios = self._db_control.select("name, bio","actors","id",actor_id)
            for actor_name_bio in actor_names_bios:
                search_actor_name = actor_name_bio[0]
                search_actor_bio = actor_name_bio[1]
                new_search_actor = ActorBio(search_actor_bio,actor_id,search_actor_name, self._db_control)
                displayed_search_actors.append(new_search_actor)
        
        for mr_id in search_mrs:
            search_mr_names_descs = self._db_control.select("name, description","meta_roles", "id", mr_id)
            for search_mr_name_desc in search_mr_names_descs:
                search_mr_name = search_mr_name_desc[0]
                search_mr_desc = search_mr_name_desc[1]
                new_search_mr = MetaRoleDescription(search_mr_desc,mr_id,search_mr_name)
                displayed_search_mrs.append(new_search_mr)

        like_search_actors = self._db_control.select_like("bio, id, name", "actors", "name", query)
        for like_actor in like_search_actors:
            new_search_actor = ActorBio(like_actor[0], like_actor[1], like_actor[2])
            displayed_search_actors.append(new_search_actor)

        like_search_mrs = self._db_control.select_like("description, id, name","meta_roles","name", query)
        for like_mr in like_search_mrs:
            new_search_mr = MetaRoleDescription(like_mr[0], like_mr[1], like_mr[2])
            displayed_search_mrs.append(new_search_mr)

        
        displayed_search_mrs = self.searchBarRemoveMRDuplicates(displayed_search_mrs)
        displayed_search_actors = self.searchBarRemoveActorDuplicates(displayed_search_actors)

        return displayed_search_mrs, displayed_search_actors

    #TODO maybe make these into their own MR_handler class?
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
