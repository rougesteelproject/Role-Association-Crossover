from classes.nodes.image import Image

class Role:

    def __init__(self, role_id, role_name, db_control, role_description= "auto-generated", alive_or_dead="alive", alignment="", parent_actor_id= None, parent_meta_id= None, actor_swap_id= None):
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

        self.gallery = self._db_control.get_images_role(self.id)

        self.relationships = self._db_control.get_relationships_role_by_role_id(self.id)
        self.abilities = self._db_control.get_ability_list_role(self.id)
        self.ability_templates = self._db_control.get_ability_template_list(self.id)

    def __lt__(self, other):
        return self.name.lower() < other.name.lower() 