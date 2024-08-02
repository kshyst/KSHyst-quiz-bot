import mysql.connector

database = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="user",
    password="user_password",
    database="kshyst_quiz_bot"
)

cursor = database.cursor(dictionary=True)


def start_and_create():
    cursor.execute("CREATE DATABASE IF NOT EXISTS kshyst_quiz_bot")
    cursor.execute("USE kshyst_quiz_bot")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, score INT , user_name TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS questions_movies (id INT AUTO_INCREMENT PRIMARY KEY, question TEXT, correct_answer TEXT, answers TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS questions_celebrities (id INT AUTO_INCREMENT PRIMARY KEY, question TEXT, correct_answer TEXT, answers TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS questions_vehicles (id INT AUTO_INCREMENT PRIMARY KEY, question TEXT, correct_answer TEXT, answers TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS questions_anime (id INT AUTO_INCREMENT PRIMARY KEY, question TEXT, correct_answer TEXT, answers TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS questions_math (id INT AUTO_INCREMENT PRIMARY KEY, question TEXT, correct_answer TEXT, answers TEXT)")
    database.commit()


def insert_user(user_id: int = None, name: str = None):
    if get_user_score(user_id) is not None:
        return

    cursor.execute(f"INSERT INTO users (user_id, score , user_name) VALUES ({user_id}, 0 , '{name}')")
    database.commit()


def get_user_score(user_id: int):
    cursor.execute("SELECT score FROM users WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()
    cursor.fetchall()
    if result is None:
        return None
    return result['score']


def update_user_score(user_id: int, score: int):
    current_score = get_user_score(user_id)
    if current_score is not None:
        new_score = current_score + score
        cursor.execute("UPDATE users SET score=%s WHERE user_id=%s", (new_score, user_id))
        database.commit()


def get_top_10_users() -> list:
    cursor.execute("SELECT * FROM users ORDER BY score DESC LIMIT 10")
    return cursor.fetchall()


def insert_question(category: str, question: str, correct_answer: str, answers: str):
    category = category.lower()
    cursor.execute(
        f"INSERT INTO questions_{category} (question, correct_answer, answers) VALUES ('{question}', '{correct_answer}', '{answers}')")
    database.commit()


print(database)

start_and_create()


def get_all_math_questions() -> list:
    cursor.execute("SELECT * FROM questions_math")
    return cursor.fetchall()


def get_all_celebrities_questions():
    return None


def get_all_movies_questions():
    return None


def get_all_vehicles_questions():
    return None


def get_all_anime_questions():
    return None
