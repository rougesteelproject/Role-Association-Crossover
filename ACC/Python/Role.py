import Image as image_class

class Role:
    def __init__(self, role_id, role_name, role_description, parent_actor, parent_meta, actor_swap_id, db_control):
        self.id = role_id
        self.name = role_name
        self.description = role_description
        self.parent_actor = parent_actor
        self.parent_meta = parent_meta
        self.actor_swap_id = actor_swap_id
        self.gallery = self.get_Images(role_id)
        self._db_control = db_control

    def get_Images(self, role_id):
        images = self.db_control.select("file, caption", "gallery", "role", role_id)
        gallery = []
        for image in images:
            gallery.append( image_class(image[0], image[1]))
        return gallery