import json
import sqlite3
from datetime import datetime, timedelta
import jdatetime
from typing import Dict, List

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

    def get_all_subscribers(self) -> List[Dict]:
        
        """
        Retrieves all subscribers from the Subscribed_users table.

        :return: A list of dictionaries containing subscriber information.
        """
        try:
            with sqlite3.connect(self.__db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, national_id FROM Subscribed_users")
                rows = cursor.fetchall()
                return [{'user_id': row[0], 'national_id': row[1]} for row in rows]
        except Exception as e:
            print(f"Error retrieving subscribers: {e}")
            return []

    def get_subscriber_by_user_id(self, user_id: int) -> Dict:
        """
        Retrieves a subscriber's information by their user ID.

        :param user_id: ID of the user to retrieve
        :return: A dictionary containing subscriber information or an empty dictionary if not found
        """
        try:
            with sqlite3.connect(self.__db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT national_id FROM Subscribed_users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    return {'user_id': user_id, 'national_id': row[0]}
                return {}
        except Exception as e:
            print(f"Error retrieving subscriber by user_id: {e}")
            return {}

class TableReservation:
    def __init__(self, db: str) -> None:
        self.__db = db

    def setup(self) -> None:
        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS table_reservation (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    hour INTEGER NOT NULL,
                    table_no INTEGER NOT NULL CHECK(table_no IN (1, 2, 3, 4)),
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def add_reservation(self, user_id: int, jalali_date: str, hour: int, table_no: int) -> bool:
        """
        Adds a new reservation for a user with a given Jalali date, hour, and table number.
        """
        try:
            # Convert Jalali date to Gregorian
            jdate = jdatetime.datetime.strptime(jalali_date, "%Y/%m/%d")
            gregorian_date = jdate.togregorian().date()  # Convert to Gregorian date
            
            # Check if the table is already reserved at this hour
            if not self.is_table_available(gregorian_date, hour, table_no):
                print(f"Table {table_no} is already reserved for {gregorian_date} at {hour}:00.")
                return False

            # Insert into table_reservation table
            with sqlite3.connect(self.__db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO table_reservation (user_id, date, hour, table_no)
                    VALUES (?, ?, ?, ?)
                """, (user_id, gregorian_date, hour, table_no))
                conn.commit()

            print(f"Reservation for table {table_no} on {gregorian_date} at {hour}:00 added successfully.")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def is_table_available(self, date: str, hour: int, table_no: int) -> bool:
        """
        Checks if the table is available for the given date and hour.
        """
        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM table_reservation
                WHERE date = ? AND hour = ? AND table_no = ?
            """, (date, hour, table_no))
            return cursor.fetchone() is None

    def get_table_status(self, date: str, hour: int) -> dict:
        """
        Gets the reservation status of each table for a given date and hour.
        
        :param date: Date in Gregorian format (YYYY-MM-DD).
        :param hour: Hour in 24-hour format (e.g., 15 for 3 PM).
        
        :return: A dictionary with table numbers as keys and reservation status as values.
                e.g. {'table1': False, 'table2': True, ...}
        """
        table_status = {'table1': False, 'table2': False, 'table3': False, 'table4': False}
        jdate = jdatetime.datetime.strptime(date, "%Y/%m/%d")
        gregorian_date = jdate.togregorian().date()
        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_no FROM table_reservation
                WHERE date = ? AND hour = ?
            """, (gregorian_date, hour))

            reserved_tables = cursor.fetchall()
            reserved_tables = [row[0] for row in reserved_tables]

            # Mark reserved tables as True
            for table_no in reserved_tables:
                if f'table{table_no}' in table_status:
                    table_status[f'table{table_no}'] = True

        return table_status

    def get_table_availability_for_now(self) -> dict:
        """
        Returns the availability status of all tables for now and the specified hour.
        
        :return: A dictionary with table availability status, where key is 'table1', 'table2', etc., 
                and the value is True (reserved) or False (available).
        """
        # Get today's Gregorian date
        today = jdatetime.datetime.now().togregorian().date()
        hour = datetime.now().hour

        # Initialize the availability dictionary for each table
        availability = {
            'table1': False,
            'table2': False,
            'table3': False,
            'table4': False
        }

        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()

            # Query reservations for today and check against the requested hour
            cursor.execute("""
                SELECT table_no, hour FROM table_reservation
                WHERE date = ? AND (hour = ? OR (hour = ? + 2))
            """, (today, hour, hour))  # We check both for the exact hour and the one before (for 2-hour reservations)

            rows = cursor.fetchall()

            for row in rows:
                table_no = row[0]
                availability[f'table{table_no}'] = True

        return availability


class RequestedBooks:
    def __init__(self, db: str) -> None:
        self.__db = db

    def setup(self) -> None:
        """
        Creates the requested_books table in the database.
        """
        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requested_books (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    author TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    subject TEXT,
                    description TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def add_requested_book(self, user_id: int, name: str, author: str, publisher: str, subject: str = None, description: str = None) -> bool:
        """
        Adds a new requested book to the requested_books table.

        :param user_id: ID of the user who requested the book.
        :param name: Name of the book.
        :param author: Author of the book.
        :param publisher: Publisher of the book.
        :param subject: Subject of the book (optional, may be null).
        :param description: Description of the book (optional, may be null).
        :return: True if the book was added successfully, False otherwise.
        """
        try:
            with sqlite3.connect(self.__db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO requested_books (user_id, name, author, publisher, subject, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, name, author, publisher, subject, description))
                conn.commit()
            return True
        except Exception as e:
            print(f"An error occurred to add requested book: {e}")
            return False 

    def get_all_requested_books(self) -> dict:
        """
        Returns all requested books as a dictionary.

        :return: A dictionary where keys are the book IDs and values are dictionaries with book details.
        """
        requested_books = {}

        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, name, author, publisher, subject, description FROM requested_books")
            rows = cursor.fetchall()

            for row in rows:
                book_id, user_id, name, author, publisher, subject, description = row
                requested_books[book_id] = {
                    'user_id': user_id,
                    'name': name,
                    'author': author,
                    'publisher': publisher,
                    'subject': subject,
                    'description': description
                }

        return requested_books


class DonateBooks:
    def __init__(self, db: str) -> None:
        self.__db = db

    def setup(self) -> None:
        """
        Creates the donate_books table in the database.
        """
        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS donate_books (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    author TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    address TEXT NOT NULL,
                    subject TEXT,
                    description TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def add_donated_book(self, user_id: int, name: str, author: str, publisher: str, address: str, subject: str = None, description: str = None) -> bool:
        """
        Adds a new donated book to the donate_books table.

        :param user_id: ID of the user who donated the book.
        :param name: Name of the book.
        :param author: Author of the book.
        :param publisher: Publisher of the book.
        :param address: Address related to the donation.
        :param subject: Subject of the book (optional, may be null).
        :param description: Description of the book (optional, may be null).
        :return: True if the book was added successfully, False otherwise.
        """
        try:
            with sqlite3.connect(self.__db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO donate_books (user_id, name, author, publisher, address, subject, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, name, author, publisher, address, subject, description))
                conn.commit()
            return True
        except Exception as e:
            print(f"An error occurred to add donated book: {e}")
            return False

    def get_all_donated_books(self) -> dict:
        """
        Returns all donated books as a dictionary.

        :return: A dictionary where keys are the book IDs and values are dictionaries with book details.
        """
        donated_books = {}

        with sqlite3.connect(self.__db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, name, author, publisher, address, subject, description FROM donate_books")
            rows = cursor.fetchall()

            for row in rows:
                book_id, user_id, name, author, publisher, address, subject, description = row
                donated_books[book_id] = {
                    'user_id': user_id,
                    'name': name,
                    'author': author,
                    'publisher': publisher,
                    'address': address,
                    'subject': subject,
                    'description': description
                }

        return donated_books


class Books:
    def __init__(self, db: str) -> None:
        self.__db = db

    def setup(self) -> None:
        """
        Creates the books table in the database.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            UID TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            author TEXT NOT NULL,
            publisher TEXT NOT NULL,
            price REAL,
            location TEXT NOT NULL
        )
        """
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def add_book(self, UID: str, name: str, author: str, publisher: str, price: float, location: str) -> bool:
        sql = """
        INSERT INTO books (UID, name, author, publisher, price, location)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (UID, name, author, publisher, price, location))
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False

    def get_all_books(self) -> List[Dict]:
        sql = "SELECT * FROM books"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            books = []
            column_names = [desc[0] for desc in cursor.description]
            for row in rows:
                books.append(dict(zip(column_names, row)))
            self.conn.close()
            return books
        except Exception as e:
            print(e)
            return []

    def get_book_by_id(self, book_id: int) -> Dict:
        return self.__get_book_by_field("id", book_id)

    def get_book_by_uid(self, uid: str) -> Dict:
        return self.__get_book_by_field("UID", uid)

    def get_book_by_name(self, name: str) -> Dict:
        return self.__get_book_by_field("name", name)

    def get_book_by_author(self, author: str) -> Dict:
        return self.__get_book_by_field("author", author)

    def get_book_by_publisher(self, publisher: str) -> Dict:
        return self.__get_book_by_field("publisher", publisher)

    def get_all_books_by_author(self, author: str) -> List[Dict]:
        return self.__get_all_books_by_field("author", author)

    def get_all_books_by_publisher(self, publisher: str) -> List[Dict]:
        return self.__get_all_books_by_field("publisher", publisher)

    def __get_book_by_field(self, field: str, value) -> Dict:
        sql = f"SELECT * FROM books WHERE {field} = ? LIMIT 1"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (value,))
            row = cursor.fetchone()
            self.conn.close()
            if row:
                column_names = [desc[0] for desc in cursor.description]
                return dict(zip(column_names, row))
            return {}
        except Exception as e:
            print(e)
            return {}

    def __get_all_books_by_field(self, field: str, value) -> List[Dict]:
        sql = f"SELECT * FROM books WHERE {field} = ?"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            self.conn.close()
            return [dict(zip(column_names, row)) for row in rows]
        except Exception as e:
            print(e)
            return []


class RentBooks:
    def __init__(self, db: str) -> None:
        """
        Constructor for managing the rent_books table.

        :param db: Path to the SQLite database file.
        """
        self.__db = db

    def setup(self) -> None:
        """
        Creates the rent_books table if it doesn't exist.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rent_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                due_date DATE DEFAULT (DATE('now', '+7 days')),
                is_return BOOLEAN DEFAULT 0,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()
        self.conn.close()

    def add_rent(self, book_id: int, user_id: int, due_date: str = None) -> bool:
        """
        Adds a new rent record.

        :param book_id: ID of the rented book
        :param user_id: ID of the user renting the book
        :param due_date: Optional due date in 'YYYY-MM-DD' format
        :return: Boolean status of the operation
        """
        if not due_date:
            due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        is_return = False
        sql = """
        INSERT INTO rent_books (book_id, user_id, due_date, is_return)
        VALUES (?, ?, ?, ?)
        """
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (book_id, user_id, due_date, is_return))
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False

    def get_all_rents(self) -> list:
        """
        Retrieves all rent records as a list of dictionaries.

        :return: List of all rent records
        """
        sql = """
        SELECT * FROM rent_books
        """
        try:
            self.conn = sqlite3.connect(self.__db)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            self.conn.close()
            return result
        except Exception as e:
            print(e)
            return []

    def get_rents_by_user(self, user_id: int) -> list:
        """
        Retrieves rent records for a specific user.

        :param user_id: ID of the user
        :return: List of rent records
        """
        sql = """
        SELECT * FROM rent_books WHERE user_id = ?
        """
        try:
            self.conn = sqlite3.connect(self.__db)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            self.conn.close()
            return result
        except Exception as e:
            print(e)
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
        self.reservation = TableReservation(self.db_file)
        self.requested_books = RequestedBooks(self.db_file)
        self.donated_books = DonateBooks(self.db_file)
        self.books = Books(self.db_file)
        self.rent = RentBooks(self.db_file)


    def create_tables(self):
        self.users.setup()
        self.subscribed_users.setup()
        self.reservation.setup()
        self.requested_books.setup()
        self.donated_books.setup()
        self.books.setup()
        self.rent.setup()
        print("Database and tables created successfully!")


if __name__ == "__main__":
    db_helper = DBHelper()
    db_helper.create_tables()