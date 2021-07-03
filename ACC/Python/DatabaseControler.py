import Constants
import sqlite3  
import traceback

class DatabaseControler():
    _database = Constants.DATABASE
    _connection = None
    _cursor = None

    def create_connection(self):
        try:
            self._connection = sqlite3.connect(self._database, check_same_thread=False)
            self._cursor = self._connection.cursor()
        except sqlite3.Error:
            traceback.print_exc()

    def update(self, table_name, column, column_values, where, where_values):
        update_sql = "UPDATE {} SET {}=? WHERE {}=?".format(table_name.lower(), column.lower(), where.lower())
        self._cursor.execute(update_sql, column_values + where_values)
    
    def commit(self):
        self._connection.commit()

def main():
    databaseControler = DatabaseControler()
    databaseControler.create_connection()
    mr_id = str(6)
    role_id = "0000284-2402207-1"
    databaseControler.update("roles", "parent_meta", [mr_id] ,"id", [role_id])
    databaseControler.commit()

main()