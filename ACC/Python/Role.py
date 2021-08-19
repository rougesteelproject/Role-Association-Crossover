from image_class import Image

class Role:
    def __init__(self, role_id, role_name, role_description, actor_swap_id, db_control):
        #TODO put back the parent id's like in the database
        self.id = role_id
        self.name = role_name
        self.description = role_description
        self.parent_actor
        self.parent_meta
        self.actor_swap_id = actor_swap_id
        self._db_control = db_control
        self.gallery = []
        self.get_Images()

    def get_Images(self):
        images = self._db_control.select("file, caption", "gallery", "role", self.id)
        for image in images:
            self.gallery.append( Image(image[0], image[1]))

    def set_parent_meta(self, parent_meta):
        self.parent_meta = parent_meta

    def set_parent_actor(self, parent_actor):
        self.parent_actor = parent_actor

    def set_actor_swap_id(self, actor_swap_id):
        self.actor_swap_id = actor_swap_id