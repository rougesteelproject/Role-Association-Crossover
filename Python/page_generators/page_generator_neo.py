import logging
from page_generators.wiki_page_generator import WikiPageGenerator

class PageGeneratorNeo(WikiPageGenerator):
    def __init__(self, layers_to_generate, callback_db_control, enable_actor_swap = False, base_actor = None, base_mr = None):
        super().__init__(layers_to_generate, enable_actor_swap)
        self._db_control = callback_db_control
        
        self._base_name = None

        if base_actor is not None:
            self._get_base_base_is_actor(base_actor)
        elif base_mr is not None:
            self._get_base_base_is_mr(base_mr)
            
        self._actors_that_show_all_roles = []
        self._meta_roles_that_show_all_roles = [] 
        self._top_layer_actors = []
        self._top_layer_meta_roles = []

    def _get_base_base_is_actor(self, base_actor):
        self._actors_that_dont_show_all_roles = [base_actor]
        self._meta_roles_that_dont_show_all_roles = []
        self._base_name = base_actor.name

    def _get_base_base_is_mr(self, base_mr):
        self._actors_that_dont_show_all_roles = []
        self._meta_roles_that_dont_show_all_roles = [base_mr]
        self._base_name = base_mr.name

    #TODO Could we get the whole blob somehow?, and feed it right to FLASK?
    #SQL Version:
    def generate_content(self):
        if self._base_name is not None:
            processing_layer = 0
            while processing_layer < self._layers_to_generate:

                

                self._process_actors_that_dont_show_all_roles()
                self._process_meta_roles_that_dont_show_all_roles()

                self._get_new_actors_that_dont_show_all_roles_from_top_layer_meta_roles()
                self._get_new_meta_roles_that_dont_show_all_roles_from_top_layer_actors()
                processing_layer += 1
                logging.debug(f'Processed Layer: {processing_layer}')

            if self._enable_actor_swap:
                logging.debug('Getting Actor Swaps')
                self._get_actor_swap_roles()

            self._generate_actor_relationships()
            self._generate_actor_abilities()

            self._generate_role_relationships()
            self._generate_role_abilities()

            self._generate_templates()

            self._alphabetize()

            logging.debug('generation complete')
        else:
            logging.debug('Error: attempt to generate page with no base mr or actor')

    def _process_actors_that_dont_show_all_roles(self):
        logging.debug('Process Actors')
        self._top_layer_actors = []
        for actor in self._actors_that_dont_show_all_roles:
            logging.debug(f'{actor.id}: {actor.name}')
        #for each inactive parent:
            #Get it's roles
            actor.get_roles()
            self._actors_that_show_all_roles.append(actor)
            self._top_layer_actors.append(actor)
            self._actors_that_dont_show_all_roles = []

    def _process_meta_roles_that_dont_show_all_roles(self):
        logging.debug('process mr')
        self._top_layer_meta_roles = []
        for meta_role in self._meta_roles_that_dont_show_all_roles:
            logging.debug(f'{meta_role.id}: {meta_role.name}')
        #for each inactive parent:
            #Get it's roles
            meta_role.get_roles()
            self._meta_roles_that_show_all_roles.append(meta_role)
            self._top_layer_meta_roles.append(meta_role)
            self._meta_roles_that_dont_show_all_roles = []


    def _get_new_meta_roles_that_dont_show_all_roles_from_top_layer_actors(self):
        logging.debug('get meta that dont show')
        #for each active parent:
        for actor in self._top_layer_actors:
            for role in actor.roles:
                
                #for each role, get it's mr
                in_meta_that_show_all = False
                in_meta_that_dont_show_all = False

                #display that mr as halfway if it's not in the list of fully-displayed
                for mr in self._meta_roles_that_show_all_roles:
                    if self._db_control.get_parent_meta(role.id) == mr.id:
                        in_meta_that_show_all = True

                #or halfway mrs
                if not in_meta_that_show_all:
                    for mr in self._meta_roles_that_dont_show_all_roles:
                        if self._db_control.get_parent_meta(role.id) == mr.id:
                            in_meta_that_dont_show_all = True
                            mr.add_role(role)

                if not in_meta_that_dont_show_all and not in_meta_that_show_all:
                    new_meta_role = self._db_control.get_mr(self._db_control.get_parent_meta(role.id))
                    new_meta_role.add_role(role)
                    self._meta_roles_that_dont_show_all_roles.append(new_meta_role)

    #for each inactive parent:
    def _get_new_actors_that_dont_show_all_roles_from_top_layer_meta_roles(self):
        logging.debug('get actors that dont show')
        for mr in self._top_layer_meta_roles:
            for role in mr.roles:
                
                in_actors_that_show_all = False
                in_actors_that_dont_show_all = False

                #for each role, get it's actor
                    #if not in actors_that_show_all_roles, add to parents_that_dont_show_all_role

                for actor in self._actors_that_show_all_roles:
                    if self._db_control.get_parent_actor(role.id) == actor.id:
                        in_actors_that_show_all = True

                if not in_actors_that_show_all:
                    for actor in self._actors_that_dont_show_all_roles:
                        if self._db_control.get_parent_actor(role.id) == actor.id:
                            in_actors_that_dont_show_all = True
                            actor.add_role(role)


                if not in_actors_that_dont_show_all and not in_actors_that_show_all:
                    new_actor = self._db_control.get_actor(self._db_control.get_parent_actor(role.id))
                    new_actor.add_role(role)
                    self._actors_that_dont_show_all_roles.append(new_actor)

    def _get_actor_swap_roles(self):
        for mr in self._meta_roles_that_dont_show_all_roles:
            mr.get_actor_swap_roles()

    def _generate_actor_relationships(self):
        all_actors = []
        all_actors.extend(self._actors_that_show_all_roles)
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

    def _generate_actor_abilities(self):
        all_actors = []
        all_actors.extend(self._actors_that_show_all_roles)
        #Only actors that show all have bios to put abilities in
        #Doing this because I dunno what'll happen if I just straight set it to = actors_that_show

        abilities = []

        for actor in all_actors:
            for ability in actor.abilities:
                if ability.id not in [ability.id for ability in abilities]:
                    abilities.append(ability)

        self.actor_abilities = abilities

    def _generate_role_relationships(self):
        all_roles = []
        all_mrs = []
        role_relationships= []
        link_role_relationships = []
        plaintext_role_relationships = []

        all_mrs.extend(self._meta_roles_that_show_all_roles)
        all_mrs.extend(self._meta_roles_that_dont_show_all_roles)

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

    def _generate_role_abilities(self):
        all_roles = []
        all_mrs = []

        all_mrs.extend(self._meta_roles_that_show_all_roles)
        all_mrs.extend(self._meta_roles_that_dont_show_all_roles)

        for mr in all_mrs:
            all_roles.extend(mr.roles)

        all_abilities = []

        for role in all_roles:
            for ability in role.abilities:
                if ability.id not in [ability.id for ability in all_abilities]:
                    all_abilities.append(ability)

        self.role_abilities = all_abilities

    def _generate_templates(self):
        all_roles = []
        all_mrs = []

        all_mrs.extend(self._meta_roles_that_show_all_roles)
        all_mrs.extend(self._meta_roles_that_dont_show_all_roles)

        for mr in all_mrs:
            all_roles.extend(mr.roles)

        all_templates = []

        for role in all_roles:
            for template in role.ability_templates:
                if template.id not in [template.id for template in all_templates]:
                    all_templates.append(template)

        self.templates = all_templates

    def _alphabetize(self):
        
        self._meta_roles_that_show_all_roles.sort()
        self._meta_roles_that_dont_show_all_roles.sort()
        
        self._actors_that_show_all_roles.sort()
        
        for mr in self._meta_roles_that_show_all_roles:
            mr.roles.sort()
        for mr in self._meta_roles_that_dont_show_all_roles:
            mr.roles.sort()
       
        self.link_actor_relationships.sort()
        self.plaintext_actor_relationships.sort()

        self.actor_abilities.sort()

        self.link_role_relationships.sort()
        self.plaintext_role_relationships.sort()

        self.role_abilities.sort()

        self.templates.sort()