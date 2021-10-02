class SearchBar:
    def __init__(self, db_control, query):
        self.db_control = db_control
        self.query = query

        self.displayed_mrs = []
        self.displayed_actors = []

        #TODO something like wiki_gen