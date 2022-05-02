# Role-Association-Crossover

needs neo4j, flask, cinemagoer(formerly imdbpy), uuid
    neomodel needs Shapely, which dowsn't work for python 3.10
    
TODO: update per: https://cinemagoer.readthedocs.io/en/latest/ 
TODO: there may be a new way to get IMDB Id's 
TODO: does adultSearch=0 still work?

TODO: SQLAlchemy will be needed for the s3database method
    TODO: there may be a way to go right from one DB to another
    Actually, this has poroblems with characters. In the SQL, every character with the same name
    has the same ID
        While this may be more efficient, we'd actually have to spend time separating chars
        that don't have the same MR

#TODO we need a better way to store the changelog for actors/mrs/abilities
