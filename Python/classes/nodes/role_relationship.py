import logging

class RoleRelationship():
    def __init__(self, id, role1_id, role1_name, role2_id, role2_name, type, db_control):
        self.id = id
        self.role1_id = role1_id
        self.role1_name = role1_name
        self.role2_id = role2_id
        self.role2_name = role2_name
        self.type = type
        
        self.db_control = db_control
        
        self.other_role_mr = None
        self.other_role_name = None

    def __lt__(self, other):
        return self.type.lower() < other.type.lower()

    def get_other_parent_meta(self, role_id):
        if role_id == self.role1_id:
            self.other_role_mr = self.db_control.get_parent_meta(self.role2_id)
            self.other_role_name = self.role2_name
        elif role_id == self.role2_id:
            self.other_role_mr = self.db_control.get_parent_meta(self.role1_id)
            self.other_role_name = self.role1_name
        else:
            logging.error(f'Error: role {role_id} not a member of relationship {self.id}')
