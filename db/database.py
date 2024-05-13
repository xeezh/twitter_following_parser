import sqlite3
import os


class DB:
    def __init__(self):
        while self.__connection is None:
            self.__connection = self.__create_connection()

    #
    # Internal functions & variables
    #

    __connection = None

    @staticmethod
    def __create_connection():
        try:
            # пытаемся подключиться к базе данных
            path = os.getcwd() + '\\db\\database.db'
            conn = sqlite3.connect(path)
            return conn
        except Exception as e:
            # в случае сбоя подключения будет выведено сообщение в STDOUT
            print(f'Can`t establish connection to database: {str(e)}')
            sleep(1)

    @staticmethod
    def __fetch(cursor):
        try:
            return cursor.fetchall()
        except Exception as e:
            print(e)
            return None

    def __request(self, sql):
        free_con = self.__connection

        cur = free_con.cursor()
        free_con.commit()
        cur.execute(sql)

        response = self.__fetch(cur)

        free_con.commit()

        return response

    def __new_user(self, user_id):
        sql = f"INSERT INTO user \n" \
              f"VALUES ('{user_id}', NULL, NULL) \n" \
              f"RETURNING *"
        return self.__request(sql)

    #
    # External functions
    #

    def get_user(self, user_id: str) -> dict:
        sql = f"SELECT * \n" \
              f"FROM user \n" \
              f"WHERE user_id = '{user_id}'"
        try:
            resp = self.__request(sql)
            data = {
                "user_id": resp[0][0],
                "proxy": resp[0][1],
                "token": resp[0][2]
            }
            return data
        except:
            resp = self.__new_user(user_id)
            data = {
                "user_id": resp[0][0],
                "proxy": resp[0][1],
                "token": resp[0][2]
            }
            return data

    def set_proxy(self, user_id: str, proxy: str) -> None:
        sql = f"UPDATE user \n" \
              f"SET proxy='{proxy}' \n" \
              f"WHERE user_id = '{user_id}'"
        self.__request(sql)

    def set_token(self, user_id: str, token: str) -> None:
        sql = f"UPDATE user \n" \
              f"SET token='{token}' \n" \
              f"WHERE user_id = '{user_id}'"
        self.__request(sql)