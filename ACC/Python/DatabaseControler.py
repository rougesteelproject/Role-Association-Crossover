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
    
    def select(self, select_columns, table_name, where, where_value , bool_and = False, bool_or = False, second_argument_column = "", second_argument_value = ""):
        select_sql = "SELECT {} FROM {} WHERE {}=?".format(select_columns.lower(),table_name.lower(),where.lower())
        if bool_and:
            select_sql = select_sql + "AND {}=?".format(second_argument_column.lower())
        elif bool_or:
            select_sql = select_sql + "OR {}=?".format(second_argument_column.lower())
        
        if second_argument_value != '':
            values = (where_value, second_argument_value,)
        else:
            values = where_value
        self._cursor.execute(select_sql, (values,))
        return self._cursor.fetchall()[0]

    def commit(self):
        self._connection.commit()

def main():
    databaseControler = DatabaseControler()
    databaseControler.create_connection()
    actor_swap_id = "1"
    actor_swap_parent = "6"
    result = databaseControler.select("id", "roles", "actor_swap_id", actor_swap_id, bool_and=True, second_argument_column="parent_meta", second_argument_value=actor_swap_parent)
    print(result)

main()