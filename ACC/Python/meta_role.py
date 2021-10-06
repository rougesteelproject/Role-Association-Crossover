from distutils.util import strtobool


class MetaRole():
    #class > tuple because it isn't fixed
    def __init__(self, MR_class_id, name, description, historical, religious, fictional_in_universe,is_biggest,db_control):
        self.roles = []
        self.id = MR_class_id
        self.name = name
        self.description = description
        self._db_control = db_control
        self.historical = historical
        self.religious = religious
        self.fictional_in_universe = fictional_in_universe
        self.is_biggest = strtobool(is_biggest)

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def set_roles(self, roles):
        self.roles = roles

    def get_roles(self):
        self.roles = self._db_control.get_roles(self.id, False)

    def add_role(self,role):
        role_in_this_parent = False
        for self_role in self.roles:
            if self_role.id == role.id:
                role_in_this_parent = True
        if not role_in_this_parent:
            self.roles.append(role)

    def add_roles(self,role_list):
        self.roles.extend(role_list)
        #TODO add duplication chaecking

    def get_actor_swap_roles(self):
        swaps = []
        for role in self.roles:
            if (role.actor_swap_id != 0):
                swaps.extend(self._db_control.get_roles_swap(self.id, role.actor_swap_id))
        self.add_roles(swaps)