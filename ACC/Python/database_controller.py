from ACC.Python.meta_role import MetaRole
from ACC.Python.actor import Actor
from role import Role
import constants
import sqlite3  
import traceback

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
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT, historical_religious INT,is_biggest INT )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gallery(file NOT NULL, role INT, actor INT, caption TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, bio TEXT, birth_date TEXT, death_date TEXT,is_biggest INT )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT, alive_or_dead TEXT, alignment TEXT, fictional_in_universe INT,parent_actor INT, parent_meta INT, actor_swap_id INT, first_parent_meta INT )''')
        #relationships
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actor_relationships(relationship_id INT PRIMARY KEY NOT NULL, actor1 TEXT, actor2 TEXT, relationship_type TEXT) ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS role_relationships(relationship_id INT PRIMARY KEY NOT NULL, role_1 TEXT, role_2 TEXT, relationship_type TEXT)''')
        #map role/actor to ability or template, ability to description
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actor_abilities(ability_id INT PRIMARY KEY NOT NULL, actor_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ability_templates(template_id INT PRIMARY KEY NOT NULL, template_name TEXT, ability_id TEXT)''') #[species/power source: ability_id]
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS role_ability_templates(role_id TEXT PRIMARY KEY NOT NULL, template_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS role_abilities(role_id TEXT PRIMARY KEY NOT NULL, ability_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities(ability_id INT PRIMARY KEY NOT NULL, name TEXT, description, TEXT)''') #[krypt: strength (kyptonian): kryptonians can lift quintillion tons blah blah]
        #create history table and pending changes
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meta_roles_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS roles_history(id TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, alive_or_dead TEXT, alignment TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS actors_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, bio TEXT, death_date TEXT)''')
        #history tables for abilities
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abilities_history(ability_id INT PRIMARY KEY NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT, description TEXT)''')

    def create_actor(self, db_actor):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_actor_sql = '''INSERT OR IGNORE INTO actors(id, name, bio, birth_date, death_date,is_biggest) VALUES (?,?,?,?,?,?) '''
        self.cursor.execute(create_actor_sql, db_actor)

    #create a new role in the role table
    def create_role(self,db_role):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_role_sql = '''INSERT OR IGNORE INTO roles(id, name, description, alive_or_dead, alignment, fictional_in_universe,parent_actor, parent_meta, actor_swap_id, first_parent_meta) VALUES (?,?,?,?,?,?,?,?,?,?) '''
        # Create table if it doesn't exist
        self.cursor.execute(create_role_sql, db_role)

    def create_mr(self, mr_id, character_name, mr_description, is_biggest=0):
        create_mr_sql = '''INSERT OR IGNORE INTO meta_roles(id, name, description, historical_religious, is_biggest) VALUES (?,?,?,?,?) '''
        self.cursor.execute(create_mr_sql,(mr_id, character_name, mr_description, is_biggest,))

    def update(self, table_name, column, column_values, where, where_values):
        update_sql = "UPDATE {} SET {}=? WHERE {}=?".format(table_name.lower(), column.lower(), where.lower())
        self.cursor.execute(update_sql, column_values + where_values)
    
    def update_reset_mr(self, roleID1):
        update_reset_mr_sql = "UPDATE roles SET parent_meta=first_parent_meta WHERE id=?"
        self.cursor.execute(update_reset_mr_sql, (roleID1,))

    def select(self, select_columns, table_name, where, where_value , bool_and = False, bool_or = False, second_argument_column = "", second_argument_value = ""):
        select_sql = "SELECT {} FROM {} WHERE {}=?".format(select_columns.lower(),table_name.lower(),where.lower())
        if bool_and:
            select_sql = select_sql + "AND {}=?".format(second_argument_column.lower())
        elif bool_or:
            select_sql = select_sql + "OR {}=?".format(second_argument_column.lower())
        
        if second_argument_value != '':
            values = (where_value, second_argument_value,)
            self.cursor.execute(select_sql, values)
        else:
            values = where_value
            self.cursor.execute(select_sql, (values,))
        return self.cursor.fetchall()

    def select_max(self, select_column, table_name, where_column, where_value):
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
        fetched_actor = self.select("*","actors","id",actor_id)
        return Actor(*fetched_actor, self)

    def get_mr(self, mr_id):
        fetched_mr = self.select("*","meta_roles", "id",mr_id)
        return MetaRole(*fetched_mr, self)

    def get_roles(self, parent_id, is_actor):
        roles = []
        if is_actor:
            fetched_roles = self.select("*", "roles", "parent_actor", parent_id)
        else:
            fetched_roles = self.select("*","roles","parent_meta",parent_id)
        for role in fetched_roles:
            roles.append(Role(*role, self))
        return roles
        

    def commit(self):
        self.connection.commit()