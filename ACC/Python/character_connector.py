class CharacterConnector():
    def __init__(self, _db_controler):
        self._db_controler = _db_controler

    def changeMR(self, role_id, mr_id):
        #changes the meta of role_id to mr_id, then checks the old one to see if it has no children
        mr_id = str(mr_id)
        self._db_controler.update("roles", "parent_meta", mr_id, "id", role_id)

    def resetMR(self, roleID1):
        self._db_controler.update_reset_mr(roleID1)

    def mergeMR(self, metaID1, metaID2):
        metaID1 = str(metaID1)
        metaID2 = str(metaID2)
        if (metaID1 != metaID2):
            lowest = min(metaID1, metaID2)
            highest = max(metaID1, metaID2)
            self._db_controler.update("roles", "parent_meta", highest, "parent_meta", lowest)

    def actorSwap(self, roleID1, roleID2):
        if roleID1 != roleID2:
            parent_meta_1 = self._db_controler.select("parent_meta", "roles", "id", roleID1)
            parent_meta_2 = self._db_controler.select("parent_meta", "roles", "id", roleID2)
            
            if parent_meta_1 != parent_meta_2:
                self.mergeMR(parent_meta_1, parent_meta_2)
            
            parent_meta = self._db_controler.select("parent_meta", "roles", "id", roleID1)
            
            swap_id = self._db_controler.select_max("actor_swap_id", "roles","parent_meta", parent_meta)
            if swap_id is not None:
                swap_id += 1
            else:
                swap_id = 1
            #Select Max() gets the highest in that column
            self._db_controler.update("roles", "actor_swap_id", swap_id, "id", roleID1, bool_or=True, second_argument_column="id", second_argument_value=roleID2)
        else:
            print("Actor Swap Error: IDs are the same.")
        
    def removeActorSwap(self, roleID1):
        actor_swap_data = self._db_controler.select("actor_swap_id, parent_meta", "roles", "id", roleID1)
        actor_swap_id = actor_swap_data[0]
        actor_swap_parent = actor_swap_data[1]
        
        #get the id  so we can check if we orphaned an actor-swap
        
        self._db_controler.update("roles", "actor_swap+id", 0, "id", roleID1)
        
        #we don't need to redo the actor-swap ids if a number is skipped
        
        #This will set any orphaned (one-child) actor_swaps to 0
        if actor_swap_id != 0:
            result = self._db_controler.select("id","roles","actor_swap_id",actor_swap_id, bool_and=True, second_argument_column="parent_meta", second_actor_value=actor_swap_parent)
            if len(result) < 2 and len(result) != 0:
                swap_id_to_clear = result[0][0]
                self._db_controler.update("roles","actor_swap_id", 0, "id", swap_id_to_clear)

    def commit(self):
        self._db_controler.commit()
#TODO a hsitory in each role of it's prior Mr's name, including an option to revert the whole change. Changes have change Id's. 
# You can revert an mr change by ID without changing the ID's