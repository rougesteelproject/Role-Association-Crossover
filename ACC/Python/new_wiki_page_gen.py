#Get base Id, add to "parents_that_don't_show_all_roles"
#Get 'layers'
#Get 'is_actor' or 'is_mr'
class WikiPageGenerator:
    def __init__(self, base_id, layers_to_generate, base_is_actor, enable_actor_swap, db_control):
        #TODO replace wiki point-five with a tiny checkbox to simplify here
        self.db_control = db_control
        self.layers_to_generate = layers_to_generate
        self.base_is_actor = base_is_actor
        self.enable_actor_swap = enable_actor_swap
        self.base_id = base_id
        
        if base_is_actor:
            self.actors_that_dont_show_all_roles = [self.db_control.get_actor(self.base_id)]
            self.meta_roles_that_dont_show_all_roles = []
            self.base_name = self.actors_that_dont_show_all_roles[0].name
        else:
            self.actors_that_dont_show_all_roles = []
            self.meta_roles_that_dont_show_all_roles = [self.db_control.get_mr(self.base_id)]
            #TODO match these calls to the real db_cont
            self.base_name = self.meta_roles_that_dont_show_all_roles[0].name
        self.actors_that_show_all_roles = []
        self.meta_roles_that_show_all_roles = []

    def generate_content(self):
        processing_layer = 0
        while processing_layer < self.layers_to_generate:
            self.process_actors_that_dont_show_all_roles()
            self.process_meta_roles_that_dont_show_all_roles()
            self.get_new_actors_that_dont_show_all_roles_from_meta_roles_that_show_all_roles()
            self.get_new_meta_roles_that_dont_show_all_roles_from_actors_that_show_all_roles()
            processing_layer += 1

        if self.enable_actor_swap:
            self.get_actor_swap_roles()

        return

    def process_actors_that_dont_show_all_roles(self):
        for actor in self.actors_that_dont_show_all_roles:
        #for each inactive parent:
            #Get it's roles
            actor.get_roles()
            self.actors_that_show_all_roles.append(actor)
            self.actors_that_dont_show_all_roles = []

    def process_meta_roles_that_dont_show_all_roles(self):
        for meta_role in self.meta_roles_that_dont_show_all_roles:
        #for each inactive parent:
            #Get it's roles
            meta_role.get_roles()
            self.meta_roles_that_show_all_roles.append(meta_role)
            self.meta_roles_that_dont_show_all_roles = []


    def get_new_meta_roles_that_dont_show_all_roles_from_actors_that_show_all_roles(self):
        #for each active parent:
        for actor in self.actors_that_show_all_roles:
            for role in actor.roles:
                #for each role, get it's mr
                in_meta_that_show_all = False
                in_meta_that_dont_show_all = False

                #display that mr as halfway if it's not in the list of fully-displayed
                for mr in self.meta_roles_that_show_all_roles:
                    if role.parent_meta == mr.id:
                        in_meta_that_show_all = True

                #or halfway mrs
                if not in_meta_that_show_all:
                    for mr in self.meta_roles_that_dont_show_all_roles:
                        if role.parent_meta == mr.id:
                            in_meta_that_dont_show_all = True
                            mr.add_role(role)
                            #TODO a check in the mr class to not add duplicate roles
                            #TODO match the expectations of the MR class

                if not in_meta_that_dont_show_all:
                    new_meta_role = self.db_control.get_mr(role.parent_meta)
                    new_meta_role.add_role(role)
                    self.meta_roles_that_dont_show_all_roles.append(new_meta_role)
                    #TODO match what MR class has

    #for each inactive parent:
    def get_new_actors_that_dont_show_all_roles_from_meta_roles_that_show_all_roles(self):
        for mr in self.meta_roles_that_show_all_roles:
            for role in mr.roles:
                in_actors_that_show_all = False
                in_actors_that_dont_show_all = False

                #for each role, get it's actor
                    #if not in actors_that_show_all_roles, add to parents_that_dont_show_all_role

                for actor in self.actors_that_show_all_roles:
                    if role.parent_actor == actor.id:
                        in_actors_that_show_all = True

                if not in_actors_that_show_all:
                    for actor in self.actors_that_dont_show_all_roles:
                        if role.parent_actor == actor.id:
                            in_actors_that_dont_show_all = True
                            actor.add_role(role)

                if not in_actors_that_dont_show_all:
                    new_actor = self.db_control.get_actor(role.parent_actor)
                    new_actor.add_role(role)
                    self.actors_that_dont_show_all_roles.append(new_actor)

    def get_actor_swap_roles(self):
        for mr in self.meta_roles_that_dont_show_all_roles:
            mr.get_actor_swap_roles()