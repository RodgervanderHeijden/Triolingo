import sqlite3
from datetime import datetime
import pandas as pd

CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS users (user_name TEXT, language_proficiency FLOAT, lr_easy FLOAT, " \
                    "lr_moderate FLOAT, lr_difficult FLOAT, last_quiz DATETIME)"
dtype_dict = {'userID': 'INTEGER',
              'user_name': 'TEXT',
              'language_proficiency': 'FLOAT',
              'lr_easy': 'FLOAT',
              'lr_moderate': 'FLOAT',
              'lr_difficult': 'FLOAT',
              'last_quiz': 'DATETIME'
              }
UPDATE_USER_STATS = "UPDATE users SET language_proficiency = ?, lr_easy = ?, lr_moderate = ?," \
                    "lr_difficult = ?, last_quiz = ? WHERE user_name = ?;"
INSERT_USER = "INSERT INTO users (user_name, language_proficiency, lr_easy, lr_moderate, " \
              "lr_difficult, last_quiz) VALUES (?, ?, ?, ?, ?, ?);"


# With me as only user
def connect_users():
    return sqlite3.connect("./databases/triolingo.db")


def initialize_table():
    """Initialize the table. Should never run again."""
    conn = connect_users()
    with conn:
        conn.execute(CREATE_USERS_TABLE)


def initialize_new_user(user_name, conn):
    language_proficiency = 1
    lr_easy = 1
    lr_moderate = 1
    lr_difficult = 1
    last_quiz = datetime.now()

    with conn:
        conn.execute(INSERT_USER, (user_name, language_proficiency, lr_easy, lr_moderate, lr_difficult, last_quiz,))


def return_user_data(username):
    conn = connect_users()
    known_users = pd.read_sql('SELECT DISTINCT user_name FROM users', con=conn)
    if username not in known_users.values:
        initialize_new_user(username, conn)
    return pd.read_sql('SELECT * FROM users where user_name = ?', params=[username], con=conn)


def update_user_info(user, error, quiz_difficulty):
    """Update the user info ie the proficiency and learning rate multiplicators.

    Some voodoo is present here as well. As to prevent easy quizzes to eventually become
    more difficult than say moderate ones because users play only easy quizzes,
    all learning rates are penalized after every quiz (even of other difficulties).
    A 10% penalty of each learning rate above the default (1.0) is taken, but a 10% bonus
    is added to the overall language proficiency."""
    updated_language_proficiency = user.language_proficiency * (1 + error * 0.2)
    lr_easy = user.lr_easy
    lr_moderate = user.lr_moderate
    lr_difficult = user.lr_difficult
    if quiz_difficulty == "easy":
        lr_easy = user.lr_easy * (1 + 0.2 * error)
    elif quiz_difficulty == "moderate":
        lr_moderate = lr_moderate * (1 + 0.2 * error)
    elif quiz_difficulty == "difficult":
        lr_difficult = lr_difficult * (1 + 0.2 * error)

    # additional voodoo to compensate for monotone difficulty selection
    updated_language_proficiency += (updated_language_proficiency - 1) * 1.05
    lr_easy -= (lr_easy - 1) * 0.1
    lr_moderate -= (lr_moderate - 1) * 0.1
    lr_difficult -= (lr_difficult - 1) * 0.1

    conn = connect_users()
    with conn:
        conn.execute(UPDATE_USER_STATS,
                     (updated_language_proficiency, lr_easy, lr_moderate, lr_difficult, datetime.now(), user.name))
    print(pd.read_sql('SELECT language_proficiency, lr_easy, lr_moderate, lr_difficult '
                      'FROM users WHERE user_name = ?', params=[user.name], con=connect_users()))
    return pd.read_sql('SELECT language_proficiency, lr_easy, lr_moderate, lr_difficult '
                       'FROM users WHERE user_name = ?', params=[user.name], con=connect_users())
