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
    #TODO break into smaller pieces
    def loop_Movies(self, actor_ID):
        try:
            actor = self.ia.get_person(str(actor_ID).zfill(8))
            actor_name = actor['name']
            actor_id = actor.personID
            birth_date = actor['birth date']
            death_date = actor['death date']

            for job in actor['filmography'].keys():
                if job == 'actress' or job == 'actor':
                    
                    print(actor_id + " " + actor_name)

                    with self._db_controller.connection:
                        
                        # create a new row in the actor table
                        self._db_controller.create_actor(actor_id, actor_name, birth_date,death_date)

                        #add filmography
                        for movie in actor['filmography'][job]:

                            movie_title = movie['title']
                            
                            role_names = str(movie.currentRole).split("/")
                            
                            role_index = 0
                            
                            for character_name in role_names:
                                
                                role_index += 1
                                role_id = self.create_role_id(actor_id, movie,role_index)
                                role_name = self.create_role_name(character_name,movie_title,actor_name)
                                print(role_name)
                                
                                mr_id = self.create_mr_id()
                                
                                self._db_controller.create_mr(mr_id, character_name)

                                self._db_controller.create_role(role_id, role_name,actor_id, mr_id)
            self._db_controller.commit()

                                
        except imdb.IMDbError:
            traceback.print_exc()
        except KeyError as e3:
            print(e3) 
        except:
            traceback.print_exc()       
        print('* * *')

    def get_All_IMDBdb(self):
        #Have it go from 0 to eight nines, since they have 50mil, tops
        actor_id = 1
        while actor_id < self.number_of_actors_to_loop:
            self.loop_Movies(actor_id)
            actor_id += 1
        print('Done')

    def create_role_id(self, actor_id, movie, role_index):
        role_id = actor_id + '-' + movie.movieID + '-' + str(role_index)
        return role_id
        
    def create_role_name(self, character_name, movie_title,actor_name):
        role_name = (f'{character_name} ({movie_title}) ({actor_name})')
        return role_name

    def create_mr_id(self):
        mr_id = self._db_controller.cursor.select_max("id", "meta_roles")
        if mr_id is not None:
            mr_id += 1
        else:
            mr_id = 1
        #Select Max() gets the highest in that column
        return mr_id

def main():
    db_controller = DatabaseController()
    db_controller.create_connection()
    db_controller.create_db_if_not_exists()
    imdb = IMDBImporter(db_controller)
    imdb.get_All_IMDBdb()

if __name__ == '__main__':
    main()