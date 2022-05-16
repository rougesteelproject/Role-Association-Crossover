from database_controller import DatabaseController

import constants

import sqlite3
from sqlite3.dbapi2 import IntegrityError
import traceback

class DatabaseControllerSQL(DatabaseController):
    def __init__(self):
        super().__init__(database_uri=constants.SQL_URI)
        self._sql_cursor = None

    #EXECUTION - SQL#

    def _create_connection(self):
        try:
            connection = sqlite3.connect(self._database_uri, check_same_thread=False)
            
            self._sql_cursor = connection.cursor()

            return connection
        except sqlite3.Error:
            traceback.print_exc()

    def execute(self, command, parameters):
        self._sql_cursor.execute(command, parameters)

    def commit(self):
        self._sql_connection.commit()

    def create_db_if_not_exists(self):
        # Create table if it doesn't exist
        self.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT \'Auto-Generated\', historical TEXT DEFAULT \'False\', religious TEXT DEFAULT \'False\', fictional_in_universe TEXT DEFAULT \'False\',is_biggest TEXT DEFAULT \'False\')''')
        #INTERGER PRIMARY KEY does auto-increment for you
        self.execute('''CREATE TABLE IF NOT EXISTS gallery(file NOT NULL, role TEXT, actor INT, caption TEXT DEFAULT \'Auto-Generated\')''')
        self.execute('''CREATE TABLE IF NOT EXISTS actors(id INT PRIMARY KEY, name TEXT NOT NULL, bio TEXT, birth_date TEXT, death_date TEXT,is_biggest TEXT DEFAULT \'False\')''')
        self.execute('''CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT \'-\', alive_or_dead TEXT DEFAULT \'-\', alignment TEXT DEFAULT \'-\',parent_actor INT, parent_meta INT, actor_swap_id INT DEFAULT 0, first_parent_meta INT )''')
        #relationships
        self.execute('''CREATE TABLE IF NOT EXISTS actor_relationships(relationship_id INTEGER PRIMARY KEY, actor1_id INT, actor1_name TEXT, actor2_id INT, actor2_name TEXT,relationship_type TEXT) ''')
        self.execute('''CREATE TABLE IF NOT EXISTS role_relationships(relationship_id INTEGER PRIMARY KEY, role1_id TEXT, role1_name TEXT ,role2_id TEXT, role2_name TEXT,relationship_type TEXT)''')
        #map role/actor to ability or template, ability to description
        #abilities include languages
        self.execute('''CREATE TABLE IF NOT EXISTS actors_to_abilities(actor_id INT, ability_id INT, UNIQUE(actor_id, ability_id))''')
        self.execute('''CREATE TABLE IF NOT EXISTS ability_templates_to_abilities(template_id INT, ability_id INT, UNIQUE(template_id,ability_id))''') #[species/power source: ability_id]
        self.execute('''CREATE TABLE IF NOT EXISTS ability_templates(template_id INTEGER PRIMARY KEY, template_name TEXT, template_description TEXT)''')
        self.execute('''CREATE TABLE IF NOT EXISTS roles_to_ability_templates(role_id TEXT, template_id TEXT, UNIQUE (role_id, template_id))''')
        self.execute('''CREATE TABLE IF NOT EXISTS roles_to_abilities(role_id TEXT, ability_id TEXT, UNIQUE (role_id, ability_id))''')
        self.execute('''CREATE TABLE IF NOT EXISTS abilities(id INTEGER PRIMARY KEY, name TEXT, description TEXT)''') #[krypt: strength (kyptonian): kryptonians can lift quintillion tons blah blah]
        #create history tables
        self.execute('''CREATE TABLE IF NOT EXISTS meta_roles_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, historical TEXT, religious TEXT, fictional_in_universe TEXT, UNIQUE(id, name, description, historical, religious, fictional_in_universe))''')
        self.execute('''CREATE TABLE IF NOT EXISTS roles_history(id TEXT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, alive_or_dead TEXT, alignment TEXT, UNIQUE (id, name, description, alive_or_dead, alignment))''')
        self.execute('''CREATE TABLE IF NOT EXISTS actors_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, bio TEXT, UNIQUE(id, name, bio))''')
        #history tables for abilities
        self.execute('''CREATE TABLE IF NOT EXISTS abilities_history(id INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT, description TEXT, UNIQUE(id, name, description))''')
        self.execute('''CREATE TABLE IF NOT EXISTS ability_template_history(id, INT NOT NULL, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, description TEXT, UNIQUE(id, name, description))''')

    #CREATE - SQL#

    def create_actor(self, id, name, bio, birth_date, death_date):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_actor_sql = '''INSERT OR IGNORE INTO actors(id, name, bio, birth_date, death_date) VALUES (?,?,?,?,?) '''
        self.execute(create_actor_sql, (id, name, bio, birth_date, death_date,))

    def create_role(self, role_id, role_name, actor_id, mr_id):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_role_sql = '''INSERT OR IGNORE INTO roles(id, name,parent_actor, parent_meta, first_parent_meta) VALUES (?,?,?,?,?) '''
        # Create table if it doesn't exist
        self.execute(create_role_sql, (role_id, role_name,actor_id, mr_id, role_id,))

    def create_mr(self,character_name, mr_id):
        create_mr_sql = '''INSERT INTO meta_roles(name, id) VALUES (?, ?) '''
        self.execute(create_mr_sql,(character_name, mr_id))



    #UPDATE#
    def update(self, table_name, column, column_value, where, where_value):
        update_sql = "UPDATE {} SET {}=? WHERE {}=?".format(table_name.lower(), column.lower(), where.lower())
        self.execute(update_sql, (column_value, where_value,))

    def update_or(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        update_sql = "UPDATE {} SET {}=? WHERE {}=? OR {}=?".format(table_name.lower(), column.lower(), where_1.lower(), where_2.lower())
        self.execute(update_sql, (column_value,where_value_1,where_value_2,))
    
    def update_and(self, table_name, column, column_value, where_1, where_value_1, where_2, where_value_2):
        update_sql = "UPDATE {} SET {}=? WHERE {}=? AND {}=?".format(table_name, column, where_1, where_2)
        self.execute(update_sql, (column_value, where_value_1, where_value_2,))

    def update_reset_mr(self, roleID1):
        update_reset_mr_sql = "UPDATE roles SET parent_meta=first_parent_meta WHERE id=?"
        self.execute(update_reset_mr_sql, (roleID1,))

    #SELECT#
    def select_where(self, select_columns, table_name, where, where_value):
        select_sql = "SELECT {} FROM {} WHERE {}=?".format(select_columns.lower(),table_name.lower(),where.lower())
        self.execute(select_sql, (where_value,))
        return self.cursor.fetchall()

    def select(self, select_columns, table_name):
        select_sql = "SELECT {} FROM {}".format(select_columns.lower(), table_name.lower())
        self.execute(select_sql)
        return self.cursor.fetchall()

    def select_and(self, select_columns, table_name, where_column, where_value, where_column_2, where_value_2):
        select_sql = "SELECT {} FROM {} WHERE {}=? AND {}=?".format(select_columns.lower(),table_name.lower(),where_column.lower(),where_column_2.lower())
        self.execute(select_sql,(where_value,where_value_2,))
        return self.cursor.fetchall()

    def select_or(self, select_columns, table_name, where_column, where_value, where_column_2, where_value_2):
        select_sql = "SELECT {} FROM {} WHERE {}=? OR {}=?".format(select_columns.lower(),table_name.lower(),where_column.lower(),where_column_2.lower())
        self.execute(select_sql,(where_value,where_value_2,))
        return self.cursor.fetchall()

    def select_max_where(self, select_column, table_name, where_column, where_value):
        select_sql = "SELECT MAX({}) FROM {} WHERE {}=?".format(select_column.lower(),table_name.lower(),where_column.lower())
        self.execute(select_sql, (where_value,))
        return self.cursor.fetchone()

    def select_like(self, select_columns, table_name, where_column, like_value):
        select_sql = "SELECT {} FROM {} WHERE {} LIKE \'%{}%\'".format(select_columns, table_name, where_column, like_value)
        self.execute(select_sql)
        return self.cursor.fetchall()

    def select_not_in(self, select_columns, table_name, where, ability_list):
        result_set = self.execute("SELECT {} FROM {} WHERE {} NOT IN ".format(select_columns.lower(),table_name.lower(),where.lower()) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)
        return result_set.fetchall()


    #IMAGES#
    def add_image(self,page_type, page_id, image_url, caption):
        if page_type == 'actor':
            sql = '''INSERT INTO gallery (file, actor, caption) VALUES (?,?,?)'''
        else:
            sql = '''INSERT INTO gallery (file, role, caption) VALUES (?,?,?)'''
        self.execute(sql,(image_url,page_id,caption,))
   
    #HISTORY#
    def create_actor_history(self, id, new_bio):
        old_actor = self.get_actor(id)
        historySql = '''INSERT INTO actors_history(id, name, bio) VALUES (?,?,?) '''
        self.execute(historySql,(id, old_actor.name, old_actor.bio))
        
        changeDescSql='''UPDATE actors SET bio=? WHERE id=?'''
        self.execute(changeDescSql,(new_bio,id,))

    def create_mr_history(self, id, new_description, historical, religious, fictional_in_universe):
        old_mr = self.get_mr(id)
        historySql = '''INSERT INTO meta_roles_history(id, name, description, historical, religious, fictional_in_universe) VALUES (?,?,?,?,?,?) '''
        self.execute(historySql,(id, old_mr.name, old_mr.description, old_mr.historical, old_mr.religious, old_mr.fictional_in_universe))
        changeDescSql='''UPDATE meta_roles SET description=?, historical=?, religious=?, fictional_in_universe=? WHERE id=?'''

        self.execute(changeDescSql,(new_description,historical, religious, fictional_in_universe,id,))

    def create_role_history(self, id, new_description, new_alive_or_dead, new_alignment):
        old_role = self.get_role(id)
        historySql = '''INSERT INTO roles_history(id, name, description, alive_or_dead, alignment) VALUES (?,?,?,?,?) '''
        self.execute(historySql,(id, old_role.name, old_role.description, old_role.alive_or_dead, old_role.alignment))
        changeDescSql='''UPDATE roles SET description=?, alive_or_dead=?,alignment=? WHERE id=?'''

        self.execute(changeDescSql,(new_description,new_alive_or_dead,new_alignment,id,))  

    #ABILITIES#
    def create_ability(self, name, description):
        create_sql = '''INSERT INTO abilities (name, description) VALUES (?,?)'''
        self.execute(create_sql, (name, description))
        return self.cursor.lastrowid

    def create_ability_history(self, id, name, description):
        old_ability = self.get_ability(id)
        try:
            historySql = '''INSERT INTO abilities_history(id, name, description) VALUES (?,?,?) '''
            self.execute(historySql, (old_ability.id, old_ability.name, old_ability.description,))
        except IntegrityError:
            print(traceback.print_exc())

        changeDescSql='''UPDATE abilities SET name=?, description=? WHERE id=?'''
        self.execute(changeDescSql, (name, description, id,))

    def remove_ability_actor(self, actor_id, ability_list):
        self.execute("DELETE FROM actors_to_abilities WHERE actor_id={}  AND ability_id IN ".format(actor_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def remove_ability_role(self, role_id, ability_list):
        self.execute("DELETE FROM roles_to_abilities WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_ability_actor(self, actor_id, ability_list):
        create_ability_actor_sql = "INSERT OR IGNORE INTO actors_to_abilities(actor_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.execute(create_ability_actor_sql,(actor_id,ability_id,))

    def add_ability_role(self, role_id, ability_list):
        create_ability_role_sql = "INSERT OR IGNORE INTO roles_to_abilities(role_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.execute(create_ability_role_sql,(role_id,ability_id,))

    def create_ability_template(self, name, description):
        create_template_sql = "INSERT INTO ability_templates(template_name, template_description) VALUES (?,?)"
        self.execute(create_template_sql,(name,description))
        return self.cursor.lastrowid

    def remove_template(self, role_id, template_id_list):
        self.execute("DELETE FROM roles_to_ability_templates WHERE role_id={}  AND ability_id IN ".format(role_id) + '(%s)' % ','.join('?'*len(template_id_list)), template_id_list)

    def add_template_role(self, role_id, template_id_list):
        add_template_sql = '''INSERT OR IGNORE INTO roles_to_ability_templates(role_id, template_id) VALUES (?,?)'''
        for template_id in template_id_list:
            self.execute(add_template_sql, (role_id, template_id))
        
    def remove_ability_from_template(self, template_id, ability_list):
        self.execute("DELETE FROM ability_templates_to_abilities WHERE template_id={} AND ability_id IN".format(template_id) + '(%s)' % ','.join('?'*len(ability_list)), ability_list)

    def add_abilities_to_template(self,template_id, ability_list):
        connect_template_ability_sql = "INSERT OR IGNORE INTO ability_templates_to_abilities(template_id,ability_id) VALUES (?,?)"
        for ability_id in ability_list:
            self.execute(connect_template_ability_sql,(template_id,ability_id,))

    def create_template_history(self, template_id, new_name, new_description):
        old_template = self.get_ability_template(template_id)
        try:
            historySql = '''INSERT INTO ability_template_history(id, name, description) VALUES (?,?,?) '''
            self.execute(historySql, (old_template.id, old_template.name, old_template.description,))
        except IntegrityError:
            print(traceback.print_exc())

        changeDescSql='''UPDATE ability_templates SET template_name=?, template_description=? WHERE template_id=?'''
        self.execute(changeDescSql, (new_name, new_description, template_id,))

    #RELEATIONSHIPS#
    def add_relationship_actor(self, actor1_id, actor1_name, actor2_id, actor2_name, relationship_type):
        sql = '''INSERT INTO actor_relationships(actor1_id, actor1_name, actor2_id, actor2_name, relationship_type) VALUES (?,?,?,?,?)'''
        self.execute(sql, (actor1_id, actor1_name, actor2_id, actor2_name, relationship_type))

    def remove_relationships_actor(self, relationship_id_list):
        for relationship_id in relationship_id_list:
            delete_sql ='''DELETE FROM actor_relationships WHERE relationship_id={}'''.format(relationship_id)
            self.execute(delete_sql)

    def add_relationship_role(self, role1_id, role1_name, role2_id, role2_name, relationship_type):
        sql = '''INSERT INTO role_relationships(role1_id, role1_name, role2_id, role2_name, relationship_type) VALUES (?,?,?,?,?)'''
        self.execute(sql, (role1_id, role1_name, role2_id, role2_name, relationship_type))

    def remove_relationships_role(self, relationship_id_list):
        for relationship_id in relationship_id_list:
            delete_sql ='''DELETE FROM role_relationships WHERE relationship_id={}'''.format(relationship_id)
            self.execute(delete_sql)
