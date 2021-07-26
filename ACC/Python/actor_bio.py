import image_class

class ActorBio:
    def __init__(self, actor_class_bio, actor__class_id, actor_name, db_control):
        self.bio = actor_class_bio
        self.id = actor__class_id
        self.name = actor_name
        self.gallery = []
        
        self._db_control = db_control
        self.get_Images()
        
    def get_Images(self):
        images = self._db_control.select("file, caption", "gallery", "actor", self.id)
        for image in images:
            self.gallery.append(image_class(image[0], image[1]))