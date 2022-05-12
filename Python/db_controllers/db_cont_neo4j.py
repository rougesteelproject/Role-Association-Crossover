from Python.database_controller import DatabaseController
import constants

class DatabaseControllerNeo(DatabaseController):
    def __init__(self):
        super().__init__()

        self._database_uri = constants.NEO4J_URI
