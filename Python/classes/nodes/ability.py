class Ability():
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()