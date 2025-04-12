import json
import sqlite3
from datetime import datetime

from flask_login import UserMixin


class UserManagement(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


class Users:
    def __init__(self, db: str) -> None:
        """
        The constructor of Users table class.

        :param db: Represents the name(or path) of the SQLite database
        :type db_file: str
        """
        self.__db = db

    def setup(self) -> None:
        """
        Creates the users table in database.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        # Create users table
        sql = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        phone TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        fname TEXT NOT NULL,
        lname TEXT NOT NULL,
        register_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        is_staff BOOLEAN DEFAULT 0,
        is_admin BOOLEAN DEFAULT 0
        )"""
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def add_user(
            self,
            phone: str,
            password: str,
            fname: str,
            lname: str,
            register_date=None,
            last_login=None,
            is_active: bool = True,
            is_staff: bool = False,
            is_admin: bool = False
    ) -> bool:
        """
        Inserts a new user into the database.

        :param phone: The phone of the user
        :type phone: str
        :param password: User's password
        :type password: str
        :param fname: The first name of the user
        :type fname: str
        :param lname: The last name of the user
        :type lname: str
        :param register_date: The date and time when the user
        is registered (optional)
        :param last_login: The date and time of the
        user's last login (optional)
        :param is_active: Indicates whether the user
        is currently active or not. defaults to True
        :type is_active: bool (optional)
        :param is_admin: Indicates whether the user being added
        is an admin or not. defaults to False
        :type is_admin: bool (optional)
        :return: a boolean that includes
        the status of adding a new user to the database
        """
        if not register_date:
            register_date = datetime.now()
        if not last_login:
            last_login = datetime.now()

        sql = """INSERT OR IGNORE INTO users (
        phone, password, fname, lname, register_date,
        last_login, is_active, is_staff, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        param = (
            phone,
            password,
            fname,
            lname,
            register_date,
            last_login,
            is_active,
            is_staff,
            is_admin
        )
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, param)
            self.conn.commit()
            self.conn.close()
            print("User added successfully")
            return True
        except Exception as e:
            print(e)
            return False

    def update_user_info(
            self,
            id: int,
            phone: str,
            fname: str,
            lname: str,
            grade: int,
    ) -> bool:
        """
        Update user parameters in the database based on user ID.

        :param id: The ID of the user to update
        :type id: int
        :param phone: New phone for the user
        :type phone: str
        :param fname: New first name for the user
        :type fname: str
        :param lname: New last name for the user
        :type lname: str
        :param grade: New grade for the user
        :type grade: int
        :return: a boolean that includes
        the status of updating the new user's info.
        """
        sql = """UPDATE users SET
        phone = ?, fname = ?,lname = ?, grade = ?
        WHERE id = ?
        """
        params = (phone, fname, lname, grade, id)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False

    def update_user_password(self, id, password) -> bool:
        """
        Update user parameters in the database based on user ID.

        :param id: The ID of the user to update
        :type id: int
        :param password: New password for the user
        :type password: str
        :return: a boolean that includes
        the status of updating the user's password.
        """
        sql = "UPDATE users SET password = ? WHERE id = ?"
        params = (password, id)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False

    def update_user_last_login(self, id) -> bool:
        """
        Update a user last login date in the database based on user ID.

        :param id: The ID of the user to update
        :type id: int
        :return: a boolean that includes
        the status of updating the user's last login.
        """
        last_login = datetime.now()
        sql = "UPDATE users SET last_login = ? WHERE id = ?"
        params = (last_login, id)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False

    def get_user_id(self, phone: str) -> int:
        """
        Get a user's id from db.

        :param phone: The phone of the user
        :type phone: str
        :return: an integer that includes user's id.
        """
        sql = "SELECT id FROM users WHERE phone = ?"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (phone,))
            row = cursor.fetchone()
            id = 0
            if row:
                id = row[0]
            self.conn.close()
            return id
        except Exception as e:
            print(e)
            return 0

    def get_user(self, id: int) -> dict:
        """
        Retrieves a user from a SQLite database based on their ID.

        :param id: Represents the unique identifier of a user
        :type id: int
        :return: user object.
        """
        sql = "SELECT * FROM users WHERE id = ?"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            user = {}
            if row:
                column_names = [desc[0] for desc in cursor.description]
                user = dict(zip(column_names, row))
            self.conn.close()
            return user
        except Exception as e:
            print(e)
            return {}


class SubscribedUsers:
    def __init__(self, db: str) -> None:
        """
        Constructor for the SubscribedUsers table class.

        :param db: Path to the SQLite database file
        """
        self.__db = db

    def setup(self) -> None:
        """
        Creates the Subscribed_users table in the database.
        """
        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            # Create the Subscribed_users table
            sql = """
            CREATE TABLE IF NOT EXISTS Subscribed_users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                national_id TEXT NOT NULL UNIQUE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            cursor.execute(sql)
            conn.commit()

    def add_subscribed_user(self, user_id: int, national_id: str) -> bool:
        """
        Adds a new subscribed user to the database.

        :param user_id: ID of the user from the users table
        :param national_id: National ID of the subscribed user
        :return: True if added successfully, False otherwise (e.g., user doesn't exist or duplicate national_id)
        """
        try:
            with sqlite3.connect(self.__db) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                # Check if the user_id exists in users table
                cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                if cursor.fetchone() is None:
                    print("User ID not found.")
                    return False
                # Insert into Subscribed_users table
                cursor.execute("""
                    INSERT INTO Subscribed_users (user_id, national_id)
                    VALUES (?, ?)
                """, (user_id, national_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def get_all_national_ids(self) -> list[str]:
        """
        Retrieves all national_id values from the Subscribed_users table.

        :return: A list of national_id strings
        """
        try:
            with sqlite3.connect(self.__db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT national_id FROM Subscribed_users")
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"Error retrieving national_ids: {e}")
            return []


class DBHelper:
    def __init__(self, db_file: str = "database.db") -> None:
        """
        The constructor of DataBase helper class.

        :param db_file: The `db_file` represents the name(or path)
        of the SQLite database
        :type db_file: str (optional)
        """
        self.db_file = db_file
        self.users = Users(self.db_file)
        self.subscribed_users = SubscribedUsers(self.db_file)


    def create_tables(self):
        self.users.setup()
        self.subscribed_users.setup()
        print("Database and tables created successfully!")


if __name__ == "__main__":
    db_helper = DBHelper()
    db_helper.create_tables()