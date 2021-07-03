import imdb
ia = imdb.IMDb(adultSearch=0)
#if it's not adult

import sqlite3
database = r'C:/MAMP/db/sqllite/rac.db'

#create a connection to the db with address db_file
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn

# create a database connection
conn = create_connection(database)

cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS meta_roles(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT, is_biggest INT )''')
cur.execute('''CREATE TABLE IF NOT EXISTS gallery(file NOT NULL, role INT, actor INT, caption TEXT)''')
# Create table if it doesn't exist
cur.execute('''CREATE TABLE IF NOT EXISTS actors(id INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, bio TEXT, is_biggest INT )''')
cur.execute('''CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT, parent_actor INT, parent_meta INT, actor_swap_id INT, first_parent_meta INT )''')
#TODO roles need a bio section with powers and relationships
conn.commit()

#create a new actor row in the table
def create_actor(db_actor):
    #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
    #TODO change bio to multiple fields
    #TODO don't forget to create those multiple fields in the other .py files, also
    sql = '''INSERT OR IGNORE INTO actors(id, name, bio, is_biggest) VALUES (?,?,?,?) '''
    cur.execute(sql, db_actor)
    conn.commit()

#create a new role in the role table
def create_role(db_role):
    #INSERT OR IGNORE ignores the INSERT if it already exists (if the value we select for has to be unique, like a PRIMARY KEY)
    sql = '''INSERT OR IGNORE INTO roles(id, name, description, parent_actor, parent_meta, actor_swap_id, first_parent_meta) VALUES (?,?,?,?,?,?,?) '''
    # Create table if it doesn't exist
    cur.execute(sql, db_role)
    conn.commit()

#calls create_actor then create_role on all their roles
def loopMovies(actor):
    try:
        actor_name = actor['name']
        actor_id = actor.personID

        for job in actor['filmography'].keys():
            if job == 'actress' or job == 'actor':
                print(actor_id + " " + actor_name)

                with conn:
                    # create a new row in the actor table

                    db_actor = (actor_id, actor_name, 'auto-generated', 0)
                    create_actor(db_actor)

                    #add filmography
                    for movie in actor['filmography'][job]:

                        movie_title = movie['title']
                        role_names = str(movie.currentRole).split("/")
                        role_index = 0
                        for character_name in role_names:
                            role_id = actor_id + '-' + movie.movieID + '-' + str(role_index)
                            role_index += 1
                            role_name = (f'{character_name} ({movie_title}) ({actor_name})')
                            print (role_name)

                            cur = conn.cursor()
                            cur.execute("SELECT MAX(id) FROM meta_roles")
                            mr_id = cur.fetchone()[0]
                            if mr_id is not None:
                                mr_id += 1
                            else:
                                mr_id = 1
                            #Select Max() gets the highest in that column

                            db_role = (role_id, role_name, 'auto-generated', actor_id, mr_id, '0', mr_id,)

                            sql = '''INSERT OR IGNORE INTO meta_roles(id, name, description, is_biggest) VALUES (?,?,?,?) '''
                            cur.execute(sql,(mr_id, character_name, 'auto-generated', 0,))
                            conn.commit()

                            create_role(db_role)

                            
    except imdb.IMDbError as e:
        print(e)
    except KeyError as e3:
        print(e3)

    
                    
    print('*')

def getIMDBdb():
    #Have it go from 0 to eight nines, since they have 50mil, tops
    actor_id = 1
    while actor_id < 100000000:
        actor = ia.get_person(str(actor_id).zfill(8))
        loopMovies(actor)
        actor_id += 1

    print("done")

#TODO adjust loopMovies so it's easier to call with just an ID #

try:
    actor = ia.get_person("284")
    loopMovies(actor)
except HTTPError as HTTPError:
    print(HTTPError)
except imdb.IMDbError as error:
    print(error)