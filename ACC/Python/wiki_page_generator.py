
#TODO update database_controll to match the expectations here

class WikiPageGenerator:
    def __init__(self, db_control, baseID, base_is_actor=False, level=1):
        self._db_control = db_control
        self.base_is_actor = base_is_actor
        self.baseID = baseID
        

        self._layer_is_actor = False
        self.level = level
        self.displayed_mrs = []
        self.displayed_actors = []
        self.halfway_mrs
        if self._base_is_actor:
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
        if (self._level*10 // 1 % 10) == 5:
        #if the last digit is five when you move the decimal
            self._point_five = True
            self._level -= 0.5
        self._level = int(self.level)

    def _update_displayed(self,parent, is_actor):
        if is_actor:
            self._displayed_actors.append(parent)
        else:
            self._displayed_mrs.append(parent)

    def _set_halfway(self):
        #the halfway-displayed mrs, when an actor only plays some of an mr's roles
        if self._layer_is_actor:
            for parent in self._inactive:
                for role in parent.roles:
                    for mr in self.halfway_mrs:
                        if role.parent_mr == mr.id:
                            in_active = True
                            mr.add_role(role)
                    if (not in_active):
                        halfway_mr = self._db_control.get_mr(role.parent_meta)
                        halfway_mr.add_role(role)
                        self.halfway_mrs.append(halfway_mr)

    def _set_point_five_roles(self):
        if(self._base_is_actor):
            #an actor at 0.5 only does actor_swaps/ the same continuity, different actor
            #1 would be same character in all continuities
            pass
            #TODO
            #for each mr in halfway
                #for each role in parent.roles
                    #if role.actor_swap_id != 0:
                        #for role in db.get_actor_swaps(mr_id, actor_swap_id):
                            #mr.add_role(role)

    def set_content(self):
        self._layer_is_actor = self.base_is_actor

        self._check_if_point_five()
        while self._layer < self.level:
            self._temp_inactive = []
            for parent in self.inactive:
                parent.set_roles(self._db_control.get_roles(parent.id, self._layer_is_actor))
                if self._layer_is_actor:
                    for role in parent.roles:
                        for mr in self.displayed_mrs:
                            if role.parent_meta == mr.id:
                                in_active = True
                        if(not in_active):
                            self._temp_inactive.append(self._db_control.get_mr(role.parent_meta))
                        else:
                            in_active = False

                else:
                    for role in parent.roles:
                        for actor in self.displayed_actors:
                            if role.parent_actor == actor.id:
                                in_active = True
                        if(not in_active):
                            self._temp_inactive.append(self._db_control.get_actor(role.parent_actor))
                self._update_displayed(parent, self._layer_is_actor)
            self._inactive = self._temp_inactive
        
        self._set_halfway()
        
        self._set_point_five_roles()
        #TODO we'l have to return the Hub Sigils (when we integrate into flask/ the graphviz)