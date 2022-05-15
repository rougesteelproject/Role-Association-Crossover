#Get base Id, add to "parents_that_don't_show_all_roles"
#Get 'layers'
#Get 'is_actor' or 'is_mr'

#TODO get the director to do the db stuff

class WikiPageGenerator:
    def __init__(self, layers_to_generate, enable_actor_swap = False):
        self._layers_to_generate = layers_to_generate
        self._enable_actor_swap = enable_actor_swap

        self.link_actor_relationships = []
        self.plaintext_actor_relationships = []
        self.link_role_relationships = []
        self.plaintext_role_relationships = []

        self.actor_abilities = []
        self.role_abilities = []

        self.templates = []

    def generate_content(self):
        #TODO using neo, I may be able to get the whole pile, so to speak.
        pass 

    #TODO we'l have to return the Hub Sigils (when we integrate into flask/ the graphviz)