from uuid import uuid4
from Python.db_controllers.database_controller import DatabaseController
import constants
from neo4j import GraphDatabase
import traceback

class DatabaseControllerNeo(DatabaseController):
    def __init__(self, database_uri = constants.NEO_URI):
        super().__init__()

#TODO roles can't be relationships. They have to be nodes, too, because they have realtionships between them

    def _create_connection(self):
        try:
            return GraphDatabase.driver(self.__uri, auth=(self.__user,self.__pass))
        except:
            traceback.print_exc()
            print("Failed to create neo4j Driver!")

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
            traceback.print_exc()
            print(f"Query failed: query \'{command}\', parameters:")
            print(parameters)
        finally:
            #finally is always executed after a 'try', no matter what
            if session is not None:
                session.close()
        return response

    def _neo4j_update(self):
        pass

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
        self.exectue(create_actor_neo, actor_parameters)

    def create_role(self,role_id, role_name, actor_id, mr_id):
        
        role_parameters = {'actor_id': actor_id, 'mr_id': mr_id, 'role_id':role_id, 'role_name':role_name}
        create_role_neo = '''CREATE r:ROLE {id: $role_id, name: $role_name, first_parent_meta: $mr_id}'''
        self.execute(create_role_neo, role_parameters)

        connect_role_parameters = {'actor_id': actor_id, 'mr_id': mr_id, 'role_id': role_id}
        connect_role_neo = '''MATCH a:Actor, mr:Meta Role, r:ROLE WHERE a.id = {$actor_id} AND mr.id = {$mr_id} AND r.id={$role_id} CREATE (a)->[p:PLAYS]-(r)-[v:VERSION]->(mr)'''
        self.execute(connect_role_neo,connect_role_parameters)

    def create_mr_and_return_id(self, character_name):
        mr_id = str(uuid4())
        create_mr_neo = '''CREATE mr:META ROLE {id: $mr_id, name: $character_name, description: auto-generated, historical: 0, religious: 0,fictional_in_universe: 0, is_biggest: 0}'''
        #no built-in function for is_biggest. You'll have to find them all and sort, then get the first  in the list
        parameters = {"character_name" : character_name, "mr_id": mr_id}
        self.execute(create_mr_neo, parameters=parameters)
        return mr_id

    def create_role_and_first_mr(self,character_name, role_id, role_name, actor_id):
        mr_id = self.create_mr_and_return_id(character_name)
        self.create_role(role_id, role_name, actor_id, mr_id)

    #UPDATE#
    #TODO
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

    #TODO we can selects the whole web. Maybe adjust accordingly.
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

    #HISTORY#
   
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

    #RELEATIONSHIPS#
    def add_relationship_actor(self, actor1_id, actor1_name, actor2_id, actor2_name, relationship_type):
        sql = '''INSERT INTO actor_relationships(actor1_id, actor1_name, actor2_id, actor2_name, relationship_type) VALUES (?,?,?,?,?)'''
        self.cursor.execute(sql, (actor1_id, actor1_name, actor2_id, actor2_name, relationship_type))

    def remove_relationships_actor(self, relationship_id_list):
        for relationship_id in relationship_id_list:
            delete_sql ='''DELETE FROM actor_relationships WHERE relationship_id={}'''.format(relationship_id)
            self.cursor.execute(delete_sql)

    def add_relationship_role(self, role1_id, role1_name, role2_id, role2_name, relationship_type):
        sql = '''INSERT INTO role_relationships(role1_id, role1_name, role2_id, role2_name, relationship_type) VALUES (?,?,?,?,?)'''
        self.cursor.execute(sql, (role1_id, role1_name, role2_id, role2_name, relationship_type))

    def remove_relationships_role(self, relationship_id_list):
        for relationship_id in relationship_id_list:
            delete_sql ='''DELETE FROM role_relationships WHERE relationship_id={}'''.format(relationship_id)
            self.cursor.execute(delete_sql)