from image import Image

class Role:

    def __init__(self, role_id, role_name, role_description, alive_or_dead, alignment, parent_actor_id, parent_meta_id, actor_swap_id, first_parent_meta,db_control):
        self.id = role_id
        self.name = role_name
        self.description = role_description
        self.parent_actor = parent_actor_id
        #parents have roles, roles have ids.
        self.parent_meta = parent_meta_id
        self.actor_swap_id = actor_swap_id
        self._db_control = db_control
        self.alive_or_dead = alive_or_dead
        self.alignment = alignment
        self.first_parent_meta = first_parent_meta
        self.gallery = self._db_control.get_images_role(self.id)

        self.relationships = self._db_control.get_relationships_role_by_role_id(self.id)
        self.abilities = self._db_control.get_ability_list_role(self.id)
        self.ability_templates = []

    def __lt__(self, other):
        return self.name.lower() < other.name.lower() 