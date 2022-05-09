import sqlite3
from sqlite3.dbapi2 import IntegrityError
import traceback

import constants
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
    def __init__(self):
        self._database = constants.DATABASE
        self.connection = None
        self.cursor = None

    def create_connection(self):
        try:
            self.connection = sqlite3.connect(self._database, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except sqlite3.Error:
            traceback.print_exc()

    #TODO each select returns a list of tuples. Check that the data is procesed at the right layer.

    def create_db_if_not_exists(self):
        # Create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT \'Auto-Generated\', historical TEXT DEFAULT \'False\', religious TEXT DEFAULT \'False\', fictional_in_universe TEXT DEFAULT \'False\',is_biggest TEXT DEFAULT \'False\')''')
        #INTERGER PRIMARY KEY does auto-increment for you
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gallery(file NOT NULL, role TEXT, actor INT, caption TEXT DEFAULT \'Auto-Generated\')''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors(id INT PRIMARY KEY, name TEXT NOT NULL, bio TEXT, birth_date TEXT, death_date TEXT,is_biggest TEXT DEFAULT \'False\')''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT \'-\', alive_or_dead TEXT DEFAULT \'-\', alignment TEXT DEFAULT \'-\',parent_actor INT, parent_meta INT, actor_swap_id INT DEFAULT 0, first_parent_meta INT )''')
        #relationships
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actor_relationships(relationship_id INTEGER PRIMARY KEY, actor1_id INT, actor1_name TEXT, actor2_id INT, actor2_name TEXT,relationship_type TEXT) ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS role_relationships(relationship_id INTEGER PRIMARY KEY, role1_id TEXT, role1_name TEXT ,role2_id TEXT, role2_name TEXT,relationship_type TEXT)''')
        #map role/actor to ability or template, ability to description
        #abilities include languages
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors_to_abilities(actor_id INT, ability_id INT, UNIQUE(actor_id, ability_id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ability_templates_to_abilities(template_id INT, ability_id INT, UNIQUE(template_id,ability_id))''') #[species/power source: ability_id]
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ability_templates(template_id INTEGER PRIMARY KEY, template_name TEXT, template_description TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_to_ability_templates(role_id TEXT, template_id TEXT, UNIQUE (role_id, template_id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_to_abilities(role_id TEXT, ability_id TEXT, UNIQUE (role_id, ability_id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities(id INTEGER PRIMARY KEY, name TEXT, description TEXT)''') #[krypt: strength (kyptonian): kryptonians can lift quintillion tons blah blah]
        #create history tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, historical TEXT, religious TEXT, fictional_in_universe TEXT, UNIQUE(id, name, description, historical, religious, fictional_in_universe))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_history(id TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, alive_or_dead TEXT, alignment TEXT, UNIQUE (id, name, description, alive_or_dead, alignment))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, bio TEXT, UNIQUE(id, name, bio))''')
        #history tables for abilities
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT, description TEXT, UNIQUE(id, name, description))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ability_template_history(id, INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, UNIQUE(id, name, description))''')

    #INSERT OR IGNORE#
    def create_actor(self, id, name, bio, birth_date, death_date):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_actor_sql = '''INSERT OR IGNORE INTO actors(id, name, bio, birth_date, death_date) VALUES (?,?,?,?,?) '''
        self.cursor.execute(create_actor_sql, (id, name, bio, birth_date, death_date,))

    def create_role(self,role_id, role_name, actor_id, mr_id):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_role_sql = '''INSERT OR IGNORE INTO roles(id, name,parent_actor, parent_meta, first_parent_meta) VALUES (?,?,?,?,?) '''
        # Create table if it doesn't exist
        self.cursor.execute(create_role_sql, (role_id, role_name,actor_id, mr_id, mr_id,))

    def create_mr_and_return_id(self, character_name):      
        create_mr_sql = '''INSERT INTO meta_roles(name) VALUES (?) '''
        self.cursor.execute(create_mr_sql,(character_name,))
        return self.cursor.lastrowid

    def create_role_and_first_mr(self,character_name, role_id, role_name, actor_id):
        mr_id = self.create_mr_and_return_id(character_name)
        self.create_role(role_id, role_name, actor_id, mr_id)

    #UPDATE#
    def update(self, table_name, column, column_value, where, where_value):
        update_sql = "UPDATE {} SET {}=? WHERE {}=?".format(table_name.lower(), column.lower(), where.lower())
        self.cursor.execute(update_sql, (column_value, where_value,))

    def update_or(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        update_sql = "UPDATE {} SET {}=? WHERE {}=? OR {}=?".format(table_name.lower(), column.lower(), where_1.lower(), where_2.lower())
        self.cursor.execute(update_sql, (column_value,where_value_1,where_value_2,))
    
    def update_and(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        update_sql = "UPDATE {} SET {}=? WHERE {}=? AND {}=?".format(table_name, column, where_1, where_2)
        self.cursor.execute(update_sql, (column_value, where_value_1, where_value_2,))

    def update_reset_mr(self, roleID1):
        update_reset_mr_sql = "UPDATE roles SET parent_meta=first_parent_meta WHERE id=?"
        self.cursor.execute(update_reset_mr_sql, (roleID1,))

    #SELECT#
    def select_where(self, select_columns, table_name, where, where_value):
        select_sql = "SELECT {} FROM {} WHERE {}=?".format(select_columns.lower(),table_name.lower(),where.lower())
        self.cursor.execute(select_sql, (where_value,))
        return self.cursor.fetchall()

    def select(self, select_columns, table_name):
        select_sql = "SELECT {} FROM {}".format(select_columns.lower(), table_name.lower())
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()

    def select_and(self, select_columns, table_name, where_column, where_value, where_column_2, where_value_2):
        select_sql = "SELECT {} FROM {} WHERE {}=? AND {}=?".format(select_columns.lower(),table_name.lower(),where_column.lower(),where_column_2.lower())
        self.cursor.execute(select_sql,(where_value,where_value_2,))
        return self.cursor.fetchall()

    def select_or(self, select_columns, table_name, where_column, where_value, where_column_2, where_value_2):
        select_sql = "SELECT {} FROM {} WHERE {}=? OR {}=?".format(select_columns.lower(),table_name.lower(),where_column.lower(),where_column_2.lower())
        self.cursor.execute(select_sql,(where_value,where_value_2,))
        return self.cursor.fetchall()

    def select_max_where(self, select_column, table_name, where_column, where_value):
        select_sql = "SELECT MAX({}) FROM {} WHERE {}=?".format(select_column.lower(),table_name.lower(),where_column.lower())
        self.cursor.execute(select_sql, (where_value,))
        return self.cursor.fetchone()

    def select_like(self, select_columns, table_name, where_column, like_value):
        select_sql = "SELECT {} FROM {} WHERE {} LIKE \'%{}%\'".format(select_columns, table_name, where_column, like_value)
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()

    def select_not_in(self, select_columns, table_name, where, ability_list):
        result_set = self.cursor.execute("SELECT {} FROM {} WHERE {} NOT IN ".format(select_columns.lower(),table_name.lower(),where.lower()) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)
        return result_set.fetchall()


    #IMAGES#
    def add_image(self,page_type, page_id, image_url, caption):
        if page_type == 'actor':
            sql = '''INSERT INTO gallery (file, actor, caption) VALUES (?,?,?)'''
        else:
            sql = '''INSERT INTO gallery (file, role, caption) VALUES (?,?,?)'''
        self.cursor.execute(sql,(image_url,page_id,caption,))

    def get_images_actor(self, actor_id):
        fetched_images = self.select_where("file, caption", "gallery", "actor", actor_id)
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    def get_images_role(self, role_id):
        fetched_images = self.select_where("file, caption", "gallery", "role", role_id)
        gallery = []
        for image in fetched_images:
            gallery.append(Image(*image))
        return gallery

    #GET#
    #TODO may search in bios or descriptions?

    def get_actor(self, actor_id):
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
        create_sql = '''INSERT INTO abilities (name, description) VALUES (?,?)'''
        self.cursor.execute(create_sql, (name, description))
        return self.cursor.lastrowid

    def create_ability_history(self, id, name, description):
        old_ability = self.get_ability(id)
        try:
            historySql = '''INSERT INTO abilities_history(id, name, description) VALUES (?,?,?) '''
            self.cursor.execute(historySql, (old_ability.id, old_ability.name, old_ability.description,))
        except IntegrityError:
            print(traceback.print_exc())

        changeDescSql='''UPDATE abilities SET name=?, description=? WHERE id=?'''
        self.cursor.execute(changeDescSql, (name, description, id,))

    def remove_ability_actor(self, actor_id, ability_list):
        self.cursor.execute("DELETE FROM actors_to_abilities WHERE actor_id={}  AND ability_id IN ".format(actor_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def remove_ability_role(self, role_id, ability_list):
        self.cursor.execute("DELETE FROM roles_to_abilities WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_ability_actor(self, actor_id, ability_list):
        create_ability_actor_sql = "INSERT OR IGNORE INTO actors_to_abilities(actor_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(create_ability_actor_sql,(actor_id,ability_id,))

    def add_ability_role(self, role_id, ability_list):
        create_ability_role_sql = "INSERT OR IGNORE INTO roles_to_abilities(role_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(create_ability_role_sql,(role_id,ability_id,))

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
        create_template_sql = "INSERT INTO ability_templates(template_name, template_description) VALUES (?,?)"
        self.cursor.execute(create_template_sql,(name,description))
        return self.cursor.lastrowid

    def remove_template(self, role_id, template_id_list):
        self.cursor.execute("DELETE FROM roles_to_ability_templates WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(template_id_list)), template_id_list)

    def add_template_role(self, role_id, template_id_list):
        add_template_sql = '''INSERT OR IGNORE INTO roles_to_ability_templates(role_id, template_id) VALUES (?,?)'''
        for template_id in template_id_list:
            self.cursor.execute(add_template_sql, (role_id, template_id))

    def get_ability_template(self, template_id):
        template = self.select_where("*", "ability_templates", "template_id", template_id)[0]
        return AbilityTemplate(*template, self)
        
    def remove_ability_from_template(self, template_id, ability_list):
        self.cursor.execute("DELETE FROM ability_templates_to_abilities WHERE template_id={} AND ability_id IN".format(template_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_abilities_to_template(self,template_id, ability_list):
        connect_template_ability_sql = "INSERT OR IGNORE INTO ability_templates_to_abilities(template_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(connect_template_ability_sql,(template_id,ability_id,))

    def create_template_history(self, template_id, new_name, new_description):
        old_template = self.get_ability_template(template_id)
        try:
            historySql = '''INSERT INTO ability_template_history(id, name, description) VALUES (?,?,?) '''
            self.cursor.execute(historySql, (old_template.id, old_template.name, old_template.description,))
        except IntegrityError:
            print(traceback.print_exc())

        changeDescSql='''UPDATE ability_templates SET template_name=?, template_description=? WHERE template_id=?'''
        self.cursor.execute(changeDescSql, (new_name, new_description, template_id,))

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
        sql = '''INSERT INTO actor_relationships(actor1_id, actor1_name, actor2_id, actor2_name, relationship_type) VALUES (?,?,?,?,?)'''
        self.cursor.execute(sql, (actor1_id, actor1_name, actor2_id, actor2_name, relationship_type))

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
        for relationship_id in relationship_id_list:
            delete_sql ='''DELETE FROM actor_relationships WHERE relationship_id={}'''.format(relationship_id)
            self.cursor.execute(delete_sql)

    def add_relationship_role(self, role1_id, role1_name, role2_id, role2_name, relationship_type):
        sql = '''INSERT INTO role_relationships(role1_id, role1_name, role2_id, role2_name, relationship_type) VALUES (?,?,?,?,?)'''
        self.cursor.execute(sql, (role1_id, role1_name, role2_id, role2_name, relationship_type))

    def get_relationships_role_by_role_id(self, role_id):
        relationships = []
        fetched_relationships = self.select_or("*", "role_relationships", "role1_id", role_id, "role2_id", role_id)
        for relationship in fetched_relationships:
            relationships.append(RoleRelationship(*relationship, self))
        return relationships

    def remove_relationships_role(self, relationship_id_list):
        for relationship_id in relationship_id_list:
            delete_sql ='''DELETE FROM role_relationships WHERE relationship_id={}'''.format(relationship_id)
            self.cursor.execute(delete_sql)

    def commit(self):
        self.connection.commit()
