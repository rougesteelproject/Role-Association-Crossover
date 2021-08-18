import image_class

class Role:
    def __init__(self, role_id, role_name, role_description, alive_or_dead, alignment, parent_actor, parent_meta, actor_swap_id, db_control):
        self.id = role_id
        self.name = role_name
        self.description = role_description
        self.parent_actor = parent_actor
        self.parent_meta = parent_meta
        self.actor_swap_id = actor_swap_id
        self._db_control = db_control
        self.alive_or_dead = alive_or_dead
        self.alignment = alignment
        self.gallery = []
        self.get_Images()

    def get_Images(self):
        images = self._db_control.select("file, caption", "gallery", "role", self.id)
        for image in images:
            self.gallery.append( image_class(image[0], image[1]))