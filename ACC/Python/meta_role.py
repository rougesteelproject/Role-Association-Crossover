class MetaRole():
    #class > tuple because it isn't fixed
    def __init__(self, MR_class_id, name, description):
        self.roles = []
        self.id = MR_class_id
        self.name = name
        self.description = description

    def set_roles(self, roles):
        self.roles = roles

    def add_role(self,role):
        self.roles.append(role)