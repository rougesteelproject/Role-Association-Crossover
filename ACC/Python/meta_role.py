class MetaRole():
    #class > tuple because it isn't fixed
    def __init__(self, MR_class_id, name, description, db_control):
        self.roles = []
        self.id = MR_class_id
        self.name = name
        self.description = description
        self._db_control = db_control

    def set_roles(self, roles):
        self.roles = roles

    def add_role(self,role):
        self.roles.append(role)

    def add_roles(self,role_list):
        self.roles.extend(role_list)

    def get_actor_swaps(self):
        for role in self.roles:
            if (role.actor_swap_id != 0):
                swaps = self._db_control.get_roles_swap(self.id, role.actor_swap_id)
                self.add_roles(swaps)