import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("DB_NAME", "scheme_matching_db")
}


def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            return connection

    except Error as e:
        print("Database connection error:", e)

    return None


def get_entrepreneur_by_id(en_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM entrepreneurs
        WHERE en_id = %s
    """

    cursor.execute(query, (en_id,))
    entrepreneur = cursor.fetchone()

    cursor.close()
    connection.close()

    return entrepreneur


def get_all_schemes():
    connection = get_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM schemes
    """

    cursor.execute(query)
    schemes = cursor.fetchall()

    cursor.close()
    connection.close()

    return schemes


def get_eligibility_rules(sch_id):
    connection = get_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM eligibility
        WHERE sch_id = %s
    """

    cursor.execute(query, (sch_id,))
    rule = cursor.fetchone()

    cursor.close()
    connection.close()

    return rule


def insert_match(en_id, sch_id, score, status="Recommended"):
    connection = get_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    query = """
        INSERT INTO scheme_matches
        (en_id, sch_id, match_confidence_score, status)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (en_id, sch_id, score, status))

    connection.commit()

    cursor.close()
    connection.close()

    return True
