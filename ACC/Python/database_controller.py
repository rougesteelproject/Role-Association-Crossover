import sqlite3
import traceback

import constants
from actor import Actor
from meta_role import MetaRole
from role import Role
from meta_role_history import MetaRoleHistory
from actor_history import ActorHistory
from role_history import RoleHistory
from ability import Ability

#TODO use Auto_Increment to simplify ids

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
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT DEFAULT \'Auto-Generated\', historical TEXT DEFAULT \'False\', religious TEXT DEFAULT \'False\', fictional_in_universe TEXT DEFAULT \'False\',is_biggest TEXT DEFAULT \'False\')''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gallery(file NOT NULL, role INT, actor INT, caption TEXT DEFAULT \'Auto-Generated\')''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, bio TEXT, birth_date TEXT, death_date TEXT,is_biggest TEXT DEFAULT \'False\')''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT DEFAULT \'-\', alive_or_dead TEXT DEFAULT \'-\', alignment TEXT DEFAULT \'-\',parent_actor INT, parent_meta INT, actor_swap_id INT DEFAULT 0, first_parent_meta INT )''')
        #relationships
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actor_relationships(relationship_id INT PRIMARY KEY NOT NULL, actor1 TEXT, actor2 TEXT, relationship_type TEXT) ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS role_relationships(relationship_id INT PRIMARY KEY NOT NULL, role_1 TEXT, role_2 TEXT, relationship_type TEXT)''')
        #map role/actor to ability or template, ability to description
        #abilities include languages
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors_to_abilities(actor_id INT PRIMARY KEY NOT NULL, ability_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ability_templates(template_id INT PRIMARY KEY NOT NULL, template_name TEXT, ability_id TEXT)''') #[species/power source: ability_id]
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_to_ability_templates(role_id TEXT PRIMARY KEY NOT NULL, template_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_to_abilities(role_id TEXT PRIMARY KEY NOT NULL, ability_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities(id INT PRIMARY KEY NOT NULL, name TEXT, description TEXT)''') #[krypt: strength (kyptonian): kryptonians can lift quintillion tons blah blah]
        #create history tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, historical TEXT, religious TEXT, fictional_in_universe TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_history(id TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, alive_or_dead TEXT, alignment TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, bio TEXT)''')
        #history tables for abilities
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities_history(id INT PRIMARY KEY NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT, description TEXT)''')

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

    def create_mr(self, mr_id, character_name):      
        create_mr_sql = '''INSERT OR IGNORE INTO meta_roles(id, name) VALUES (?,?) '''
        self.cursor.execute(create_mr_sql,(mr_id, character_name,))

    #UPDATE#
    def update(self, table_name, column, column_value, where, where_value):
        update_sql = "UPDATE {} SET {}=? WHERE {}=?".format(table_name.lower(), column.lower(), where.lower())
        self.cursor.execute(update_sql, (column_value, where_value,))

    def update_or(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        update_sql = "UPDATE {} SET {}=? WHERE {}=? OR {}=?".format(table_name.lower(), column.lower(), where_1.lower(), where_2.lower())
        self.cursor.execute(update_sql, (column_value,where_value_1,where_value_2,))
    
    def update_reset_mr(self, roleID1):
        update_reset_mr_sql = "UPDATE roles SET parent_meta=first_parent_meta WHERE id=?"
        self.cursor.execute(update_reset_mr_sql, (roleID1,))

    #SELECT#
    def select(self, select_columns, table_name, where, where_value):
        select_sql = "SELECT {} FROM {} WHERE {}=?".format(select_columns.lower(),table_name.lower(),where.lower())
        self.cursor.execute(select_sql, (where_value,))
        return self.cursor.fetchall()

    def select_all(self, select_columns, table_name):
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

    def select_max(self, select_column, table_name):
        select_sql = "SELECT MAX({}) FROM {}".format(select_column.lower(),table_name.lower())
        self.cursor.execute(select_sql)
        return self.cursor.fetchone()[0]

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


    #SEARCH AND RETRIEVE#
    def get_actor(self, actor_id):
        fetched_actor = self.select("*","actors","id",actor_id)[0]
        actor = Actor(*fetched_actor, self)
        actor.set_abilities(self.get_ability_list_actor(actor_id))
        return actor

    def get_actors_search(self, query):
        actors = []
        fetched_actors = self.select_like("*","actors","name", query)
        for actor in fetched_actors:
            actors.apppend(Actor(*actor, self))
        return actors

    def get_mr(self, mr_id):
        fetched_mr = self.select("*","meta_roles", "id",mr_id)[0]
        return MetaRole(*fetched_mr, self)

    def get_mrs_search(self,query):
        mrs = []
        fetched_mrs = self.select_like("*","meta_roles","name",query)
        for mr in fetched_mrs:
            mrs.append(MetaRole(*mr, self))
        return mrs

    def get_role(self, role_id):
        fetched_role = self.select("*","roles","id",role_id)
        return Role(*fetched_role, self)

    def get_roles(self, parent_id, is_actor):
        roles = []
        if is_actor:
            fetched_roles = self.select("*", "roles", "parent_actor", parent_id)
        else:
            fetched_roles = self.select("*","roles","parent_meta",parent_id)
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles

    def get_roles_search(self, query):
        roles = []
        fetched_roles = self.select_like("*","roles","name",query)
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles
        
    def get_roles_swap(self, mr_id, actor_swap_id):
        roles = []
        fetched_roles = self.select("*","roles","parent_meta",mr_id,bool_and=True, second_argument_column="actor_swap", second_argument_value=actor_swap_id)
        for role in fetched_roles:
            roles.append(Role(*role,self))
        return roles

    def get_ability(self, ability_id):
        ability = self.select("*","abilities","id",ability_id)[0]
        return Ability(*ability)

    def get_ability_list_role(self, role_id):
        pass

    def get_ability_list_actor(self, actor_id):
        ability_ids = self.select("ability_id", "actors_to_abilities", "actor_id", actor_id)
        abilities = []
        if len(ability_ids) == 1:
            for id in ability_ids[0]:
                abilities.append(self.get_ability(id))
        return abilities

    def get_ability_list_exclude_actor(self, actor_id):
        ability_ids = self.select("ability_id", "actors_to_abilities", "actor_id", actor_id)
        
        abilities_that_are_not_connected = []

        if len(ability_ids) == 1:
            db_abilites = self.select_not_in("*","abilities","id", ability_ids[0])

        else:
            db_abilites = self.get_all_abilities()
            
        for ability in db_abilites:
            abilities_that_are_not_connected.append(Ability(*ability))
        return abilities_that_are_not_connected

    def get_ability_list_exclude_role(self, role_id):
        pass

    def get_ability_template_list_exclude_actor(self, actor_id):
        pass

    def get_ability_template_list_exclude_role(self, role_id):
        pass

    def get_all_abilities(self):
        abilities = self.select_all('*', 'abilities')
        return abilities

    def get_parent_meta(self, role_id):
        pass #TODO

    #HISTORY#
    def get_actor_history(self,id):
        revision_list = []
        history = self.select("*", "actors_history", "id", id)
        for revision in history:
            revision_list.append(ActorHistory(*revision))
        return revision_list

    def get_mr_history(self, id):
        revision_list = []
        history = self.select("*", "meta_roles_history", "id", id)
        for revision in history:
            revision_list.append(MetaRoleHistory(*revision))
        return revision_list

    def get_role_history(self,id):
        revision_list = []
        history = self.select("*", "roles_history", "id", id)
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
        #TODO check here to see if a change is identical to the current
        changeDescSql='''UPDATE meta_roles SET description=?, historical=?, religious=?, fictional_in_universe=? WHERE id=?'''

        self.cursor.execute(changeDescSql,(new_description,historical, religious, fictional_in_universe,id,))

    def create_role_history(self, id, new_description, new_alive_or_dead, new_alignment):
        old_role = self.get_role(id)
        historySql = '''INSERT INTO roles_history(id, name, description, alive_or_dead, alignment) VALUES (?,?,?,?,?) '''
        self.cursor.execute(historySql,(id, old_role.name, old_role.description, old_role.alive_or_dead, old_role.alignment))
        #TODO check here to see if a change is identical to the current
        changeDescSql='''UPDATE roles SET description=?, alive_or_dead=?,alignment=? WHERE id=?'''

        self.cursor.execute(changeDescSql,(new_description,new_alive_or_dead,new_alignment,id,))  

    def get_ability_history(id):
        #TODO
        return ability_history

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
            
            swap_id = self.select_max_where("actor_swap_id", "roles","parent_meta", parent_meta)[0]
            if swap_id is not None:
                swap_id += 1
            else:
                swap_id = 1
            #Select Max() gets the highest in that column
            self.update_or("roles", "actor_swap_id", swap_id, "id", roleID1, where_2="id", where_value_2=roleID2)
        else:
            print("Actor Swap Error: IDs are the same.")
        
    def removeActorSwap(self, roleID1, parent_id_1):
        actor_swap_data = self.select("actor_swap_id, parent_meta", "roles", "id", roleID1)
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

    #ABILITY DISCONNECTOR#
    def remove_ability_actor(self, actor_id, ability_list):
        self.cursor.execute("DELETE FROM actors_to_abilities WHERE actor_id={}  AND ability_id IN ".format(actor_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_ability_actor(self, actor_id, ability_list):
        create_ability_actor_sql = "INSERT OR IGNORE INTO actors_to_abilities(actor_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.cursor.execute(create_ability_actor_sql,(actor_id,ability_id,))

    def commit(self):
        self.connection.commit()
