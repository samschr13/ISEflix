from flask import g
from flask_mysqldb import MySQL
from MySQLdb import OperationalError


def get_db(app=None):
    if "db" not in g:
        g.db = MySQL(app)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        try:
            db.connection.close()
        except OperationalError:
            pass


def init_app(app):
    app.teardown_appcontext(close_db)
    get_db(app)


def insert_user(username, password):
    conn = get_db().connection
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO user (username, password) VALUES ('{username}', '{password}')"
    )
    conn.commit()
    cursor.close()


def get_user_by(key, value):
    conn = get_db().connection
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM user WHERE {key} = '{value}'")
    user = cursor.fetchone()
    cursor.close()
    return user


def get_payment_info(user_id, cursor=None):
    close = False
    if cursor is None:
        conn = get_db().connection
        cursor = conn.cursor()
        close = True
    cursor.execute(f"SELECT * FROM payment WHERE user_id = '{user_id}'")
    payment_info = cursor.fetchone()
    if close:
        cursor.close()
    return payment_info


def update_subscription(user_id, new_status):
    conn = get_db().connection
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE user SET subscription = '{new_status}' WHERE id = '{user_id}'"
    )
    conn.commit()
    cursor.close()


def update_payment_info(user_id, card_number, expiration, cvv):
    conn = get_db().connection
    cursor = conn.cursor()
    if get_payment_info(user_id, cursor=cursor):
        cursor.execute(
            f"UPDATE payment SET card_number = '{card_number}', expiration = '{expiration}', cvv = '{cvv}' WHERE user_id = '{user_id}'"
        )
    else:
        cursor.execute(
            f"INSERT INTO payment (user_id, card_number, expiration, cvv) VALUES ('{user_id}', '{card_number}', '{expiration}', '{cvv}')"
        )
    conn.commit()
    cursor.close()


def update_password(user_id, new_password):
    conn = get_db().connection
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE user SET password = '{new_password}' WHERE id = '{user_id}'"
    )
    conn.commit()
    cursor.close()
