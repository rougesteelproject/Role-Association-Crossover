#Get base Id, add to "parents_that_don't_show_all_roles"
#Get 'layers'
#Get 'is_actor' or 'is_mr'

class WikiPageGenerator:
    def __init__(self, base_id, layers_to_generate, base_is_actor, enable_actor_swap, db_control):
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
            self.base_name = self.meta_roles_that_dont_show_all_roles[0].name
        self.actors_that_show_all_roles = []
        self.meta_roles_that_show_all_roles = [] 
        self.top_layer_actors = []
        self.top_layer_meta_roles = []

        self.link_actor_relationships = []
        self.plaintext_actor_relationships = []
        self.link_role_relationships = []
        self.plaintext_role_relationships = []

        self.actor_abilities = []
        self.role_abilities = []

        self.templates = []

    def generate_content(self):
        processing_layer = 0
        while processing_layer < self.layers_to_generate:
            #TODO THis is slow, because the top layer keeps getting bigger
            self.process_actors_that_dont_show_all_roles()
            self.process_meta_roles_that_dont_show_all_roles()

            self.get_new_actors_that_dont_show_all_roles_from_top_layer_meta_roles()
            self.get_new_meta_roles_that_dont_show_all_roles_from_top_layer_actors()
            processing_layer += 1
            print(f'Processed Layer: {processing_layer}')

        if self.enable_actor_swap:
            print('Getting Actor Swaps')
            self.get_actor_swap_roles()

        self.generate_actor_relationships()
        self.generate_actor_abilities()

        self.generate_role_relationships()
        self.generate_role_abilities()

        self.generate_templates()

        self.alphabetize()

        print('generation complete')

    def process_actors_that_dont_show_all_roles(self):
        print('Process Actors')
        self.top_layer_actors = []
        for actor in self.actors_that_dont_show_all_roles:
            print(f'{actor.id}: {actor.name}')
        #for each inactive parent:
            #Get it's roles
            actor.get_roles()
            self.actors_that_show_all_roles.append(actor)
            self.top_layer_actors.append(actor)
            self.actors_that_dont_show_all_roles = []

    def process_meta_roles_that_dont_show_all_roles(self):
        print('process mr')
        self.top_layer_meta_roles = []
        for meta_role in self.meta_roles_that_dont_show_all_roles:
            print(f'{meta_role.id}: {meta_role.name}')
        #for each inactive parent:
            #Get it's roles
            meta_role.get_roles()
            self.meta_roles_that_show_all_roles.append(meta_role)
            self.top_layer_meta_roles.append(meta_role)
            self.meta_roles_that_dont_show_all_roles = []


    def get_new_meta_roles_that_dont_show_all_roles_from_top_layer_actors(self):
        print('get meta that dont show')
        #for each active parent:
        for actor in self.top_layer_actors:
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

                if not in_meta_that_dont_show_all and not in_meta_that_show_all:
                    new_meta_role = self.db_control.get_mr(role.parent_meta)
                    new_meta_role.add_role(role)
                    self.meta_roles_that_dont_show_all_roles.append(new_meta_role)

    #for each inactive parent:
    def get_new_actors_that_dont_show_all_roles_from_top_layer_meta_roles(self):
        print('get actors that dont show')
        for mr in self.top_layer_meta_roles:
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


                if not in_actors_that_dont_show_all and not in_actors_that_show_all:
                    new_actor = self.db_control.get_actor(role.parent_actor)
                    new_actor.add_role(role)
                    self.actors_that_dont_show_all_roles.append(new_actor)

    def get_actor_swap_roles(self):
        for mr in self.meta_roles_that_dont_show_all_roles:
            mr.get_actor_swap_roles()

    def generate_actor_relationships(self):
        all_actors = []
        all_actors.extend(self.actors_that_show_all_roles)
        all_actor_ids = [actor.id for actor in all_actors]
        #Only actors that show all have bios to put relatioships in
        #Doing this because I dunno what'll happen if I just straight set it to = actors_that_show

        relationships = []
        
        for actor in all_actors:
            for relationship in actor.relationships:
                if relationship.id not in [relationship.id for relationship in relationships]:
                    relationships.append(relationship)

        link_relationships = [relationship for relationship in relationships if relationship.link_actor_id not in all_actor_ids]
        plaintext_relationships = [relationship for relationship in relationships if relationship not in link_relationships]
        
        print (link_relationships)
        print (plaintext_relationships)

        self.link_actor_relationships = link_relationships
        self.plaintext_actor_relationships = plaintext_relationships

    def generate_actor_abilities(self):
        all_actors = []
        all_actors.extend(self.actors_that_show_all_roles)
        #Only actors that show all have bios to put abilities in
        #Doing this because I dunno what'll happen if I just straight set it to = actors_that_show

        abilities = []

        for actor in all_actors:
            for ability in actor.abilities:
                if ability.id not in [ability.id for ability in abilities]:
                    abilities.append(ability)

        self.actor_abilities = abilities

    def generate_role_relationships(self):
        all_roles = []
        all_mrs = []
        role_relationships= []
        link_role_relationships = []
        plaintext_role_relationships = []

        all_mrs.extend(self.meta_roles_that_show_all_roles)
        all_mrs.extend(self.meta_roles_that_dont_show_all_roles)

        for mr in all_mrs:
            all_roles.extend(mr.roles)

        for role in all_roles:
            for relationship in role.relationships:
                if relationship.id not in [relationship.id for relationship in role_relationships]:
                    relationship.get_other_parent_meta(role.id)
                    role_relationships.append(relationship)

        for relationship in role_relationships:
            if relationship.other_role_mr not in [mr.id for mr in all_mrs]:
                plaintext_role_relationships.append(relationship)
            else:
                link_role_relationships.append(relationship)

        self.link_role_relationships = link_role_relationships
        self.plaintext_role_relationships = plaintext_role_relationships

    def generate_role_abilities(self):
        all_roles = []
        all_mrs = []

        all_mrs.extend(self.meta_roles_that_show_all_roles)
        all_mrs.extend(self.meta_roles_that_dont_show_all_roles)

        for mr in all_mrs:
            all_roles.extend(mr.roles)

        all_abilities = []

        for role in all_roles:
            for ability in role.abilities:
                if ability.id not in [ability.id for ability in all_abilities]:
                    all_abilities.append(ability)

        self.role_abilities = all_abilities

    def generate_templates(self):
        all_roles = []
        all_mrs = []

        all_mrs.extend(self.meta_roles_that_show_all_roles)
        all_mrs.extend(self.meta_roles_that_dont_show_all_roles)

        for mr in all_mrs:
            all_roles.extend(mr.roles)

        all_templates = []

        for role in all_roles:
            for template in role.ability_templates:
                if template.id not in [template.id for template in all_templates]:
                    all_templates.append(template)

        self.templates = all_templates

    def alphabetize(self):
        
        self.meta_roles_that_show_all_roles.sort()
        self.meta_roles_that_dont_show_all_roles.sort()
        
        self.actors_that_show_all_roles.sort()
        
        for mr in self.meta_roles_that_show_all_roles:
            mr.roles.sort()
        for mr in self.meta_roles_that_dont_show_all_roles:
            mr.roles.sort()
       
        self.link_actor_relationships.sort()
        self.plaintext_actor_relationships.sort()

        self.actor_abilities.sort()

        self.link_role_relationships.sort()
        self.plaintext_role_relationships.sort()

        self.role_abilities.sort()

        self.templates.sort()

    #TODO we'l have to return the Hub Sigils (when we integrate into flask/ the graphviz)