class WikiPageGenerator:
    def __init__(self, db_control, baseID, base_is_actor=False, level=1):
        self._db_control = db_control
        self.base_is_actor = base_is_actor
        self.baseID = baseID
        print(self.baseID)

        self._layer_is_actor = False
        self.level = level
        self.displayed_mrs = []
        self.displayed_actors = []
        self.halfway_mrs = []
        if self.base_is_actor:
            self._inactive = [self._db_control.get_actor(self.baseID)]
        else:
            self._inactive = [self._db_control.get_mr(self.baseID)]
        self._temp_inactive = []
        self.base_name = self._inactive[0].name
        self._point_five_roles = []
        self._point_five = False
        self._check_if_point_five()
        self._layer = 0
    
    def _check_if_point_five(self):
        if (self.level*10 // 1 % 10) == 5:
        #if the last digit is five when you move the decimal
            self._point_five = True
            self.level -= 0.5
        self.level = int(self.level)

    def _update_displayed(self,parent, is_actor):
        if is_actor:
            self.displayed_actors.append(parent)
            print(parent.name)
        else:
            self.displayed_mrs.append(parent)
            print(parent.name)

    def _set_halfway(self):
        #the halfway-displayed mrs, when an actor only plays some of an mr's roles
        for parent in self._inactive:
            for role in parent.roles:
                in_active = False
                for mr in self.halfway_mrs:
                    if role.parent_meta == mr.id:
                        in_active = True
                        mr.add_role(role)
                if (not in_active):
                    halfway_mr = self._db_control.get_mr(role.parent_meta)
                    halfway_mr.add_role(role)
                    self.halfway_mrs.append(halfway_mr)

    def _set_point_five_roles(self):
        if(self.base_is_actor):
            #an actor at 0.5 only does actor_swaps/ the same continuity, different actor
            #1 would be same character in all continuities
            for mr in self.halfway_mrs:
                mr.get_actor_swaps()

    #TODO get actor relationships as a class variable - a list of ids paired with names
    #actor.relationships_spouse for actor in displayed_actors
    #link relationships - not in displayed_actors
    #plaintext relationships - in displayed_actors

    #TODO get role relationships as a class variable
    #get list of "other" role id's
    #get parent_meta for each "other" - can't be a role.parent_meta, because we don't need the whole role
        #db_cont.get_parent_meta(role_id)
    #link_relationship_spouce - etc if mr in displayed_mrs
    #plaintext_etc

    #TODO a list of power templates, 
       #with duplicate checking
    #TODO
        #a list of other powers
        #check for duplicates

    #TODO list of actor skills
        #check duplicates

    def set_content(self):
        self._layer_is_actor = self.base_is_actor
        #TODO Mrs or actorsa are borked, and it's just getting carrie fisher, too
        self._check_if_point_five()
        while self._layer < self.level:
            self._temp_inactive = []
            for parent in self._inactive:
                parent.set_roles(self._db_control.get_roles(parent.id, self._layer_is_actor))
                if self._layer_is_actor:
                    self._set_halfway()

                else: #eg, there are unprocessed mrs in Inactive
                    for role in parent.roles:
                        in_active = False
                        for actor in self.displayed_actors:
                            if role.parent_actor == actor.id:
                                in_active = True
                        if(not in_active):
                            self._temp_inactive.append(self._db_control.get_actor(role.parent_actor))
                self._update_displayed(parent, self._layer_is_actor)
            self._layer += 1
            self._layer_is_actor = not self._layer_is_actor
            self._inactive = self._temp_inactive
        
        self._set_point_five_roles()
        #TODO we'l have to return the Hub Sigils (when we integrate into flask/ the graphviz)