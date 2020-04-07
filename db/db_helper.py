import sqlite3


class DbHelper(object):
    conn = sqlite3.connect('db/db.db')
    cursor = conn.cursor()
    cursor.execute('create table if not exists t_client (row_id text, app_id text, security text)')
    cursor.execute(
        'create table if not exists t_user (ID INTEGER PRIMARY KEY AUTOINCREMENT,row_id text,name text,color text,client_id text)')
    conn.commit()

    @staticmethod
    def insert_client(row_id, app_id, security):
        DbHelper.cursor.execute('insert into t_client (row_id, app_id,security) values (?,?,?)',
                                (row_id, app_id, security))
        DbHelper.conn.commit()

    @staticmethod
    def query_client():
        DbHelper.cursor.execute('select * from t_client')
        return DbHelper.cursor.fetchone()

    @staticmethod
    def delete_client():
        DbHelper.cursor.execute('delete from t_client')
        DbHelper.cursor.execute('delete from t_user')
        DbHelper.conn.commit()

    @staticmethod
    def insert_user(row_id, name, color, client_id):
        DbHelper.cursor.execute('insert into t_user (row_id,name,color,client_id) values (?,?,?,?)',
                                (row_id, name, color, client_id))
        DbHelper.conn.commit()
        DbHelper.cursor.execute('select last_insert_rowid() from t_user')
        return DbHelper.cursor.fetchone()[0]

    @staticmethod
    def query_users():
        DbHelper.cursor.execute('select * from t_user')
        return DbHelper.cursor.fetchall()

    @staticmethod
    def delete_users():
        DbHelper.cursor.execute('delete from t_user')
        DbHelper.conn.commit()
