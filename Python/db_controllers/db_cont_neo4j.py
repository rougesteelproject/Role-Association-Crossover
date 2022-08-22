import constants
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable, ClientError, ConstraintError, CypherSyntaxError

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
#TODO fictional_in_universe needs to get moved to roles, to resolve eg: Buzz Lightyear the toy having same MR as fictional Buzz the movie character

class DatabaseControllerNeo():
    def __init__(self, database_uri = constants.NEO_URI):
        self._database_uri = database_uri

        #DEBUGGING#
        #handler = logging.StreamHandler(sys.stdout)
        #handler.setLevel(logging.DEBUG)
        #logging.getLogger("neo4j").addHandler(handler)
        #logging.getLogger("neo4j").setLevel(logging.DEBUG)

        self._connection = self._create_connection()
        self._create_db_if_not_exists()
        #TODO use 'with' more often

#Roles have to be nodes, too, because they have realtionships between them

    def _create_connection(self):
        try:
            return GraphDatabase.driver(uri = self._database_uri, auth=(constants.neo_user, constants.neo_pass))
        except:
            logging.exception("Failed to create neo4j Driver!")

    def _neo4j_close_driver(self):
        if self._connection is not None:
            self._connection.close()
        
    def _execute(self, command, parameters=None):
        assert self._connection is not None, "neo4j Driver not initialized!"
        session = None
        response = None

        try:
            with  self._connection.session() as session:
                response = session.run(command,parameters)
                data = response.data()
                return [record for record in data]
            #TODO because this is a list, double check it's processed at the right level
        except ServiceUnavailable:
            logging.exception('ServiceUnavailable while trying to create a session and execute a neo4j command')
            logging.error('Restart the pc, then set the username and password to the constants')
            logging.error(f"Query failed: query \'{command}\', parameters:")
            logging.error(parameters)
        except ConstraintError:
            logging.info(f'Tried to create a node that already exists.', exc_info=1)
        except CypherSyntaxError:
            logging.exception('Syntax error in neo command:')
        except ClientError:
            logging.exception('ClientError while trying to execute neo command')
            logging.error(f"Query failed: query \'{command}\', parameters:")
            logging.error(parameters)
        except Exception:
            logging.exception('An exception ocured while trying to _execute a neo4j command')
            logging.error(f"Query failed: query \'{command}\', parameters:")
            logging.error(parameters)

    #TODO each query returns a list

    def _create_db_if_not_exists(self):
        self._execute("CREATE DATABASE rac IF NOT EXISTS")
        unique_actor_neo = '''CREATE CONSTRAINT unique_actor IF NOT EXISTS FOR (a:Actor) REQUIRE a.imdb_id IS UNIQUE'''
        self._execute(unique_actor_neo)
        unique_mr_neo = '''CREATE CONSTRAINT unique_meta_role IF NOT EXISTS FOR (mr:Meta_Role) REQUIRE mr.mr_id IS UNIQUE'''
        self._execute(unique_mr_neo)
        unique_role_neo = '''CREATE CONSTRAINT unique_role IF NOT EXISTS FOR (r:Role) REQUIRE r.role_id IS UNIQUE'''
        self._execute(unique_role_neo)
        #TODO a better history than an sql or neo database
        
    #CREATE#
    def create_actor(self, id, name, bio, birth_date, death_date):
        actor_parameters = {'id': id, 'name':name, 'bio':bio, 'birth_date':birth_date, 'death_date':death_date}
        create_actor_neo = '''CREATE (a:Actor {imdb_id: $id, name: $name, bio: $bio, birth_date: $birth_date, death_date: $death_date})'''
        self._execute(create_actor_neo, actor_parameters)

    def create_role(self,role_id, role_name, actor_id, mr_id):
        
        role_parameters = {'actor_id': actor_id, 'mr_id': mr_id, 'role_id':role_id, 'role_name':role_name}
        create_role_neo = '''CREATE (r:Role {role_id: $role_id, name: $role_name})'''
        self._execute(create_role_neo, role_parameters)

        connect_role_parameters = {'actor_id': actor_id, 'mr_id': mr_id, 'role_id': role_id}
        connect_role_neo = '''MATCH (a:Actor), (mr:Meta_Role), (r:Role) WHERE a.imdb_id = $actor_id AND mr.mr_id = $mr_id AND r.role_id=$role_id MERGE (a)-[p:PLAYS]->(r)-[v:VERSION]->(mr)'''
        self._execute(connect_role_neo,connect_role_parameters)

    def create_mr(self, character_name, mr_id):
        create_mr_neo = '''CREATE (mr:Meta_Role {mr_id: $mr_id, name: $character_name, description: 'auto-generated', historical: 0, religious: 0,fictional_in_universe: 0, is_biggest: 0})'''
        #no built-in function for is_biggest. You'll have to find them all and sort, then get the first  in the list
        parameters = {"character_name" : character_name, "mr_id": mr_id}
        self._execute(create_mr_neo, parameters=parameters)

    def create_role_and_first_mr(self,character_name, role_id, role_name, actor_id):
        self.create_mr(character_name, role_id)
        self.create_role(role_id, role_name, actor_id, role_id)

    #UPDATE#

    def _changeMR(self, role_id, mr_id):
        delete_neo = """MATCH (r:Role {role_id: $role_id}) - [v:VERSION] -> () DELETE v"""
        match_parameters = {'role_id': role_id}
        self._execute(delete_neo, match_parameters)

        connect_role_parameters = {'mr_id': mr_id, 'role_id': role_id}
        connect_role_neo = '''mr:Meta_Role, r:Role WHERE mr.id = $mr_id AND r.id=$role_id MERGE (r)-[v:VERSION]->(mr)'''
        self._execute(connect_role_neo,connect_role_parameters)


    def _resetMR(self, role_id):
        match_and_delete_neo = """MATCH (r:Role {role_id: $role_id}) - [v:VERSION] -> () DELETE v"""
        match_parameters = {'role_id': role_id}
        self._execute(match_and_delete_neo, match_parameters)

        connect_role_parameters = {'role_id': role_id}
        connect_role_neo = '''mr:Meta_Role, r:Role WHERE  r.id=$role_id AND mr.id = r.role_id MERGE (r)-[v:VERSION]->(mr)'''
        self._execute(connect_role_neo,connect_role_parameters)

    def _mergeMR(self, metaID1, metaID2):
        if (metaID1 != metaID2):
            lowest = min(metaID1, metaID2)
            highest = max(metaID1, metaID2)
            delete_neo = """MATCH (r:Role) - [v:VERSION] -> (mr:Meta_Role {mr_id: $lowest}) DELETE v"""
            merge_neo = """MATCH (mr:Meta_Role {id: $highest}) MERGE (r)-[v:VERSION]->(mr)"""
            match_parameters = {'highest': highest,'lowest': lowest}
            self._execute(delete_neo, match_parameters)
            self._execute(merge_neo, match_parameters)

    def _connect_actor_swap(self, roleID1, roleID2, mr_id_1, mr_id_2):
        if roleID1 != roleID2:

            if mr_id_1 != mr_id_2:
                self._mergeMR(mr_id_1, mr_id_2)

            actor_swap_parameters = {'role1':roleID1, 'role2':roleID2}
            actor_swap_neo = """MATCH (r1:Role {role_id:$role1}), (r2:Role {role_id:$role2}) MERGE (r1) - [:ACTOR_SWAP] - (r2)"""
            self._execute(actor_swap_neo, actor_swap_parameters)
            
        else:
            logging.debug("Actor Swap Error: IDs are the same.")

    def _remove_actor_swap(self, role_id):
        remove_actor_swap_neo = """MATCH (r:Role {role_id:$role_id}) REMOVE (r) - [:ACTOR_SWAP] - () """
        remove_actor_swap_parameters = {'role_id':role_id}
        self._execute(remove_actor_swap_neo,remove_actor_swap_parameters)

    #TODO we can select the whole web. Maybe adjust accordingly.

    #IMAGES#
    def add_image(self,page_type, page_id, image_url, caption):
        if page_type == 'actor':
            neo = '''MATCH (a:Actor {imdb_id:$page_id}) MERGE (i:IMAGE {url:$image_url, caption:$caption})-[:GALLERY]-(a)'''
        else:
            neo = '''MATCH (r:Role {role_id:$page_id}) MERGE (i:IMAGE {url:$image_url, caption:$caption})-[:GALLERY]-(r)'''
        parameters = {'page_id':page_id, 'image_url': image_url, 'caption':caption}
        self._execute(neo, parameters)

    def get_images_actor(self, actor_id):
        #LEAVE UN-PASSED
        fetched_images = self._execute('''MATCH (i:IMAGE)-[:GALLERY]-(a:Actor {imdb_id:$page_id}) RETURN i''', parameters={'page_id': actor_id})
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    def get_images_role(self, role_id):
        #LEAVE UN-PASSED
        fetched_images = self._execute('''MATCH (i:IMAGE)-[:GALLERY]-(r:Role {role_id:$page_id}) RETURN i''', parameters={'page_id': role_id})
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    #GET#
    #TODO maybe search in bios or descriptions?

    def get_actor(self, actor_id):
        #TODO callback to get an actor that's not already in the db (send an error: no such actor in db, then try imdbImp, then imdbImp will give an error if no such person)
        if actor_id != '':
            fetched_actor = self._execute('''MATCH (a:Actor {imdb_id:$actor_id}) RETURN a''', {'actor_id':actor_id})
            fetched_values = fetched_actor[0]["a"]
            actor = Actor(id= fetched_values["imdb_id"],name = fetched_values["name"], bio=fetched_values["bio"], birth_date=fetched_values["birth_date"], death_date=fetched_values["death_date"],is_biggest="False", db_control = self)
            return actor
        else:
            logging.debug('get_actor error: there was no base_id')

    def get_actors_search(self, query):
        actors = []
        fetched_actors = self._execute('''MATCH (a:Actor) WHERE a.name CONTAINS $query RETURN a''', {'query':query})
        for actor in fetched_actors:
            fetched_values = actor['a']
            actors.append(Actor(id= fetched_values["imdb_id"],name = fetched_values["name"], bio=fetched_values["bio"], birth_date=fetched_values["birth_date"], death_date=fetched_values["death_date"],is_biggest="False", db_control = self))
        return actors

    def get_all_actors(self):
        all_actors_fetched = self._execute('''MATCH (a:Actor) RETURN a''')
        all_actors = []
        for actor in all_actors_fetched:
            fetched_values = actor["a"]
            all_actors.append(Actor(id= fetched_values["imdb_id"],name = fetched_values["name"], bio=fetched_values["bio"], birth_date=fetched_values["birth_date"], death_date=fetched_values["death_date"],is_biggest="False", db_control = self))
        return all_actors

    def get_mr(self, mr_id):
        fetched_mr = self._execute('''MATCH (mr:Meta_Role {mr_id:$mr_id}) RETURN mr''', {'mr_id':mr_id})
        fetched_values = fetched_mr[0]['mr']
        return MetaRole(mr_id=fetched_values['mr_id'], name=fetched_values['name'],description=fetched_values['description'], historical=fetched_values['historical'],religious=fetched_values['religious'] ,fictional_in_universe=fetched_values['fictional_in_universe'],is_biggest=fetched_values['is_biggest'] , db_control=self)

    def get_mrs_search(self,query):
        mrs = []
        fetched_mrs = self.self._execute('''MATCH (mr:Meta_Role) WHERE mr.name CONTAINS $query RETURN mr''', {'query':query})
        for mr in fetched_mrs:
            fetched_values = mr["mr"]
            new_mr = MetaRole(mr_id=fetched_values['mr_id'], name=fetched_values['name'],description=fetched_values['description'], historical=fetched_values['historical'],religious=fetched_values['religious'] ,fictional_in_universe=fetched_values['fictional_in_universe'],is_biggest=fetched_values['is_biggest'], db_control=self)
            new_mr.get_roles()
            if new_mr.roles != []:
                mrs.append(new_mr)
            
        return mrs

    def get_role(self, role_id):
        fetched_role = self._execute('''MATCH (r:Role {role_id:$role_id}) RETURN r''', {'role_id':role_id})
        if len(fetched_role) != 0:
            role_values = fetched_role[0]["r"]
            return Role(role_id = role_values['role_id'], role_name = role_values['name'], db_control=self)
        else:
            logging.debug(f'No such role: {role_id}')

    def get_roles(self, parent_id, is_actor):
        roles = []
        if is_actor:
            fetched_roles = self._execute('''MATCH (r:Role)<-[:PLAYS]-(a:Actor {imdb_id:$parent_id}) RETURN r''', {'parent_id':parent_id})
        else:
            fetched_roles = self._execute('''MATCH (r:Role)<-[:VERSION]-(a:Meta_Role {mr_id:$parent_id}) RETURN r''', {'parent_id':parent_id})
        for role in fetched_roles:
            role_values = role["r"]
            roles.append(Role(role_id = role_values['role_id'], role_name = role_values['name'], db_control=self))
        return roles

    def get_all_roles(self):
        all_roles_fetched = self._execute('''MATCH (r:Role) RETURN r''')
        all_roles = []
        for role in all_roles_fetched:
            role_values = role["r"]
            all_roles.append(Role(role_id = role_values['role_id'], role_name = role_values['name'], db_control=self))
        return all_roles

    def get_roles_search(self, query):
        roles = []
        fetched_roles = self._execute('''MATCH (r:Role) WHERE r.name CONTAINS $query RETURN r''', {'query':query})
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles
        
    def get_roles_swap(self, mr_id, actor_swap_id):
        roles = []
        fetched_roles = self._execute('''MATCH (mr:Meta_Role {mr_id:$mr_id})<-[:VERSION]-(r:Role)-[:ACTOR_SWAP]-(r2:Role) RETURN r, r2''',{'mr_id':mr_id})
        for role in fetched_roles:
            roles.append(Role(*role,self))
        return roles

    def get_parent_meta(self, role_id):
        parent_meta = self._execute('''MATCH (r:Role {role_id:$role_id})-[:VERSION]->(mr:Meta_Role) RETURN mr.mr_id''',{'role_id':role_id})
        return parent_meta[0]['mr.mr_id']

    def get_parent_actor(self, role_id):
        parent_actor = role_id.split('-')
        return parent_actor

    def search_char_connector(self, query1, query2):
        connector_mrs_1 = self.get_mrs_search(query1)
        connector_mrs_2 = self.get_mrs_search(query2)

        roles_1 = self.get_roles_search(query1)
        roles_2 = self.get_roles_search(query2)

        for role in roles_1:
            mr_in_list = False
            for mr in connector_mrs_1:
                if mr.id == self.get_parent_meta(role.id):
                    mr_in_list= True

            if not mr_in_list:
                new_mr = self.get_mr(self.get_parent_meta(role.id))
                new_mr.get_roles()
                if new_mr.roles != []:
                    connector_mrs_1.append(new_mr)

        for role in roles_2:
            mr_in_list = False
            for mr in connector_mrs_2:
                if mr.id == self.get_parent_meta(role.id):
                    mr_in_list= True

            if not mr_in_list:
                new_mr = self.get_mr(self.get_parent_meta(role.id))
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
                if self.get_parent_meta(role.id) == mr.id:
                    in_mrs = True

            if not in_mrs:
                search_bar_mrs.append(self.get_mr(self._db_control.get_parent_meta(role.id)))

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
        self.cursor._execute(historySql,(id, old_actor.name, old_actor.bio))
        
        changeDescSql='''UPDATE actors SET bio=? WHERE id=?'''
        self.cursor._execute(changeDescSql,(new_bio,id,))

    def create_mr_history(self, id, new_description, historical, religious, fictional_in_universe):
        old_mr = self.get_mr(id)
        historySql = '''INSERT INTO meta_roles_history(id, name, description, historical, religious, fictional_in_universe) VALUES (?,?,?,?,?,?) '''
        self.cursor._execute(historySql,(id, old_mr.name, old_mr.description, old_mr.historical, old_mr.religious, old_mr.fictional_in_universe))
        changeDescSql='''UPDATE meta_roles SET description=?, historical=?, religious=?, fictional_in_universe=? WHERE id=?'''

        self.cursor._execute(changeDescSql,(new_description,historical, religious, fictional_in_universe,id,))

    def create_role_history(self, id, new_description, new_alive_or_dead, new_alignment):
        old_role = self.get_role(id)
        historySql = '''INSERT INTO roles_history(id, name, description, alive_or_dead, alignment) VALUES (?,?,?,?,?) '''
        self.cursor._execute(historySql,(id, old_role.name, old_role.description, old_role.alive_or_dead, old_role.alignment))
        changeDescSql='''UPDATE roles SET description=?, alive_or_dead=?,alignment=? WHERE id=?'''

        self.cursor._execute(changeDescSql,(new_description,new_alive_or_dead,new_alignment,id,))  

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
                logging.debug(f'Opperation \'{mode}\' does not exist.')

            self.commit()
    #TODO create a splitter function that makes two MR's with roles divided based on their id (maybe two lists of id's to check against?)

    #TODO a hsitory in each role of it's prior Mr's name, including an option to revert the whole change. Changes have change Id's. 
    # You can revert an mr change by ID without changing the ID's 

    #TODO abilities need to be nodes
    #ABILITIES#
    def create_ability(self, name, description):
        return None
        create_sql = '''INSERT INTO abilities (name, description) VALUES (?,?)'''
        self.cursor._execute(create_sql, (name, description))
        return self.cursor.lastrowid

    def create_ability_history(self, id, name, description):
        return None
        old_ability = self.get_ability(id)
        try:
            historySql = '''INSERT INTO abilities_history(id, name, description) VALUES (?,?,?) '''
            self.cursor._execute(historySql, (old_ability.id, old_ability.name, old_ability.description,))
        except IntegrityError:
            logging.error()

        changeDescSql='''UPDATE abilities SET name=?, description=? WHERE id=?'''
        self.cursor._execute(changeDescSql, (name, description, id,))

    def remove_ability_actor(self, actor_id, ability_list):
        return None
        self.cursor._execute("DELETE FROM actors_to_abilities WHERE actor_id={}  AND ability_id IN ".format(actor_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def remove_ability_role(self, role_id, ability_list):
        return None
        self.cursor._execute("DELETE FROM roles_to_abilities WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_ability_actor(self, actor_id, ability_list):
        return None
        create_ability_actor_sql = "INSERT OR IGNORE INTO actors_to_abilities(actor_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor._execute(create_ability_actor_sql,(actor_id,ability_id,))

    def add_ability_role(self, role_id, ability_list):
        return None
        create_ability_role_sql = "INSERT OR IGNORE INTO roles_to_abilities(role_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor._execute(create_ability_role_sql,(role_id,ability_id,))

    def get_ability(self, ability_id):
        return None
        fetched_ability = self.select_where("*","abilities","id",ability_id)
        if len(fetched_ability) == 1:
            ability = fetched_ability[0]
            return Ability(*ability)

    def get_ability_list_role(self, role_id):
        return []
        ability_ids = self.select_where("ability_id", "roles_to_abilities", "role_id", role_id)
        abilities = []
        if len(ability_ids) >= 1:
            for id_tuple in ability_ids:
                abilities.append(self.get_ability(id_tuple[0]))
        return abilities

    def get_ability_list_actor(self, actor_id):
        return []
        ability_ids = self.select_where("ability_id", "actors_to_abilities", "actor_id", actor_id)
        abilities = []
        if len(ability_ids) == 1:
            for id in ability_ids[0]:
                abilities.append(self.get_ability(id))
        return abilities

    def get_ability_list_exclude_actor(self, actor_id):
        return []
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
        return []
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
        return []
        template_id_list = self.select_where("template_id", "roles_to_ability_templates", "role_id", role_id)
        
        ability_templates = []

        for template_id in template_id_list:
            ability_templates.append(self.get_ability_template(template_id[0]))

        return ability_templates

    def get_ability_template_list_exclude_role(self, role_id):
        return []
        template_id_list = self.select_where("template_id", "roles_to_ability_templates", "role_id", role_id)
        new_id_list = [temp_id[0] for temp_id in template_id_list]

        excluded_template_id_list = self.select_not_in("template_id", "ability_templates", "template_id", new_id_list)

        ability_templates = []

        for id in excluded_template_id_list:
            ability_templates.append(self.get_ability_template(id[0]))

        return ability_templates

    def get_abilities_template(self, template_id):
        return []
        fetched_ability_id_list = self.select_where("ability_id", "ability_templates_to_abilities", "template_id", template_id)
        new_id_list = [id[0] for id in fetched_ability_id_list]
        ability_list = []
        for ability_id in new_id_list:
            ability_list.append(self.get_ability(ability_id))
        return ability_list

    def get_ability_list_exclude_template(self, template_id):
        return []
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
        return None
        create_template_sql = "INSERT INTO ability_templates(template_name, template_description) VALUES (?,?)"
        self.cursor._execute(create_template_sql,(name,description))
        return self.cursor.lastrowid

    def remove_template(self, role_id, template_id_list):
        return None
        self.cursor._execute("DELETE FROM roles_to_ability_templates WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(template_id_list)), template_id_list)

    def add_template_role(self, role_id, template_id_list):
        return None
        add_template_sql = '''INSERT OR IGNORE INTO roles_to_ability_templates(role_id, template_id) VALUES (?,?)'''
        for template_id in template_id_list:
            self.cursor._execute(add_template_sql, (role_id, template_id))

    def get_ability_template(self, template_id):
        return None
        template = self.select_where("*", "ability_templates", "template_id", template_id)[0]
        return AbilityTemplate(*template, self)
        
    def remove_ability_from_template(self, template_id, ability_list):
        return None
        self.cursor._execute("DELETE FROM ability_templates_to_abilities WHERE template_id={} AND ability_id IN".format(template_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_abilities_to_template(self,template_id, ability_list):
        return None
        connect_template_ability_sql = "INSERT OR IGNORE INTO ability_templates_to_abilities(template_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor._execute(connect_template_ability_sql,(template_id,ability_id,))

    def create_template_history(self, template_id, new_name, new_description):
        return None
        old_template = self.get_ability_template(template_id)
        try:
            historySql = '''INSERT INTO ability_template_history(id, name, description) VALUES (?,?,?) '''
            self.cursor._execute(historySql, (old_template.id, old_template.name, old_template.description,))
        except IntegrityError:
            logging.exception()

        changeDescSql='''UPDATE ability_templates SET template_name=?, template_description=? WHERE template_id=?'''
        self.cursor._execute(changeDescSql, (new_name, new_description, template_id,))

    def get_template_history(self, template_id):
        return []
        revision_list = []
        history = self.select_where("*", "ability_template_history", "id", template_id)
        for revision in history:
            revision_list.append(TemplateHistory(*revision))
        return revision_list

    def get_all_abilities(self):
        return []
        fetched_abilities = self.select('*', 'abilities')
        abilities = []
        for ability in fetched_abilities:
            abilities.append(Ability(*ability))
        return abilities

    def get_ability_history(self, id):
        return []
        revision_list = []
        history = self.select_where("*", "abilities_history", "id", id)
        for revision in history:
            revision_list.append(AbilityHistory(*revision))
        return revision_list

    #RELEATIONSHIPS#
    def add_relationship_actor(self, actor1_id, actor1_name, actor2_id, actor2_name, relationship_type):
        add_relationship_neo = '''MATCH (a1:Actor {imdb_id:$actor1_id}), (a2:Actor {imdb_id:$actor2_id}}) CREATE (a1) - [$relationship_type] - (a2)'''
        add_relationship_parameters = {'actor1_id':actor1_id, 'actor2_id':actor2_id, 'relationship_type':relationship_type.upper()}
        self._execute(add_relationship_neo,add_relationship_parameters)

    def get_relationships_actor_by_actor_id(self, actor_id):
        relationships = []
        fetched_relationships = self._execute('''MATCH (a:Actor {imdb_id:$actor_id})-[]-(a2:Actor) RETURN a.imdb_id, a.name, a2.imdb_id, a2.name''', {'actor_id':actor_id})
        if len(fetched_relationships) != 0:
            for relationship in fetched_relationships:
                new_relationship = ActorRelationship(*relationship)
                new_relationship.set_link_actor(actor_id)
                relationships.append(new_relationship)
        else:
            logging.debug(f'No relationships for actor {actor_id}')
        return relationships

    def remove_relationships_actor(self, actor_id, relationship_id_list):
        for relationship_id in relationship_id_list:
            remove_relationship_neo = '''MATCH (a:Actor {imdb_id:$actor_id})-[rel:]-(Actor) WHERE rel.id IN $relationship_id_list DELETE rel'''
            remove_relationship_parameters = {'actor_id':actor_id, 'relationship_id_list':relationship_id_list}
            self._execute(remove_relationship_neo, remove_relationship_parameters)

    def add_relationship_role(self, role1_id, role1_name, role2_id, role2_name, relationship_type):
        add_relationship_neo = '''MATCH (r1:Role {role_id:$role1_id}), (r2:Role {role_id:$role2_id}}) CREATE (r1) - [:$relationship_type] - (r2)'''
        add_relationship_parameters = {'role1_id':role1_id, 'role1_id':role2_id, 'relationship_type':relationship_type.upper()}
        self._execute(add_relationship_neo,add_relationship_parameters)

    def get_relationships_role_by_role_id(self, role_id):
        relationships = []
        get_relationships_neo = '''MATCH (r:Role {role_id:$role_id}) - [rel] - (r2:Role) WHERE rel <> 'ACTOR_SWAP' RETURN r.role_id, r.name, r2.role_id, r2.name '''
        get_relationships_parameters = {'role_id':role_id}
        fetched_relationships = self._execute(get_relationships_neo,get_relationships_parameters)
        for relationship in fetched_relationships:
            relationships.append(RoleRelationship(*relationship, self))
        return relationships

    def remove_relationships_role(self, role_id, relationship_id_list):
        remove_relationship_neo = '''MATCH (r:Role {role_id:$role_id})-[rel:]-(Role) WHERE rel.id IN $relationship_id_list DELETE rel'''
        remove_relationship_parameters = {'role_id':role_id, 'relationship_id_list':relationship_id_list}
        self._execute(remove_relationship_neo, remove_relationship_parameters)