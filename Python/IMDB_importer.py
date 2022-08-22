from imdb import Cinemagoer
import constants
import logging

#TODO switch to the s3dataset method so you can just download once, re-download every so often
#https://imdbpy.readthedocs.io/en/latest/usage/s3.html

#TODO The get_movie, get_person and get_company methods take an optional info parameter,
# which can be used to specify the kinds of data to fetch.

class IMDBImporter():
    def __init__(self, callback_db_control):
        self._callback_db_control = callback_db_control
        self.ia = Cinemagoer(adultSearch=0)
        #if it's not adult
        self.number_of_actors_to_loop = constants.NUMBER_OF_ACTORS_TO_LOOP

    #calls create_actor then create_role on all their roles

    def get_actor_IMDB(self, actor_ID):
        try:
            actor = self.ia.get_person(str(actor_ID).zfill(8))
            #TODO actor = self.ia.get_person(str(actor_ID).zfill(8), info = ['biography','filmography'])
            #This will be a test of a change to get only what we need
            actor_name = actor['name']
            actor_id = str(actor_ID)
            actor_bio = actor['biography'][0]
            birth_date = actor['birth date']
            try:
                death_date = actor['death date']
            except:
                death_date = "n/a"

            logging.debug(actor_id + " " + actor_name)

            for job in actor['filmography'].keys():
                if job == 'actress' or job == 'actor':
                        
                    # create a new row in the actor table
                    self._create_actor(actor_id, actor_name, actor_bio,birth_date,death_date)

                    #add filmography
                    for movie in actor['filmography'][job]:

                        movie_title = movie['title']
                        
                        role_names = str(movie.currentRole).split("/")
                        
                        for role_index, character_name in enumerate(role_names):
                            
                            role_id = self._create_role_id(actor_id, movie,role_index+1)
                            role_name = self._create_role_name(character_name,movie_title,actor_name)
                            logging.debug(role_name)
                        
                            self._create_role_and_first_mr(character_name, role_id, role_name, actor_id)

        except:
            logging.exception(f'An exception ocured while getting actor with id: {actor_ID}')
        logging.debug('* * *')

    def get_all_IMDB(self):
        #Have it go from 0 to eight nines, since they have 50mil, tops
        actor_id = 1
        while actor_id < self.number_of_actors_to_loop:
            self.get_actor_IMDB(actor_id)
            actor_id += 1
        logging.debug('Done')

    def get_testing_IMDB(self):
        self.get_actor_IMDB(89707)
        self.get_actor_IMDB(284)
        self.get_actor_IMDB(1281932)

    def _create_role_id(self, actor_id, movie, role_index):
        role_id = actor_id + '-' + movie.movieID + '-' + str(role_index)
        return role_id
        
    def _create_role_name(self, character_name, movie_title,actor_name):
        role_name = (f'{character_name} ({movie_title}) ({actor_name})')
        return role_name

    def _create_actor(self, actor_id, actor_name, actor_bio,birth_date,death_date):
        self._callback_db_control.create_actor(actor_id, actor_name, actor_bio,birth_date,death_date)

    def _create_role_and_first_mr(self, character_name, role_id, role_name, actor_id):
        self._callback_db_control.create_role_and_first_mr(character_name, role_id, role_name, actor_id)