import sqlite3
import traceback

import constants
from actor import Actor
from meta_role import MetaRole
from role import Role
from meta_role_history import MetaRoleHistory
from actor_history import ActorHistory
from role_history import RoleHistory


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
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT DEFAULT \'Auto-Generated\', historical TEXT DEFAULT \'False\', religious TEXT DEFAULT \'False\', fictional_in_universe TEXT DEFAULT \'False\',is_biggest INT DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gallery(file NOT NULL, role INT, actor INT, caption TEXT DEFAULT \'Auto-Generated\')''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, bio TEXT DEFAULT \'Auto-Generated\', birth_date TEXT, death_date TEXT,is_biggest INT DEFAULT 0)''')
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
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities(ability_id INT PRIMARY KEY NOT NULL, name TEXT, description, TEXT)''') #[krypt: strength (kyptonian): kryptonians can lift quintillion tons blah blah]
        #create history tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, historical TEXT, religious TEXT, fictional_in_universe TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_history(id TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, alive_or_dead TEXT, alignment TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, bio TEXT)''')
        #history tables for abilities
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities_history(ability_id INT PRIMARY KEY NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT, description TEXT)''')

    def create_actor(self, id, name, birth_date, death_date):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_actor_sql = '''INSERT OR IGNORE INTO actors(id, name, birth_date, death_date) VALUES (?,?,?,?) '''
        self.cursor.execute(create_actor_sql, (id, name, birth_date, death_date,))

    #create a new role in the role table
    def create_role(self,role_id, role_name, actor_id, mr_id):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_role_sql = '''INSERT OR IGNORE INTO roles(id, name,parent_actor, parent_meta, first_parent_meta) VALUES (?,?,?,?,?) '''
        # Create table if it doesn't exist
        self.cursor.execute(create_role_sql, (role_id, role_name,actor_id, mr_id, mr_id,))

    def create_mr(self, mr_id, character_name):      
        create_mr_sql = '''INSERT OR IGNORE INTO meta_roles(id, name) VALUES (?,?) '''
        self.cursor.execute(create_mr_sql,(mr_id, character_name,))

    def update(self, table_name, column, column_values, where, where_values):
        update_sql = "UPDATE {} SET {}=? WHERE {}=?".format(table_name.lower(), column.lower(), where.lower())
        self.cursor.execute(update_sql, column_values + where_values)
    
    def update_reset_mr(self, roleID1):
        update_reset_mr_sql = "UPDATE roles SET parent_meta=first_parent_meta WHERE id=?"
        self.cursor.execute(update_reset_mr_sql, (roleID1,))

    def select(self, select_columns, table_name, where, where_value):
        select_sql = "SELECT {} FROM {} WHERE {}=?".format(select_columns.lower(),table_name.lower(),where.lower())
        self.cursor.execute(select_sql, (where_value,))
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
        return self.cursor.fetchone()

    def select_max_where(self, select_column, table_name, where_column, where_value):
        select_sql = "SELECT MAX({}) FROM {} WHERE {}=?".format(select_column.lower(),table_name.lower(),where_column.lower())
        self.cursor.execute(select_sql, (where_value,))
        return self.cursor.fetchone()

    def select_like(self, select_colums, table_name, where_column, like_value):
        select_sql = "SELECT {} FROM {} WHERE {} LIKE {}".format(select_colums, table_name, where_column, like_value)
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()

    def add_image(self,page_type, page_id, image_url, caption):
        if page_type == 'actor':
            sql = '''INSERT INTO gallery (file, actor, caption) VALUES (?,?,?)'''
        else:
            sql = '''INSERT INTO gallery (file, role, caption) VALUES (?,?,?)'''
        self.cursor.execute(sql,(image_url,page_id,caption,))

    def get_actor(self, actor_id):
        fetched_actor = self.select("*","actors","id",actor_id)[0]
        return Actor(*fetched_actor, self)

    def get_actors_search(self, query):
        actors = []
        fetched_actors = self.select_like("*","actors","name", query)
        for actor in fetched_actors:
            actors.apppend(Actor(*actor, self))
        return actors

    def get_mr(self, mr_id):
        fetched_mr = self.select("*","meta_roles", "id",mr_id)
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

    #TODO split
    def get_history(self, id, type):
        revision_list = []
        if type== 'actor':
            history = self.select("*", "actors_history", "id", id)
            for revision in history:
                revision_list.append(ActorHistory(*revision))
        elif type == 'role':
            history = self.select("*", "roles_history", "id", id)
            for revision in history:
                revision_list.append(RoleHistory(*revision))
        elif type == 'mr':
            history = self.select("*", "meta_roles_history", "id", id)
            for revision in history:
                revision_list.append(MetaRoleHistory(*revision))
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

    def get_ability(ability_id):
        #TODO
        return ability

    def get_ability_history(id):
        #TODO
        return ability_history

    def commit(self):
        self.connection.commit()
