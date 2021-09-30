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

    def get_actor_IMDB(self, actor_ID):
        try:
            actor = self.ia.get_person(str(actor_ID).zfill(8))
            actor_name = actor['name']
            actor_id = actor.personID
            actor_bio = actor['biography'][0]
            birth_date = actor['birth date']
            try:
                death_date = actor['death date']
            except:
                death_date = "n/a"

            print(actor_id + " " + actor_name)

            for job in actor['filmography'].keys():
                if job == 'actress' or job == 'actor':

                    with self._db_controller.connection:
                        
                        # create a new row in the actor table
                        self._db_controller.create_actor(actor_id, actor_name, actor_bio,birth_date,death_date)

                        #add filmography
                        for movie in actor['filmography'][job]:

                            movie_title = movie['title']
                            
                            role_names = str(movie.currentRole).split("/")
                            
                            for role_index, character_name in enumerate(role_names):
                                
                                role_id = self.create_role_id(actor_id, movie,role_index+1)
                                role_name = self.create_role_name(character_name,movie_title,actor_name)
                                print(role_name)
                            
                                self._db_controller.create_role_and_first_mr(character_name, role_id, role_name, actor_id)

            self._db_controller.commit()

        except:
            traceback.print_exc()       
        print('* * *')

    def get_all_IMDB(self):
        #Have it go from 0 to eight nines, since they have 50mil, tops
        actor_id = 1
        while actor_id < self.number_of_actors_to_loop:
            self.get_actor_IMDB(actor_id)
            actor_id += 1
        print('Done')

    def create_role_id(self, actor_id, movie, role_index):
        role_id = actor_id + '-' + movie.movieID + '-' + str(role_index)
        return role_id
        
    def create_role_name(self, character_name, movie_title,actor_name):
        role_name = (f'{character_name} ({movie_title}) ({actor_name})')
        return role_name

def main():
    db_controller = DatabaseController()
    db_controller.create_connection()
    db_controller.create_db_if_not_exists()
    imdbImp = IMDBImporter(db_controller)
    imdbImp.get_actor_IMDB(636046)


if __name__ == '__main__':
    main()