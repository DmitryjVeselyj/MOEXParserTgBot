import sqlite3


# without sqlaclchemy, hardcore only

class GenericDao:
    def __init__(self, db_path) -> None:
        self._connection = sqlite3.connect(db_path)

    def select(self, table, columns=None, condition=None):  # TODO add group by. order, limit and others
        cursor = self._connection.cursor()
        query = (f'select {",".join(columns)}' if columns is not None else 'select *') + f' from {table}'

        if condition is not None:
            query += f' where {condition}'

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()
        return data

    @classmethod
    def _form_insert_query(cls, table, data):
        query = f'insert into {table} ('
        for key in data.keys():
            query += key + ','

        query = query[:-1] + ') values ('

        for value in data.values():
            query += '?' + ','

        query = query[:-1] + ')'

        return query

    def insert(self, table, data: dict):
        cursor = self._connection.cursor()
        query = self._form_insert_query(table, data)

        cursor.execute(query, tuple(data.values()))

        self._connection.commit()
        cursor.close()

    def delete(self, table, condition=None):
        cursor = self._connection.cursor()
        query = f'''
                delete from {table}
                '''
        if condition is not None:
            query += f' where {condition}'

        cursor.execute(query)

        self._connection.commit()
        cursor.close()

    def update(self, table, data: dict, condition):
        cursor = self._connection.cursor()
        query = f'''
                update {table}
                set 
                '''

        query += ','.join(f'{key} = "{value}"' for key, value in data.items())

        if condition is not None:
            query += f' where {condition}'

        cursor.execute(query)

        self._connection.commit()
        cursor.close()

    def __del__(self):
        self._connection.close()
