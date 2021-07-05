import imdb
import Constants
#TODO learn how to pass it db_controller

class IMDBImporter():
    def __init__(self, _db_controler):
        self._db_controler = _db_controler
        self.ia = imdb.IMDb(adultSearch=0)
        #if it's not adult
        self.number_of_actors_to_loop = Constants.NUMBER_OF_ACTORS_TO_LOOP

#create a new actor row in the table
    def create_actor(self, db_actor):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        #TODO change bio to multiple fields
        #TODO don't forget to create those multiple fields in the other .py files, also
        create_actor_sql = '''INSERT OR IGNORE INTO actors(id, name, bio, is_biggest) VALUES (?,?,?,?) '''
        self._db_controller.cursor.execute(create_actor_sql, db_actor)

    #create a new role in the role table
    def create_role(self,db_role):
        #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
        create_role_sql = '''INSERT OR IGNORE INTO roles(id, name, description, parent_actor, parent_meta, actor_swap_id, first_parent_meta) VALUES (?,?,?,?,?,?,?) '''
        # Create table if it doesn't exist
        self._db_controller.cursor.execute(create_role_sql, db_role)

    #calls create_actor then create_role on all their roles
    def loop_Movies(self, actor_ID):
        try:
            actor = self.ia.get_person(str(actor_ID).zfill(8))
            actor_name = actor['name']
            actor_id = actor.personID

            for job in actor['filmography'].keys():
                if job == 'actress' or job == 'actor':
                    #print(actor_id + " " + actor_name)

                    with self._db_controller.connection:
                        # create a new row in the actor table

                        db_actor = (actor_id, actor_name, 'auto-generated', 0)
                        self.create_actor(db_actor)

                        #add filmography
                        for movie in actor['filmography'][job]:

                            movie_title = movie['title']
                            role_names = str(movie.currentRole).split("/")
                            role_index = 0
                            for character_name in role_names:
                                role_id = actor_id + '-' + movie.movieID + '-' + str(role_index)
                                role_index += 1
                                role_name = (f'{character_name} ({movie_title}) ({actor_name})')
                                
                                self._db_controller.cursor.execute("SELECT MAX(id) FROM meta_roles")
                                mr_id = self._db_controller.cursor.fetchone()[0]
                                if mr_id is not None:
                                    mr_id += 1
                                else:
                                    mr_id = 1
                                #Select Max() gets the highest in that column

                                db_role = (role_id, role_name, 'auto-generated', actor_id, mr_id, '0', mr_id,)

                                sql = '''INSERT OR IGNORE INTO meta_roles(id, name, description, is_biggest) VALUES (?,?,?,?) '''
                                self._db_controller.cursor.execute(sql,(mr_id, character_name, 'auto-generated', 0,))

                                self.create_role(db_role)
            self._db_controler.commit()

                                
        except imdb.IMDbError as e:
            print(e)
        except KeyError as e3:
            print(e3)        
        #print('*')

    def get_All_IMDBdb(self):
        #Have it go from 0 to eight nines, since they have 50mil, tops
        actor_id = 1
        while actor_id < self.number_of_actors_to_loop:
            self.loop_Movies(actor_id)
            actor_id += 1