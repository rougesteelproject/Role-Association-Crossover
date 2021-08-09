from database_controller import DatabaseController
import imdb
import constants
import traceback


class IMDBImporter():
    def __init__(self, db_controller):
        self._db_controller = db_controller
        self.ia = imdb.IMDb(adultSearch=0)
        #if it's not adult
        self.number_of_actors_to_loop = constants.NUMBER_OF_ACTORS_TO_LOOP

    

    #calls create_actor then create_role on all their roles
    def loop_Movies(self, actor_ID):
        try:
            actor = self.ia.get_person(str(actor_ID).zfill(8))
            actor_name = actor['name']
            actor_id = actor.personID

            for job in actor['filmography'].keys():
                if job == 'actress' or job == 'actor':
                    print(actor_id + " " + actor_name)

                    with self._db_controller.connection:
                        # create a new row in the actor table

                        db_actor = (actor_id, actor_name, 'auto-generated', 0)
                        self._db_controller.create_actor(db_actor)

                        #add filmography
                        for movie in actor['filmography'][job]:

                            movie_title = movie['title']
                            role_names = str(movie.currentRole).split("/")
                            role_index = 0
                            for character_name in role_names:
                                role_id = actor_id + '-' + movie.movieID + '-' + str(role_index)
                                role_index += 1
                                role_name = (f'{character_name} ({movie_title}) ({actor_name})')
                                #print(role_name)
                                self._db_controller.cursor.execute("SELECT MAX(id) FROM meta_roles")
                                mr_id = self._db_controller.cursor.fetchone()[0]
                                if mr_id is not None:
                                    mr_id += 1
                                else:
                                    mr_id = 1
                                #Select Max() gets the highest in that column

                                db_role = (role_id, role_name, 'auto-generated', actor_id, mr_id, '0', mr_id,)

                                
                                self._db_controller.create_mr(mr_id, character_name, 'auto-generated', 0)

                                self._db_controller.create_role(db_role)
            self._db_controller.commit()

                                
        except imdb.IMDbError:
            traceback.print_exc()
        except KeyError as e3:
            print(e3) 
        except:
            traceback.print_exc()       
        print('*')

    def get_All_IMDBdb(self):
        #Have it go from 0 to eight nines, since they have 50mil, tops
        actor_id = 1
        while actor_id < self.number_of_actors_to_loop:
            self.loop_Movies(actor_id)
            actor_id += 1

def main():
    db_controller = DatabaseController()
    db_controller.create_connection()
    imdb = IMDBImporter(db_controller)
    imdb.get_All_IMDBdb()

if __name__ == '__main__':
    main()