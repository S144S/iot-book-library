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
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        fname TEXT NOT NULL,
        lname TEXT NOT NULL,
        grade INTEGER NOT NULL DEFAULT 7,
        register_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0
        )"""
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def add_user(
            self,
            username: str,
            password: str,
            fname: str,
            lname: str,
            grade: int = 7,
            register_date=None,
            last_login=None,
            is_active: bool = True,
            is_admin: bool = False
    ) -> bool:
        """
        Inserts a new user into the database.

        :param username: The username of the user
        :type username: str
        :param password: User's password
        :type password: str
        :param fname: The first name of the user
        :type fname: str
        :param lname: The last name of the user
        :type lname: str
        :param grade: The grade of the user. defaults to 7
        :type grade: int (optional)
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
        username, password, fname, lname, grade, register_date,
        last_login, is_active, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        param = (
            username,
            password,
            fname,
            lname,
            grade,
            register_date,
            last_login,
            is_active,
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
            username: str,
            fname: str,
            lname: str,
            grade: int,
    ) -> bool:
        """
        Update user parameters in the database based on user ID.

        :param id: The ID of the user to update
        :type id: int
        :param username: New username for the user
        :type username: str
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
        username = ?, fname = ?,lname = ?, grade = ?
        WHERE id = ?
        """
        params = (username, fname, lname, grade, id)
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

    def update_user_tries(self, tries, id) -> bool:
        """
        Update a user tries.

        :param id: The ID of the user to update
        :type id: int
        :param tries: The number of tries
        :type tries: int
        :return: a boolean that indicate success.
        """
        sql = "UPDATE users SET tries = ? WHERE id = ?"
        params = (tries, id)
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

    def update_user_trees(self, trees: int, id: int):
        """
        Update a user trees in the database based on user ID.

        :param trees: The number of trees
        :type trees: int
        :param id: The ID of the user to update
        :type id: int
        :return: a boolean that includes
        the status of updating the user's trees.
        """
        sql = "UPDATE users SET trees = ? WHERE id = ?"
        params = (trees, id)
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

    def get_user_id(self, username: str) -> int:
        """
        Get a user's id from db.

        :param username: The username of the user
        :type username: str
        :return: an integer that includes user's id.
        """
        sql = "SELECT id FROM users WHERE username = ?"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, (username,))
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


class Topics:
    def __init__(self, db: str) -> None:
        """
        The constructor of Topics table class.

        :param db: Represents the name(or path) of the SQLite database
        :type db_file: str
        """
        self.__db = db
        self.setup()

    def setup(self) -> None:
        """
        Creates the topics table in database.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        # Create users table
        sql = """CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY,
        name TEXT,
        grade INTEGER
        )"""
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def get_all_topics(self) -> list:
        """
        Get all topics from database.

        :return: list of topics
        """
        sql = "SELECT * FROM topics"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.conn.close()
            if not rows:
                return []
            topics_list = []
            for row in rows:
                topic_dict = {'id': row[0], 'name': row[1], 'grade': row[2]}
                topics_list.append(topic_dict)
            return topics_list
        except Exception as e:
            print(e)
            return []

    def get_topics_by_grade(self, max_grade: int) -> list[dict]:
        """
        Reads topics from the db where grade is less or equal to max_grade.

        :param max_grade: Represents the maximum grade of the topics
        :type max_grade: int
        :return: list of topics
        :rtype: list
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM topics WHERE grade <= ?", (max_grade,))
        topics = []
        for row in cursor.fetchall():
            topic_dict = {
                "id": row[0],
                "name": row[1],
                "grade": row[2]
            }
            topics.append(topic_dict)
        self.conn.close()
        return topics

    def add_topic(self, name: str, grade: int):
        """
        Inserts a new topic into the db.

        :param name: Represents the name of the topic
        :type name: str
        :param grade: Rrepresents the level or grade of the topic
        :type grade: int
        :return: The `add_topic` method returns a boolean value,
        `True` if the topic was added successfully,
        and `False` if there was an exception during the process.
        """
        sql = """INSERT OR IGNORE INTO topics
        (name, grade)
        VALUES (?, ?)
        """
        param = (name, grade)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, param)
            self.conn.commit()
            self.conn.close()
            print("Topic added successfully")
            return True
        except Exception as e:
            print(e)
            return False


class Questions:
    def __init__(self, db: str) -> None:
        """
        The constructor of Questions table class.

        :param db: Represents the name(or path) of the SQLite database
        :type db_file: str
        """
        self.__db = db
        self.setup()

    def setup(self) -> None:
        """
        Creates the questions table in database.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        # Create users table
        sql = """CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        option1 TEXT NOT NULL,
        option2 TEXT NOT NULL,
        option3 TEXT NOT NULL,
        option4 TEXT NOT NULL,
        option5 TEXT DEFAULT "نخوانده ایم",
        answer INTEGER NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
        )"""
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def add_question(
            self,
            topic_id: int,
            question: str,
            opt1: str,
            opt2: str,
            opt3: str,
            opt4: str,
            answer: int
    ):
        """
        Inserts a new question into the db.

        :param topic_id: Represents the id of the topic
        :type name: int
        :param question: Rrepresents the question
        :type question: str
        :param opt1: Rrepresents the option 1
        :type opt1: str
        :param opt2: Rrepresents the option 2
        :type opt2: str
        :param opt3: Rrepresents the option 3
        :type opt3: str
        :param opt4: Rrepresents the option 4
        :type opt4: str
        :param answer: Represents the right answer of question
        :type name: int
        :return: The `add_topic` method returns a boolean value,
        `True` if the topic was added successfully,
        and `False` if there was an exception during the process.
        """
        sql = """INSERT OR IGNORE INTO questions
        (topic_id, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        param = (topic_id, question,  opt1, opt2, opt3, opt4, answer)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, param)
            self.conn.commit()
            self.conn.close()
            print("Question added successfully")
            return True
        except Exception as e:
            print(e)
            return False

    def get_all_questions(self) -> list[dict]:
        """
        Reads all questions from the questions table in the database
        and returns them as a list of dictionaries.

        :return: A list of dictionaries
        :rtype: list[dict]
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM questions")
        questions = []
        for row in cursor.fetchall():
            question_dict = {
                "id": row[0],
                "topic_id": row[1],
                "question": json.loads(row[2]),
                "option1": json.loads(row[3]),
                "option2": json.loads(row[4]),
                "option3": json.loads(row[5]),
                "option4": json.loads(row[6]),
                "option5": row[7],
                "answer": row[8]
            }
            questions.append(question_dict)
        self.conn.close()
        return questions


class TextBooks:
    def __init__(self, db: str) -> None:
        """
        The constructor of TextBooks table class.

        :param db: Represents the name(or path) of the SQLite database
        :type db_file: str
        """
        self.__db = db
        self.setup()

    def setup(self) -> None:
        """
        Creates the textbooks table in database.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        # Create users table
        sql = """CREATE TABLE IF NOT EXISTS textbooks (
        id INTEGER PRIMARY KEY,
        topic INTEGER NOT NULL,
        name TEXT,
        pdf TEXT,
        video TEXT,
        FOREIGN KEY(topic) REFERENCES topics(id)
        )"""
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def get_all_textbooks(self) -> list:
        """
        Get all textbooks from database.

        :return: list of textbooks
        """
        sql = "SELECT * FROM textbooks"
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.conn.close()
            if not rows:
                return []
            topics_list = []
            for row in rows:
                topic_dict = {
                    'id': row[0],
                    'topic': row[1],
                    'name': row[2],
                    'pdf': row[3],
                    'video': row[4]
                }
                topics_list.append(topic_dict)
            return topics_list
        except Exception as e:
            print(e)
            return []

    def add_textbook(self, tid: int, name: str, pdf: str, video: str) -> bool:
        """
        Inserts a new textbook into the db.

        :param name: Represents the name of the topic
        :type name: str
        :param tid: Represents the id of the topic
        :type tid: int
        :param pdf: Represents the pdf of the textbook
        :type pdf: str
        :param video: Represents the video of the textbook
        :type video: str
        :return: The `add_textbook` method returns a boolean value,
        `True` if the textbook was added successfully,
        and `False` if there was an exception during the process.
        """
        pdf_path = "./static/dars/" + pdf + ".pdf"
        sql = """INSERT OR IGNORE INTO textbooks
        (topic, name, pdf, video)
        VALUES (?, ?, ?, ?)
        """
        param = (tid, name, pdf_path, video)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, param)
            self.conn.commit()
            self.conn.close()
            print("Textbook added successfully")
            return True
        except Exception as e:
            print(e)
            return False

    def get_textbooks_by_topics(self, topic_ids: list) -> list:
        """
        Retrieve textbooks based on a list of topic IDs.

        :param topic_ids: List of topic IDs
        :type topic_ids: list
        :return: List of textbooks matching the provided topic IDs
        :rtype: list
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        
        textbooks_by_topics = {}  # Initialize an empty dictionary to store textbooks by topics
        
        for topic_id in topic_ids:
            sql = "SELECT * FROM textbooks WHERE topic = ?"
            cursor.execute(sql, (topic_id,))
            textbooks = cursor.fetchall()
            textbooks_by_topics[topic_id] = textbooks
        
        self.conn.close()
        return textbooks_by_topics


class Results:
    def __init__(self, db: str) -> None:
        """
        The constructor of Result table class.
        """
        self.__db = db
        self.setup()

    def setup(self) -> None:
        """
        Creates the result table in database.
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        # Create users table
        sql = """CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        topic INTEGER NOT NULL,
        result INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
        FOREIGN KEY (topic) REFERENCES topics(id)
        )"""
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()
    
    def add_result(self, user_id, topic, result) -> bool:
        """
        Inserts a new result into the db.

        :param user_id: Represents the id of the user
        :type user_id: int
        :param topic: Represents the id of the topic
        :type topic: int
        :param result: Represents the result of the topic
        :type result: int
        :return: The `add_result` method returns a boolean value,
        `True` if the result was added successfully,
        and `False` if there was an exception during the process.
        """
        sql = """INSERT OR IGNORE INTO results
        (user_id, topic, result)
        VALUES (?, ?, ?)
        """
        param = (user_id, topic, result)
        try:
            self.conn = sqlite3.connect(self.__db)
            cursor = self.conn.cursor()
            cursor.execute(sql, param)
            self.conn.commit()
            self.conn.close()
            print("Result added successfully")
            return True
        except Exception as e:
            print(e)
            return False

    def get_results_by_user_id(self, user_id: int) -> list[dict]:
        """
        Reads results from the results table for a specific user_id.

        :param user_id: Represents the id of the user
        :type user_id: int
        :return: A list of results dictionaries
        :rtype: list[dict]
        """
        self.conn = sqlite3.connect(self.__db)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM results WHERE user_id = ?", (user_id,))
        results = []
        for row in cursor.fetchall():
            result_dict = {
                "id": row[0],
                "topic": row[2],
                "result": row[3]
            }
            results.append(result_dict)
        self.conn.close()
        return results


class DBHelper:
    def __init__(self, db_file: str = "database.db") -> None:
        """
        The constructor of DataBase helper class.

        :param db_file: The `db_file` represents the name(or path)
        of the SQLite database
        :type db_file: str (optional)
        """
        self.db_file = db_file
        # self.conn = sqlite3.connect(self.db_file)
        self.users = Users(self.db_file)
        # self.topics = Topics(self.db_file)
        # self.questions = Questions(self.db_file)
        # self.textbooks = TextBooks(self.db_file)
        # self.results = Results(self.db_file)

    def create_tables(self):
        self.users.setup()
        print("Database and tables created successfully!")


if __name__ == "__main__":
    db_helper = DBHelper()
    db_helper.create_tables()