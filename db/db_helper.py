import sqlite3


class DbHelper(object):
    conn = sqlite3.connect('db/db.db')
    cursor = conn.cursor()
    cursor.execute('create table if not exists t_client (app_id text, security text, flag_login integer)')
    conn.commit()

    @staticmethod
    def insert_client(app_id, security):
        DbHelper.cursor.execute('insert into t_client (app_id,security) values (?,?)', (app_id, security))
        DbHelper.conn.commit()

    @staticmethod
    def query_client():
        DbHelper.cursor.execute('select * from t_client')
        return DbHelper.cursor.fetchone()

