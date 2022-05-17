from classes.nodes.actor import Actor
from classes.nodes.meta_role import MetaRole
from classes.nodes.role import Role

from classes.histories.meta_role_history import MetaRoleHistory
from classes.histories.actor_history import ActorHistory
from classes.histories.role_history import RoleHistory
from classes.histories.ability_history import AbilityHistory

from classes.nodes.ability import Ability

from classes.nodes.ability_template import AbilityTemplate
from classes.histories.template_history import TemplateHistory

from classes.nodes.actor_relationship import ActorRelationship
from classes.nodes.role_relationship import RoleRelationship

from classes.nodes.image import Image

#TODO replace some text with varChar

#TODO a way to remove porn actors, because the 'no adult films' bit doesn't work.

class DatabaseController():
    def __init__(self, database_uri):

        self.requests = []
        self._database_uri = database_uri
        self.connection = self._create_connection() 
        self._create_db_if_not_exists
        #Sublcalsses will use their owwn versions

        #TODO use 'with' more often

    def _create_connection(self):
        pass

    def execute(self, command, parameters):
        pass

    def commit(self):
        pass

    #TODO each select returns a list of tuples. Check that the data is procesed at the right layer.

    def _create_db_if_not_exists(self):
        pass

    #CREATE#
    def create_actor(self, id, name, bio, birth_date, death_date):
        pass

    def create_role(self,role_id, role_name, actor_id, mr_id):
        pass

    def create_mr(self, character_name, mr_id):
        pass
    
    #UPDATE#
    def update(self, table_name, column, column_value, where, where_value):
        pass

    def update_or(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        pass
    
    def update_and(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        pass

    def update_reset_mr(self, roleID1):
        pass

    #SELECT#
    def select_where(self, select_columns, table_name, where, where_value):
        pass

    def select(self, select_columns, table_name):
        pass

    def select_and(self, select_columns, table_name, where_column, where_value, where_column_2, where_value_2):
        pass

    def select_or(self, select_columns, table_name, where_column, where_value, where_column_2, where_value_2):
        pass

    def select_max_where(self, select_column, table_name, where_column, where_value):
        pass

    def select_like(self, select_columns, table_name, where_column, like_value):
        pass

    def select_not_in(self, select_columns, table_name, where, ability_list):
        pass

    #IMAGES#
    def add_image(self,page_type, page_id, image_url, caption):
       pass

    def get_images_actor(self, actor_id):
        #LEAVE UN-PASSED
        fetched_images = self.select_where("file, caption", "gallery", "actor", actor_id)
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    def get_images_role(self, role_id):
        #LEAVE UN-PASSED
        fetched_images = self.select_where("file, caption", "gallery", "role", role_id)
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    #GET#
    #TODO may search in bios or descriptions?

    def get_actor(self, actor_id):
        #TODO callback to get an actor that's not already in the db (send an error: no such actor in db, then try imdbImp, then imdbImp will give an error if no such person)
        if actor_id != '':
            fetched_actor = self.select_where("*","actors","id",actor_id)[0]
            actor = Actor(*fetched_actor, self)
            return actor
        else:
            print('get_actor error: there was no base_id')

    def get_actors_search(self, query):
        actors = []
        fetched_actors = self.select_like("*","actors","name", query)
        for actor in fetched_actors:
            actors.append(Actor(*actor, self))
        return actors

    def get_all_actors(self):
        all_actors_fetched = self.select("*", "actors")
        all_actors = []
        for actor in all_actors_fetched:
            all_actors.append(Actor(*actor, self))
        return all_actors

    def get_mr(self, mr_id):
        fetched_mr = self.select_where("*","meta_roles", "id",mr_id)[0]
        return MetaRole(*fetched_mr, self)

    def get_mrs_search(self,query):
        mrs = []
        fetched_mrs = self.select_like("*","meta_roles","name",query)
        for mr in fetched_mrs:
            new_mr = MetaRole(*mr, self)
            new_mr.get_roles()
            if new_mr.roles != []:
                mrs.append(new_mr)
            
        return mrs

    def get_role(self, role_id):
        fetched_role = self.select_where("*","roles","id",role_id)
        if len(fetched_role) != 0:
            return Role(*fetched_role[0], self)
        else:
            print(f'No such role: {role_id}')

    def get_roles(self, parent_id, is_actor):
        roles = []
        if is_actor:
            fetched_roles = self.select_where("*", "roles", "parent_actor", parent_id)
        else:
            fetched_roles = self.select_where("*","roles","parent_meta",parent_id)
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles

    def get_all_roles(self):
        all_roles_fetched = self.select("*", "roles")
        all_roles = []
        for role in all_roles_fetched:
            all_roles.append(Role(*role, self))
        return all_roles

    def get_roles_search(self, query):
        roles = []
        fetched_roles = self.select_like("*","roles","name",query)
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles
        
    def get_roles_swap(self, mr_id, actor_swap_id):
        roles = []
        fetched_roles = self.select_and("*","roles","parent_meta",mr_id, "actor_swap_id", actor_swap_id)
        for role in fetched_roles:
            roles.append(Role(*role,self))
        return roles

    def get_parent_meta(self, role_id):
        parent_meta = self.select_where("parent_meta", "roles", "id", role_id)[0][0]
        return parent_meta

    def search_char_connector(self, query1, query2):
        connector_mrs_1 = self.get_mrs_search(query1)
        connector_mrs_2 = self.get_mrs_search(query2)

        roles_1 = self.get_roles_search(query1)
        roles_2 = self.get_roles_search(query2)

        for role in roles_1:
            mr_in_list = False
            for mr in connector_mrs_1:
                if mr.id == role.parent_meta:
                    mr_in_list= True

            if not mr_in_list:
                new_mr = self.get_mr(role.parent_meta)
                new_mr.get_roles()
                if new_mr.roles != []:
                    connector_mrs_1.append(new_mr)

        for role in roles_2:
            mr_in_list = False
            for mr in connector_mrs_2:
                if mr.id == role.parent_meta:
                    mr_in_list= True

            if not mr_in_list:
                new_mr = self.get_mr(role.parent_meta)
                new_mr.get_roles()
                if new_mr.roles != []:
                    connector_mrs_2.append(new_mr)

        if query1 != query2:
            id_list = [mr.id for mr in connector_mrs_1]
            connector_mrs_2 = [mr for mr in connector_mrs_2 if mr.id not in id_list]

        return connector_mrs_1, connector_mrs_2

    def search_bar(self, query):
        search_bar_actors  = self.get_actors_search(query)
        search_bar_mrs = self.get_mrs_search(query)

        roles = self.get_roles_search(query)

        for role in roles:
            in_mrs = False
            for mr in search_bar_mrs:
                if role.parent_meta == mr.id:
                    in_mrs = True

            if not in_mrs:
                search_bar_mrs.append(self.get_mr(role.parent_meta))

        return search_bar_actors, search_bar_mrs
   
    #HISTORY#
    def get_actor_history(self,id):
        revision_list = []
        history = self.select_where("*", "actors_history", "id", id)
        for revision in history:
            revision_list.append(ActorHistory(*revision))
        return revision_list

    def get_mr_history(self, id):
        revision_list = []
        history = self.select_where("*", "meta_roles_history", "id", id)
        for revision in history:
            revision_list.append(MetaRoleHistory(*revision))
        return revision_list

    def get_role_history(self,id):
        revision_list = []
        history = self.select_where("*", "roles_history", "id", id)
        for revision in history:
            revision_list.append(RoleHistory(*revision))
        return revision_list

    def create_actor_history(self, id, new_bio):
        pass

    def create_mr_history(self, id, new_description, historical, religious, fictional_in_universe):
        pass

    def create_role_history(self, id, new_description, new_alive_or_dead, new_alignment):
        pass

    #CHARACTER CONNECTOR#
    def character_connector_switch(self, mode, id1, id2):
        if id1 != None and id2 != None:
            role_id_1, mr_id_1 = id1.split('|')
            role_id_2, mr_id_2 = id2.split('|')

            if mode == "changeMR":
                self.changeMR(role_id_1, mr_id_2)
            elif mode == "resetMR":
                self.resetMR(role_id_1)
            elif mode == "mergeMR":
                self.mergeMR(mr_id_1,mr_id_2)
            elif mode == "actorSwap":
                self.actorSwap(role_id_1,role_id_2, mr_id_1, mr_id_2)
            elif mode == "removeActorSwap":
                self.removeActorSwap(role_id_1)
            else:
                print(f'Opperation \'{mode}\' does not exist.')

            self.commit()
    #TODO create a splitter function that makes two MR's with roles divided based on their id (maybe two lists of id's to check against?)

    #TODO a hsitory in each role of it's prior Mr's name, including an option to revert the whole change. Changes have change Id's. 
    # You can revert an mr change by ID without changing the ID's
    def changeMR(self, role_id, mr_id):
        #changes the meta of role_id to mr_id
        self.update("roles", "parent_meta", mr_id, "id", role_id)

    def resetMR(self, roleID1):
        self.update_reset_mr(roleID1)

    def mergeMR(self, metaID1, metaID2):
        if (metaID1 != metaID2):
            lowest = min(metaID1, metaID2)
            highest = max(metaID1, metaID2)
            self.update("roles", "parent_meta", highest, "parent_meta", lowest)

    def actorSwap(self, roleID1, roleID2, mr_id_1, mr_id_2):
        if roleID1 != roleID2:

            if mr_id_1 != mr_id_2:
                self.mergeMR(mr_id_1, mr_id_2)
            
            parent_meta = max(mr_id_1,mr_id_2)
            
            #TODO actor_swap may be a relationship in neo
            
            swap_id_1 = self.select_where("actor_swap_id", "roles", "id", roleID1)[0][0]
            swap_id_2 = self.select_where("actor_swap_id", "roles", "id", roleID2)[0][0]
            if swap_id_1 == 0 and swap_id_2 == 0:
                swap_id = self.select_max_where("actor_swap_id", "roles","parent_meta", parent_meta)[0]
                if swap_id is not None:
                    swap_id += 1
                else:
                    swap_id = 1
                #Select Max() gets the highest in that column
                #If both are zero, set both to the new one we generate
                self.update_or("roles", "actor_swap_id", swap_id, "id", roleID1, where_2="id", where_value_2=roleID2)
            else:
                swap_id = max(swap_id_1, swap_id_2)
                min_swap_id = min(swap_id_1, swap_id_2)
                if min_swap_id == 0:
                    #if just one is zero, we set both to the max (because min would get us zero)
                    self.update_or("roles", "actor_swap_id", swap_id, "id", roleID1, where_2="id", where_value_2=roleID2)
                else:
                    #change all the ones with the same actor_swap as the new addition
                    self.update_and("roles", "actor_swap_id", swap_id, "actor_swap_id", min_swap_id, "parent_meta", parent_meta)
            
        else:
            print("Actor Swap Error: IDs are the same.")
        
    def removeActorSwap(self, roleID1, parent_id_1):
        actor_swap_data = self.select_where("actor_swap_id, parent_meta", "roles", "id", roleID1)
        actor_swap_id = actor_swap_data[0]
        
        #get the id  so we can check if we orphaned an actor-swap
        
        self.update("roles", "actor_swap_id", 0, "id", roleID1)
        
        #we don't need to redo the actor-swap ids if a number is skipped
        
        #This will set any orphaned (one-child) actor_swaps to 0
        if actor_swap_id != 0:
            result = self.select_and("id","roles","actor_swap_id",actor_swap_id, "parent_meta", parent_id_1)
            if len(result) < 2 and len(result) != 0:
                swap_id_to_clear = result[0][0]
                self.update("roles","actor_swap_id", 0, "id", swap_id_to_clear)

    #ABILITIES#
    def create_ability(self, name, description):
        pass

    def create_ability_history(self, id, name, description):
        pass

    def remove_ability_actor(self, actor_id, ability_list):
        pass

    def remove_ability_role(self, role_id, ability_list):
        pass

    def add_ability_actor(self, actor_id, ability_list):
        pass

    def add_ability_role(self, role_id, ability_list):
        pass

    def get_ability(self, ability_id):
        fetched_ability = self.select_where("*","abilities","id",ability_id)
        if len(fetched_ability) == 1:
            ability = fetched_ability[0]
            return Ability(*ability)

    def get_ability_list_role(self, role_id):
        ability_ids = self.select_where("ability_id", "roles_to_abilities", "role_id", role_id)
        abilities = []
        if len(ability_ids) >= 1:
            for id_tuple in ability_ids:
                abilities.append(self.get_ability(id_tuple[0]))
        return abilities

    def get_ability_list_actor(self, actor_id):
        ability_ids = self.select_where("ability_id", "actors_to_abilities", "actor_id", actor_id)
        abilities = []
        if len(ability_ids) == 1:
            for id in ability_ids[0]:
                abilities.append(self.get_ability(id))
        return abilities

    def get_ability_list_exclude_actor(self, actor_id):
        ability_ids = self.select_where("ability_id", "actors_to_abilities", "actor_id", actor_id)
        
        abilities_that_are_not_connected = []

        if len(ability_ids) == 1:
            db_abilites = self.select_not_in("*","abilities","id", ability_ids[0])
            for ability in db_abilites:
                abilities_that_are_not_connected.append(Ability(*ability))

        else:
            abilities_that_are_not_connected = self.get_all_abilities()
        
        return abilities_that_are_not_connected

    def get_ability_list_exclude_role(self, role_id):
        ability_ids = self.select_where("ability_id", "roles_to_abilities", "role_id", role_id)
        
        abilities_that_are_not_connected = []

        if len(ability_ids) == 1:
            db_abilites = self.select_not_in("*","abilities","id", ability_ids[0])
            for ability in db_abilites:
                abilities_that_are_not_connected.append(Ability(*ability))

        else:
            abilities_that_are_not_connected = self.get_all_abilities()  
        
        return abilities_that_are_not_connected

    def get_ability_template_list(self, role_id):
        template_id_list = self.select_where("template_id", "roles_to_ability_templates", "role_id", role_id)
        
        ability_templates = []

        for template_id in template_id_list:
            ability_templates.append(self.get_ability_template(template_id[0]))

        return ability_templates

    def get_ability_template_list_exclude_role(self, role_id):
        template_id_list = self.select_where("template_id", "roles_to_ability_templates", "role_id", role_id)
        new_id_list = [temp_id[0] for temp_id in template_id_list]

        excluded_template_id_list = self.select_not_in("template_id", "ability_templates", "template_id", new_id_list)

        ability_templates = []

        for id in excluded_template_id_list:
            ability_templates.append(self.get_ability_template(id[0]))

        return ability_templates

    def get_abilities_template(self, template_id):
        fetched_ability_id_list = self.select_where("ability_id", "ability_templates_to_abilities", "template_id", template_id)
        new_id_list = [id[0] for id in fetched_ability_id_list]
        ability_list = []
        for ability_id in new_id_list:
            ability_list.append(self.get_ability(ability_id))
        return ability_list

    def get_ability_list_exclude_template(self, template_id):
        ability_ids = self.select_where("ability_id", "ability_templates_to_abilities", "template_id", template_id)

        abilities_that_are_not_connected = []

        if len(ability_ids) == 1:
            new_ids = [id for id in ability_ids[0]]
            db_abilites = self.select_not_in("*","abilities","id", new_ids)
            for ability in db_abilites:
                abilities_that_are_not_connected.append(Ability(*ability))

        else:
            abilities_that_are_not_connected = self.get_all_abilities()
        
        return abilities_that_are_not_connected

    def create_ability_template(self, name, description):
        pass

    def remove_template(self, role_id, template_id_list):
        pass

    def add_template_role(self, role_id, template_id_list):
        pass

    def get_ability_template(self, template_id):
        template = self.select_where("*", "ability_templates", "template_id", template_id)[0]
        return AbilityTemplate(*template, self)
        
    def remove_ability_from_template(self, template_id, ability_list):
        pass

    def add_abilities_to_template(self,template_id, ability_list):
        pass

    def create_template_history(self, template_id, new_name, new_description):
        pass

    def get_template_history(self, template_id):
        revision_list = []
        history = self.select_where("*", "ability_template_history", "id", template_id)
        for revision in history:
            revision_list.append(TemplateHistory(*revision))
        return revision_list

    def get_all_abilities(self):
        fetched_abilities = self.select('*', 'abilities')
        abilities = []
        for ability in fetched_abilities:
            abilities.append(Ability(*ability))
        return abilities

    def get_ability_history(self, id):
        revision_list = []
        history = self.select_where("*", "abilities_history", "id", id)
        for revision in history:
            revision_list.append(AbilityHistory(*revision))
        return revision_list

    #RELEATIONSHIPS#
    def add_relationship_actor(self, actor1_id, actor1_name, actor2_id, actor2_name, relationship_type):
        pass

    def get_relationships_actor_by_actor_id(self, actor_id):
        relationships = []
        fetched_relationships = self.select_or("*", "actor_relationships", "actor1_id", actor_id, "actor2_id", actor_id)
        if len(fetched_relationships) != 0:
            for relationship in fetched_relationships:
                new_relationship = ActorRelationship(*relationship)
                new_relationship.set_link_actor(actor_id)
                relationships.append(new_relationship)
        else:
            print(f'No relationships for actor {actor_id}')
        return relationships

    def remove_relationships_actor(self, relationship_id_list):
        pass

    def add_relationship_role(self, role1_id, role1_name, role2_id, role2_name, relationship_type):
        pass

    def get_relationships_role_by_role_id(self, role_id):
        relationships = []
        fetched_relationships = self.select_or("*", "role_relationships", "role1_id", role_id, "role2_id", role_id)
        for relationship in fetched_relationships:
            relationships.append(RoleRelationship(*relationship, self))
        return relationships

    def remove_relationships_role(self, relationship_id_list):
        pass