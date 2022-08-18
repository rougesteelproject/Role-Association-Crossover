class ActorRelationship():
    def __init__(self, id, actor1_id, actor1_name, actor2_id, actor2_name, type):
        self.id = id
        self.actor1_id = actor1_id
        self.actor1_name = actor1_name
        self.actor2_id = actor2_id
        self.actor2_name = actor2_name
        self.type = type
        self.link_actor_id = None
        self.link_actor_name = None
        #TODO rename this a bit, because we still need link_actor_name for plaintext, it's the "other" member
        self.plaintext_actor_id = None
        self.plaintext_actor_name = None

    def set_link_actor(self, actor_id):
        if self.actor1_id == actor_id:
            self.link_actor_id = self.actor1_id
            self.link_actor_name = self.actor1_name
            self.plaintext_actor_id = self.actor2_id
            self.plaintext_actor_name = self.actor2_name
        elif self.actor2_id == actor_id:
            self.link_actor_id = self.actor2_id
            self.link_actor_name = self.actor2_name
            self.plaintext_actor_id = self.actor1_id
            self.plaintext_actor_name = self.actor1_name
        else:
            print(f'Error: {actor_id} is not either of the actors in relationship {self.id}')


    def __lt__(self, other):
        return self.type.lower() < other.type.lower()