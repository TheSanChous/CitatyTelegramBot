from config import DATABASE_URL
import psycopg2


def ensure_subscribe_user(chat_id: object):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    cursor.execute(f'SELECT "Id" FROM public."Users" WHERE "ChatId" = {chat_id};')
    result = cursor.fetchone()
    if result is None:
        cursor.execute(f'INSERT INTO public."Users" ("ChatId") VALUES ({chat_id});')
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False


def add_to_saves(chat_id: int, save: str) -> bool:
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    save = save.replace("'", '')
    cursor.execute(f'INSERT INTO public."Quotes" ("content", "userId") VALUES (\'{save}\', {chat_id})')
    connection.commit()
    connection.close()


def get_user_saves(chat_id: int) -> list:
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    cursor.execute(f'SELECT content FROM public."Quotes" WHERE "userId"={chat_id};')
    return cursor.fetchall()


def try_delete_user_save(chat_id: int, save: str):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    save = save.replace("'", '')
    cursor.execute(f'DELETE FROM public."Quotes" WHERE "userId" = {chat_id} AND "content" = \'{save}\';')
    connection.commit()
    connection.close()
