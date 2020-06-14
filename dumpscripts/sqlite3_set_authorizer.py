# sqlite3_set_authorizer.py

import sqlite3

db_filename = 'todo.db'


def authorizer_func(action, table, column, sql_location, ignore):
    print('\nauthorizer_func({}, {}, {}, {}, {})'.format(
        action, table, column, sql_location, ignore))

    response = sqlite3.SQLITE_OK  # siamo permissivi per default

    if action == sqlite3.SQLITE_SELECT:
        print('richiesta permessi per eseguire una istruzione select')
        response = sqlite3.SQLITE_OK

    elif action == sqlite3.SQLITE_READ:
        print('richiesta accesso a colonna {}.{} da {}'.format(
            table, column, sql_location))
        if column == 'dettagli':
            print('  colonna dettagli ignorata')
            response = sqlite3.SQLITE_IGNORE
        elif column == 'priorita':
            print('  negato accesso alla colonna priorita')
            response = sqlite3.SQLITE_DENY

    return response


with sqlite3.connect(db_filename) as conn:
    conn.row_factory = sqlite3.Row
    conn.set_authorizer(authorizer_func)

    print('Utilizzo di SQLITE_IGNORE per nascondere un valore di colonna:')
    cursor = conn.cursor()
    cursor.execute("""
    select id, dettagli from compito where progetto = 'pymotw-it 3'
    """)
    for row in cursor.fetchall():
        print(row['id'], row['dettagli'])

    print('\nUtilizzo di SQLITE_DENY per negare accssso ad una colonna:')
    cursor.execute("""
    select id, priorita from compito where progetto = 'pymotw-it 3'
    """)
    for row in cursor.fetchall():
        print(row['id'], row['dettagli'])
