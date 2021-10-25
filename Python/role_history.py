class RoleHistory:
    def __init__(self, id, timestamp, name, description, alive_or_dead, alignment):
        self.id = id
        self.name=name
        self.description=description
        self.alive_or_dead = alive_or_dead
        self.alignment = alignment
        self.timestamp = timestamp