from meta_role_description import MetaRoleDescription
from meta_role import MetaRole
from actor import Actor

class ConnectorAndBarSearch():
    def __init__(self, db_control):
        self._db_control = db_control

    def mrSearchResults(self, query):
        query = f'%{query}%'
        displayed_connector_mrs = []

        connector_roles = self._db_control.get_roles_search(query)

        for role in connector_roles:
            connector_mr_exists = self.check_mr_exists_already(role,displayed_connector_mrs)
            if not connector_mr_exists:
                new_connector_mr = self._db_control.get_mr(role.parent_meta)
                new_connector_mr.add_role(role)
                displayed_connector_mrs.append(new_connector_mr)
        
        return displayed_connector_mrs

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
            displayed_search_actors.append(Actor(self._db_control.get_actor(actor_id)))
            
        
        for mr_id in search_mrs:
            displayed_search_mrs.append(MetaRole(self._db_control.get_mr(mr_id)))

        like_search_actors = self._db_control.get_actors_search(query)
        displayed_search_actors.extend(like_search_actors)
        #TODO maybe we need to check here for duplicates

        like_search_mrs = self._db_control.get_mrs_search(query)
        displayed_search_mrs.extend(like_search_mrs)

        return displayed_search_mrs, displayed_search_actors

    def check_mr_exists_already(self, role, mr_list):
        mr_exists_already = False
        for mr in mr_list:
            if role.parent_meta == mr.id:
                mr_exists_already = True
                mr.add_role(role)
        return mr_exists_already