from image import Image
from distutils.util import strtobool

class Actor:
    def __init__(self, id, name, bio, birth_date, death_date, is_biggest, db_control):
        self.bio = bio
        self.id = id
        self.name = name
        
        self.roles = []
        self.birth_date = birth_date
        self.death_date = death_date
        self.is_biggest  = strtobool(is_biggest)
        
        self._db_control = db_control

        self.gallery = self._db_control.get_images_actor(self.id)

        self.relationships = self._db_control.get_relationships_actor_by_actor_id(self.id)
        self.abilities = self._db_control.get_ability_list_actor(self.id)
        
    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def set_roles(self, roles):
        self.roles = roles

    def get_roles(self):
        self.roles = self._db_control.get_roles(self.id, True)

    def add_role(self,role):
        role_in_this_parent = False
        for self_role in self.roles:
            if self_role.id == role.id:
                role_in_this_parent = True
        if not role_in_this_parent:
            self.roles.append(role)