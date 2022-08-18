import constants
from neo4j import GraphDatabase
import logging

from classes.nodes.image import Image
from classes.nodes.actor import Actor
from classes.nodes.meta_role import MetaRole
from classes.nodes.role import Role
from classes.nodes.actor_relationship import ActorRelationship
from classes.nodes.role_relationship import RoleRelationship
from classes.nodes.ability import Ability
from classes.nodes.ability_template import AbilityTemplate

from classes.histories.actor_history import ActorHistory
from classes.histories.meta_role_history import MetaRoleHistory
from classes.histories.role_history import RoleHistory
from classes.histories.template_history import TemplateHistory
from classes.histories.ability_history import AbilityHistory

#TODO this needs a lot of testing, because i'm sure I do it wrong
#TODO clean up methods that are never called

class DatabaseControllerNeo():
    def __init__(self, database_uri = constants.NEO_URI):
        self._database_uri = database_uri
        self._auth = (constants.neo_user, constants.neo_pass)
        self.connection = self._create_connection() 
        #TODO use 'with' more often

#Roles have to be nodes, too, because they have realtionships between them

    def _create_connection(self):
        try:
            return GraphDatabase.driver(self._database_uri, auth=self._auth)
        except:
            logging.exception()
            logging.error("Failed to create neo4j Driver!")

    def _neo4j_close_driver(self):
        if self.connection is not None:
            self.connection.close()
        
    def execute(self, command, parameters=None):
        assert self.connection is not None, "neo4j Driver not initialized!"
        session = None
        response = None

        try:
            session = self.connection.session()
            response = list(session.run(command,parameters))
            #TODO because this is a list, double check it's processed at the right level
        except Exception:
            logging.exception()
            logging.error(f"Query failed: query \'{command}\', parameters:")
            logging.error(parameters)
        finally:
            #finally is always executed after a 'try', no matter what
            if session is not None:
                session.close()
        return response

    #TODO each query returns a list

    def create_db_if_not_exists(self):
        self.execute("CREATE DATABASE rac IF NOT EXISTS")
        unique_actor_neo = '''CREATE CONSTRAINT [unique_actor] [IF NOT EXISTS]
            FOR (a:Actor)
            REQUIRE a.id IS UNIQUE'''
        self.execute(unique_actor_neo)
        unique_mr_neo = '''CREATE CONSTRAINT [unique_meta_role] [IF NOT EXISTS]
            FOR (mr:Meta Role)
            REQUIRE mr.id IS UNIQUE'''
        self.execute(unique_mr_neo)
        #TODO a better history than an sql or neo database
        
    #CREATE#
    def create_actor(self, id, name, bio, birth_date, death_date):
        actor_parameters = {'id': id, 'name':name, 'bio':bio, 'birth_date':birth_date, 'death_date':death_date}
        create_actor_neo = '''CREATE a:ACTOR {id: $id, name: $name, bio: $bio, birth_date: $birth_date, death_date: $death_date}'''
        self.execute(create_actor_neo, actor_parameters)

    def create_role(self,role_id, role_name, actor_id, mr_id):
        
        role_parameters = {'actor_id': actor_id, 'mr_id': mr_id, 'role_id':role_id, 'role_name':role_name}
        create_role_neo = '''CREATE r:ROLE {id: $role_id, name: $role_name, first_parent_meta: $mr_id}'''
        self.execute(create_role_neo, role_parameters)

        connect_role_parameters = {'actor_id': actor_id, 'mr_id': mr_id, 'role_id': role_id}
        connect_role_neo = '''MATCH a:Actor, mr:Meta Role, r:ROLE WHERE a.id = {$actor_id} AND mr.id = {$mr_id} AND r.id={$role_id} CREATE (a)->[p:PLAYS]-(r)-[v:VERSION]->(mr)'''
        self.execute(connect_role_neo,connect_role_parameters)

    def create_mr(self, character_name, mr_id):
        create_mr_neo = '''CREATE mr:META ROLE {id: $mr_id, name: $character_name, description: auto-generated, historical: 0, religious: 0,fictional_in_universe: 0, is_biggest: 0}'''
        #no built-in function for is_biggest. You'll have to find them all and sort, then get the first  in the list
        parameters = {"character_name" : character_name, "mr_id": mr_id}
        self.execute(create_mr_neo, parameters=parameters)

    def create_role_and_first_mr(self,character_name, role_id, role_name, actor_id):
        self.create_mr(character_name, role_id)
        self.create_role(role_id, role_name, actor_id, role_id)

    #UPDATE#

    def _changeMR(self, role_id, mr_id):
        delete_neo = """MATCH (r:ROLE {id: $role_id}) - [v:VERSION] -> ()
        DELETE v"""
        match_parameters = {'role_id': role_id}
        self.execute(delete_neo, match_parameters)

        connect_role_parameters = {'mr_id': mr_id, 'role_id': role_id}
        connect_role_neo = '''mr:Meta Role, r:ROLE WHERE mr.id = {$mr_id} AND r.id={$role_id} CREATE (r)-[v:VERSION]->(mr)'''
        self.execute(connect_role_neo,connect_role_parameters)


    def _resetMR(self, role_id):
        match_and_delete_neo = """MATCH (r:ROLE {id: $role_id}) - [v:VERSION] -> ()
        DELETE v"""
        match_parameters = {'role_id': role_id}
        self.execute(match_and_delete_neo, match_parameters)

        connect_role_parameters = {'role_id': role_id}
        connect_role_neo = '''mr:Meta Role, r:ROLE WHERE mr.id = r.first_parent_meta AND r.id={$role_id} CREATE (r)-[v:VERSION]->(mr)'''
        self.execute(connect_role_neo,connect_role_parameters)

    def _mergeMR(self, metaID1, metaID2):
        if (metaID1 != metaID2):
            lowest = min(metaID1, metaID2)
            highest = max(metaID1, metaID2)
            delete_neo = """MATCH (r:ROLE) - [v:VERSION] -> (mr:META ROLE {id: $lowest})
            DELETE v
            MATCH (mr:Meta Role {id: $highest}) CREATE (r)-[v:VERSION]->(mr)"""
            match_parameters = {'highest': highest,'lowest': lowest}
            self.execute(delete_neo, match_parameters)

    def _connect_actor_swap(self, roleID1, roleID2, mr_id_1, mr_id_2):
        if roleID1 != roleID2:

            if mr_id_1 != mr_id_2:
                self._mergeMR(mr_id_1, mr_id_2)

            actor_swap_parameters = {'role1':roleID1, 'role2':roleID2}
            actor_swap_neo = """MATCH (r1:ROLE {id:$role1}), (r2:ROLE {id:$role2}) CREATE (r1) - [actor_swap] - (r2)"""
            self.execute(actor_swap_neo, actor_swap_parameters)
            
        else:
            print("Actor Swap Error: IDs are the same.")

    def _remove_actor_swap(self, role_id):
        remove_actor_swap_neo = """MATCH (r:ROLE {id:$role_id}) REMOVE (r) - [actor_swap] - () """
        remove_actor_swap_parameters = {'role_id':role_id}
        self.execute(remove_actor_swap_neo,remove_actor_swap_parameters)

    #TODO we can select the whole web. Maybe adjust accordingly.

    #IMAGES#
    def add_image(self,page_type, page_id, image_url, caption):
        if page_type == 'actor':
            neo = '''MATCH (a:ACTOR {id:$page_id}) CREATE (i:IMAGE {url:$image_url, caption:$caption})-[GALLERY]-(a)'''
        else:
            neo = '''MATCH (r:ROLE {id:$page_id}) CREATE (i:IMAGE {url:$image_url, caption:$caption})-[GALLERY]-(r)'''
        parameters = {'page_id':page_id, 'image_url': image_url, 'caption':caption}
        self.execute(neo, parameters)

    def get_images_actor(self, actor_id):
        #LEAVE UN-PASSED
        fetched_images = self.execute('''MATCH (i:IMAGE)-[GALLERY]-(a:ACTOR {id:$page_id})''', parameters={'page_id': actor_id})
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    def get_images_role(self, role_id):
        #LEAVE UN-PASSED
        fetched_images = self.execute('''MATCH (i:IMAGE)-[GALLERY]-(r:ROLE {id:$page_id})''', parameters={'page_id': role_id})
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    #GET#
    #TODO maybe search in bios or descriptions?

    def get_actor(self, actor_id):
        #TODO callback to get an actor that's not already in the db (send an error: no such actor in db, then try imdbImp, then imdbImp will give an error if no such person)
        if actor_id != '':
            fetched_actor = self.execute('''MATCH (a:ACTOR {id:$actor_id})''', {'actor_id':actor_id})
            actor = Actor(*fetched_actor, self)
            return actor
        else:
            print('get_actor error: there was no base_id')

    def get_actors_search(self, query):
        actors = []
        fetched_actors = self.execute('''MATCH (a:ACTOR) WHERE a.name CONTAINS $query''', {'query':query})
        for actor in fetched_actors:
            actors.append(Actor(*actor, self))
        return actors

    def get_all_actors(self):
        all_actors_fetched = self.execute('''MATCH (a:ACTOR)''')
        all_actors = []
        for actor in all_actors_fetched:
            all_actors.append(Actor(*actor, self))
        return all_actors

    def get_mr(self, mr_id):
        fetched_mr = self.execute('''MATCH (mr:META_ROLE) WHERE mr.id = $mr_id''', {'mr_id':mr_id})
        return MetaRole(*fetched_mr, self)

    def get_mrs_search(self,query):
        mrs = []
        fetched_mrs = self.self.execute('''MATCH (mr:META_ROLE)''')
        for mr in fetched_mrs:
            new_mr = MetaRole(*mr, self)
            new_mr.get_roles()
            if new_mr.roles != []:
                mrs.append(new_mr)
            
        return mrs

    def get_role(self, role_id):
        fetched_role = self.execute('''MATCH (r:ROLE) WHERE r.id = $role_id''', {'role_id':role_id})
        if len(fetched_role) != 0:
            return Role(*fetched_role[0], self)
        else:
            print(f'No such role: {role_id}')

    def get_roles(self, parent_id, is_actor):
        roles = []
        if is_actor:
            fetched_roles = self.execute('''MATCH (r:ROLE)<-[PLAYS]-(a:ACTOR {id:$parent_id})''', {'parent_id':parent_id})
        else:
            fetched_roles = self.execute('''MATCH (r:ROLE)<-[VERSION]-(a:META_ROLE {id:$parent_id})''', {'parent_id':parent_id})
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles

    def get_all_roles(self):
        all_roles_fetched = self.execute('''MATCH (r:ROLE)''')
        all_roles = []
        for role in all_roles_fetched:
            all_roles.append(Role(*role, self))
        return all_roles

    def get_roles_search(self, query):
        roles = []
        fetched_roles = self.execute('''MATCH (r:ROLE) WHERE r.name CONTAINS $query''', {'query':query})
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles
        
    def get_roles_swap(self, mr_id, actor_swap_id):
        roles = []
        fetched_roles = self.execute('''MATCH (mr:META_ROLE {id:$mr_id})<-[VERSION]-()-[ACTOR_SWAP]-()''',{'mr_id':mr_id})
        for role in fetched_roles:
            roles.append(Role(*role,self))
        return roles

    def get_parent_meta(self, role_id):
        parent_meta = self.execute('''MATCH (r:ROLE)<-[VERSION]-(mr:META_ROLE) WHERE r.id = $role_id RETURN mr.id''',{'role_id':role_id})
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

    #TODO
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
        old_actor = self.get_actor(id)
        historySql = '''INSERT INTO actors_history(id, name, bio) VALUES (?,?,?) '''
        self.cursor.execute(historySql,(id, old_actor.name, old_actor.bio))
        
        changeDescSql='''UPDATE actors SET bio=? WHERE id=?'''
        self.cursor.execute(changeDescSql,(new_bio,id,))

    def create_mr_history(self, id, new_description, historical, religious, fictional_in_universe):
        old_mr = self.get_mr(id)
        historySql = '''INSERT INTO meta_roles_history(id, name, description, historical, religious, fictional_in_universe) VALUES (?,?,?,?,?,?) '''
        self.cursor.execute(historySql,(id, old_mr.name, old_mr.description, old_mr.historical, old_mr.religious, old_mr.fictional_in_universe))
        changeDescSql='''UPDATE meta_roles SET description=?, historical=?, religious=?, fictional_in_universe=? WHERE id=?'''

        self.cursor.execute(changeDescSql,(new_description,historical, religious, fictional_in_universe,id,))

    def create_role_history(self, id, new_description, new_alive_or_dead, new_alignment):
        old_role = self.get_role(id)
        historySql = '''INSERT INTO roles_history(id, name, description, alive_or_dead, alignment) VALUES (?,?,?,?,?) '''
        self.cursor.execute(historySql,(id, old_role.name, old_role.description, old_role.alive_or_dead, old_role.alignment))
        changeDescSql='''UPDATE roles SET description=?, alive_or_dead=?,alignment=? WHERE id=?'''

        self.cursor.execute(changeDescSql,(new_description,new_alive_or_dead,new_alignment,id,))  

    #CHARACTER CONNECTOR#
    def character_connector_switch(self, mode, id1, id2):
        if id1 != None and id2 != None:
            role_id_1, mr_id_1 = id1.split('|')
            role_id_2, mr_id_2 = id2.split('|')

            if mode == "changeMR":
                self._changeMR(role_id_1, mr_id_2)
            elif mode == "resetMR":
                self._resetMR(role_id_1)
            elif mode == "mergeMR":
                self._mergeMR(mr_id_1,mr_id_2)
            elif mode == "actorSwap":
                self._connect_actor_swap(role_id_1,role_id_2, mr_id_1, mr_id_2)
            elif mode == "removeActorSwap":
                self._remove_actor_swap(role_id_1)
            else:
                print(f'Opperation \'{mode}\' does not exist.')

            self.commit()
    #TODO create a splitter function that makes two MR's with roles divided based on their id (maybe two lists of id's to check against?)

    #TODO a hsitory in each role of it's prior Mr's name, including an option to revert the whole change. Changes have change Id's. 
    # You can revert an mr change by ID without changing the ID's 

    #TODO abilities need to be nodes
    #ABILITIES#
    def create_ability(self, name, description):
        pass
        create_sql = '''INSERT INTO abilities (name, description) VALUES (?,?)'''
        self.cursor.execute(create_sql, (name, description))
        return self.cursor.lastrowid

    def create_ability_history(self, id, name, description):
        pass
        old_ability = self.get_ability(id)
        try:
            historySql = '''INSERT INTO abilities_history(id, name, description) VALUES (?,?,?) '''
            self.cursor.execute(historySql, (old_ability.id, old_ability.name, old_ability.description,))
        except IntegrityError:
            logging.error()

        changeDescSql='''UPDATE abilities SET name=?, description=? WHERE id=?'''
        self.cursor.execute(changeDescSql, (name, description, id,))

    def remove_ability_actor(self, actor_id, ability_list):
        pass
        self.cursor.execute("DELETE FROM actors_to_abilities WHERE actor_id={}  AND ability_id IN ".format(actor_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def remove_ability_role(self, role_id, ability_list):
        pass
        self.cursor.execute("DELETE FROM roles_to_abilities WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_ability_actor(self, actor_id, ability_list):
        pass
        create_ability_actor_sql = "INSERT OR IGNORE INTO actors_to_abilities(actor_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(create_ability_actor_sql,(actor_id,ability_id,))

    def add_ability_role(self, role_id, ability_list):
        pass
        create_ability_role_sql = "INSERT OR IGNORE INTO roles_to_abilities(role_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(create_ability_role_sql,(role_id,ability_id,))

    def get_ability(self, ability_id):
        pass
        fetched_ability = self.select_where("*","abilities","id",ability_id)
        if len(fetched_ability) == 1:
            ability = fetched_ability[0]
            return Ability(*ability)

    def get_ability_list_role(self, role_id):
        pass
        ability_ids = self.select_where("ability_id", "roles_to_abilities", "role_id", role_id)
        abilities = []
        if len(ability_ids) >= 1:
            for id_tuple in ability_ids:
                abilities.append(self.get_ability(id_tuple[0]))
        return abilities

    def get_ability_list_actor(self, actor_id):
        pass
        ability_ids = self.select_where("ability_id", "actors_to_abilities", "actor_id", actor_id)
        abilities = []
        if len(ability_ids) == 1:
            for id in ability_ids[0]:
                abilities.append(self.get_ability(id))
        return abilities

    def get_ability_list_exclude_actor(self, actor_id):
        pass
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
        pass
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
        pass
        template_id_list = self.select_where("template_id", "roles_to_ability_templates", "role_id", role_id)
        
        ability_templates = []

        for template_id in template_id_list:
            ability_templates.append(self.get_ability_template(template_id[0]))

        return ability_templates

    def get_ability_template_list_exclude_role(self, role_id):
        pass
        template_id_list = self.select_where("template_id", "roles_to_ability_templates", "role_id", role_id)
        new_id_list = [temp_id[0] for temp_id in template_id_list]

        excluded_template_id_list = self.select_not_in("template_id", "ability_templates", "template_id", new_id_list)

        ability_templates = []

        for id in excluded_template_id_list:
            ability_templates.append(self.get_ability_template(id[0]))

        return ability_templates

    def get_abilities_template(self, template_id):
        pass
        fetched_ability_id_list = self.select_where("ability_id", "ability_templates_to_abilities", "template_id", template_id)
        new_id_list = [id[0] for id in fetched_ability_id_list]
        ability_list = []
        for ability_id in new_id_list:
            ability_list.append(self.get_ability(ability_id))
        return ability_list

    def get_ability_list_exclude_template(self, template_id):
        pass
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
        create_template_sql = "INSERT INTO ability_templates(template_name, template_description) VALUES (?,?)"
        self.cursor.execute(create_template_sql,(name,description))
        return self.cursor.lastrowid

    def remove_template(self, role_id, template_id_list):
        pass
        self.cursor.execute("DELETE FROM roles_to_ability_templates WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(template_id_list)), template_id_list)

    def add_template_role(self, role_id, template_id_list):
        pass
        add_template_sql = '''INSERT OR IGNORE INTO roles_to_ability_templates(role_id, template_id) VALUES (?,?)'''
        for template_id in template_id_list:
            self.cursor.execute(add_template_sql, (role_id, template_id))

    def get_ability_template(self, template_id):
        pass
        template = self.select_where("*", "ability_templates", "template_id", template_id)[0]
        return AbilityTemplate(*template, self)
        
    def remove_ability_from_template(self, template_id, ability_list):
        pass
        self.cursor.execute("DELETE FROM ability_templates_to_abilities WHERE template_id={} AND ability_id IN".format(template_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_abilities_to_template(self,template_id, ability_list):
        pass
        connect_template_ability_sql = "INSERT OR IGNORE INTO ability_templates_to_abilities(template_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(connect_template_ability_sql,(template_id,ability_id,))

    def create_template_history(self, template_id, new_name, new_description):
        pass
        old_template = self.get_ability_template(template_id)
        try:
            historySql = '''INSERT INTO ability_template_history(id, name, description) VALUES (?,?,?) '''
            self.cursor.execute(historySql, (old_template.id, old_template.name, old_template.description,))
        except IntegrityError:
            logging.exception()

        changeDescSql='''UPDATE ability_templates SET template_name=?, template_description=? WHERE template_id=?'''
        self.cursor.execute(changeDescSql, (new_name, new_description, template_id,))

    def get_template_history(self, template_id):
        pass
        revision_list = []
        history = self.select_where("*", "ability_template_history", "id", template_id)
        for revision in history:
            revision_list.append(TemplateHistory(*revision))
        return revision_list

    def get_all_abilities(self):
        pass
        fetched_abilities = self.select('*', 'abilities')
        abilities = []
        for ability in fetched_abilities:
            abilities.append(Ability(*ability))
        return abilities

    def get_ability_history(self, id):
        pass
        revision_list = []
        history = self.select_where("*", "abilities_history", "id", id)
        for revision in history:
            revision_list.append(AbilityHistory(*revision))
        return revision_list

    #RELEATIONSHIPS#
    def add_relationship_actor(self, actor1_id, actor1_name, actor2_id, actor2_name, relationship_type):
        add_relationship_neo = '''MATCH (a1:ACTOR {id:$actor1_id}), (a2:ACTOR {id:$actor2_id}}) CREATE (a1) - [$relationship_type] - (a2)'''
        add_relationship_parameters = {'actor1_id':actor1_id, 'actor2_id':actor2_id, 'relationship_type':relationship_type.upper()}
        self.execute(add_relationship_neo,add_relationship_parameters)

    def get_relationships_actor_by_actor_id(self, actor_id):
        relationships = []
        fetched_relationships = self.execute('''MATCH (a:ACTOR {id:$actor_id})-[]-(a2:ACTOR) RETURN a.id, a.name, a2,id, a2.name''', {'actor_id':actor_id})
        if len(fetched_relationships) != 0:
            for relationship in fetched_relationships:
                new_relationship = ActorRelationship(*relationship)
                new_relationship.set_link_actor(actor_id)
                relationships.append(new_relationship)
        else:
            print(f'No relationships for actor {actor_id}')
        return relationships

    def remove_relationships_actor(self, actor_id, relationship_id_list):
        for relationship_id in relationship_id_list:
            remove_relationship_neo = '''MATCH (a:ACTOR {id:$actor_id})-[rel:]-(ACTOR) WHERE rel.id IN $relationship_id_list DELETE rel'''
            remove_relationship_parameters = {'actor_id':actor_id, 'relationship_id_list':relationship_id_list}
            self.execute(remove_relationship_neo, remove_relationship_parameters)

    def add_relationship_role(self, role1_id, role1_name, role2_id, role2_name, relationship_type):
        add_relationship_neo = '''MATCH (r1:ROLE {id:$role1_id}), (a2:ROLE {id:$role2_id}}) CREATE (r1) - [:$relationship_type] - (r2)'''
        add_relationship_parameters = {'role1_id':role1_id, 'role1_id':role2_id, 'relationship_type':relationship_type.upper()}
        self.execute(add_relationship_neo,add_relationship_parameters)

    def get_relationships_role_by_role_id(self, role_id):
        relationships = []
        get_relationships_neo = '''MATCH (r:ROLE {id:$role_id}) - [r] - (r2:ROLE) WHERE r <> 'ACTOR_SWAP' RETURN r.id, r.name, r2.id, r2.name '''
        get_relationships_parameters = {'role_id':role_id}
        fetched_relationships = self.execute(get_relationships_neo,get_relationships_parameters)
        for relationship in fetched_relationships:
            relationships.append(RoleRelationship(*relationship, self))
        return relationships

    def remove_relationships_role(self, role_id, relationship_id_list):
        remove_relationship_neo = '''MATCH (r:ROLE {id:$role_id})-[rel:]-(ROLE) WHERE rel.id IN $relationship_id_list DELETE rel'''
        remove_relationship_parameters = {'role_id':role_id, 'relationship_id_list':relationship_id_list}
        self.execute(remove_relationship_neo, remove_relationship_parameters)