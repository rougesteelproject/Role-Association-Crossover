class MetaRole():
    #class > tuple because it isn't fixed
    def __init__(self, roles, MR_class_id, name, description):
        self.roles = roles
        self.id = MR_class_id
        self.name = name
        self.description = description