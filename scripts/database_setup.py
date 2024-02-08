import pymysql
import logging

def setup_database():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="root"
    )

    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS db")
        cursor.execute("USE db")
        logging.info('[itsKios-09]: Database "db" created or already exists')

    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """)
        logging.info('[itsKios-09]: Table "users" created or already exists')

    connection.commit()
    connection.close()
    logging.info('[itsKios-09]: Database setup script execution completed')

    print('[itsKios-09]: Database setup script execution completed')
