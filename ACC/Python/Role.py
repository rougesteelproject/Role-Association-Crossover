from image import Image

class Role:

    def __init__(self, role_id, role_name, role_description, alive_or_dead, alignment, parent_actor_id, parent_meta_id, actor_swap_id, db_control):
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
        self.gallery = []
        self.get_Images()

        self.relationships =[]
        self.get_relationships()
        #TODO a function like this for each type of relationship
        #TODO maybe a relationship class

    def get_Images(self):
        images = self._db_control.select("file, caption", "gallery", "role", self.id)
        for image in images:
            self.gallery.append( Image(image[0], image[1]))