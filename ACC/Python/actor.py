from image import Image
from distutils.util import strtobool

class Actor:
    def __init__(self, id, name, bio, birth_date, death_date, is_biggest, db_control):
        self.bio = bio
        self.id = id
        self.name = name
        self.gallery = []
        self.roles = []
        self.birth_date = birth_date
        self.death_date = death_date
        self.is_biggest  = strtobool(is_biggest)
        
        self._db_control = db_control
        self.get_Images()

        self.relationships = []
        self.abilities = []
        #self.get_relationships()
        #TODO a function like this for each type of relationship
        
    def get_Images(self):
        images = self._db_control.select("file, caption", "gallery", "actor", self.id)
        for image in images:
            self.gallery.append(Image(image[0], image[1]))

    def set_roles(self, roles):
        self.roles = roles

    def set_abilities(self, abilities):
        self.abilities = abilities

    def get_roles(self):
        self.roles = self._db_control.get_roles(self.id, True)

    def add_role(self, role):
        self.roles.append(role)