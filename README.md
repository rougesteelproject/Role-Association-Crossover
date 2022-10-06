# Role Association Crossover

## Dependancies

- (neo4j or sqlite 3)
- flask
- cinemagoer(formerly imdbpy)
- uuid
- neomodel needs Shapely, which dowsn't work for python 3.10

## Global TODO

- TODO: the base needs to be more modular. public methods should be calling db-specific private methods
- Law of Demeter: each class shouls only 'know' it's own methods or variables, and the top-level methods
of any other classes it has been given
-Have getters vs public variables
- TODO variable types with (name: type)
- TODO more intuitive variable names, a sweep to make it pythonic
- TODO I shouldn't need "go_back_url"
-- some need to stay put
-- Links/buttons can go onclick="history.back()"
- TODO: update per: [cinemagoer's docs](https://cinemagoer.readthedocs.io/en/latest/)
- TODO: does adultSearch=0 still work?
- TODO we need a better way to store the changelog for actors/mrs/abilities

Now generating MR id equal to the role id. This makes it easy to match a role to it's original mr. It's as close to a natural key as i can get. each mr is derived from the role, after all. -This means mr id comes from role id, --which comes from actor id + movie + index of roles by that actor in that movie

## Reject Pile

### cinemagoer

SQLAlchemy will be needed for the s3database method there may be a way to go right from one DB to another Actually, this has poroblems with characters. In the SQL, every character with the same name has the same ID While this may be more efficient, we'd actually have to spend time separating chars that don't have the same MR
