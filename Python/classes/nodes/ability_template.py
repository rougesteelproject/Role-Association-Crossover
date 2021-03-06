class AbilityTemplate:
    def __init__(self, id, name, description, db_control) -> None:
        self.id = id
        self.name = name
        self.description = description

        self.db_control = db_control

        self.abilities = self.db_control.get_abilities_template(self.id)

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()