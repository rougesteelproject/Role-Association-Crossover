

class Search():
    def __init__(self, db_control):
        self._db_control = db_control
        self.displayed_mrs = []
        self.displayed_actors = []

    def mrSearchResults(self, query):
        query = f'%{query}%'

        connector_roles = self._db_control.get_roles_search(query)

        for role in connector_roles:
            connector_mr_exists = self.check_mr_exists_already(role,self.displayed_mrs)
            if not connector_mr_exists:
                new_connector_mr = self._db_control.get_mr(role.parent_meta)
                new_connector_mr.add_role(role)
                self.displayed_mrs.append(new_connector_mr)

        self.check_for_duplicates()


    def check_for_duplicates(self):
        seen_ids = []
        actors_no_duplicates = []
        mrs_no_duplicates = []
        
        for parent in self.displayed_actors:
            if parent.id not in seen_ids:
                seen_ids.append(parent.id)
                actors_no_duplicates.append(parent)
        self.displayed_actors = actors_no_duplicates

        for parent in self.displayed_mrs:
            if parent.id not in seen_ids:
                seen_ids.append(parent.id)
                mrs_no_duplicates.append(parent)
        self.displayed_mrs = mrs_no_duplicates

    def searchBar(self, query):
        query = f'\'%{query}%\''
        search_actor_ids= []
        search_mr_ids = []

        search_actors_and_mrs = self._db_control.select_like("parent_actor, parent_meta","roles","name",query)
        
        for result in search_actors_and_mrs:
            search_actor_ids.append(result[0])
            search_mr_ids.append(result[1])
        list(dict.fromkeys(search_actor_ids))
        list(dict.fromkeys(search_mr_ids))
            
        for actor_id in search_actor_ids:
            self.displayed_actors.append(self._db_control.get_actor(actor_id))
            
        
        for mr_id in search_mr_ids:
            self.displayed_mrs.append(self._db_control.get_mr(mr_id))

        like_search_actors = self._db_control.get_actors_search(query)
        self.displayed_actors.extend(like_search_actors)

        like_search_mrs = self._db_control.get_mrs_search(query)
        self.displayed_mrs.extend(like_search_mrs)

        self.check_for_duplicates()

    def check_mr_exists_already(self, role, mr_list):
        mr_exists_already = False
        for mr in mr_list:
            if role.parent_meta == mr.id:
                mr_exists_already = True
                mr.add_role(role)
        return mr_exists_already