"""
Common functions to read/write/append CSV files without feature specific knowledge.
The layer that have access to any kind of long term data storage. In this case, we use CSV files, but later on we'll change this to SQL database.
"""
import psycopg2
import csv
import os
from pathlib import Path

from util import List


def get_connection_string():
    user_name = os.environ.get('PSQL_USER_NAME')
    password = os.environ.get('PSQL_PASSWORD')
    host = os.environ.get('PSQL_HOST')
    database_name = os.environ.get('PSQL_DB_NAME')


    env_variables_defined = user_name and password and host and database_name

    if env_variables_defined:
        return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
            user_name=user_name,
            password=password,
            host=host,
            database_name=database_name
        )
    else:
        raise KeyError('Some necessary environment variable(s) are not defined')


def open_database():
    try:
        connection_string = get_connection_string()
        connection = psycopg2.connect(connection_string)
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print('Database connection problem')
        raise exception
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value

    return wrapper
















#--------------------------------------------------------------------------------------- AskMate v.1

data_folder = Path("data/")

QUESTION_FIELDS = ['question_id', 'pic', 'title', 'time', 'views', 'votes', 'message']
ANSWER_FIELDS = ['question_id', 'answer_id', 'pic', 'time', 'votes', 'message']

answers_file = data_folder / 'answer.csv'
question_file = data_folder / 'question.csv'


def get_all_data(file_name: Path) -> List[dict]:
    with open(file_name, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        table = [row for row in csv_reader]
        # convert all numeric strings values to int
        [data.update({key: int(value)}) for data in table for key, value in data.items() if value.lstrip('-').isnumeric()]
    return table


def load_data(data_type: str) -> list:
    if data_type == 'questions':
        return get_all_data(question_file)
    elif data_type == 'answers':
        return get_all_data(answers_file)


def save_data(data_type: str, list_of_data: list) -> None:
    if data_type == 'questions':
        write_all_data(file_name=question_file, list_of_data=list_of_data, field_names=QUESTION_FIELDS)
    elif data_type == 'answers':
        write_all_data(file_name=answers_file, list_of_data=list_of_data, field_names=ANSWER_FIELDS)


def write_all_data(file_name: Path, list_of_data: list, field_names: list) -> None:
    with open(file_name, "w") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        csv_writer.writeheader()
        for row in list_of_data:
            csv_writer.writerow(row)


def change_numbers(data_type: str, question_id: int, key_type: str, number: int, answer_id: int = None) -> None:
    data = load_data(data_type)
    if data_type == 'questions':
        for question in data:
            if question['question_id'] == question_id:
                question[key_type] += number
    elif data_type == 'answers':
        for answer in data:
            if answer['answer_id'] == answer_id and answer['question_id'] == question_id:
                answer[key_type] += number
    save_data(data_type=data_type, list_of_data=data)


def get_latest_id(id_type: str, data_type: str) -> int:
    return max([int(item[id_type]) for item in load_data(data_type)])


def write_new_data_to_file(data_type: str, new_data_from_user) -> None:
    if data_type == 'questions':
        with open(question_file, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=QUESTION_FIELDS)
            new_question = dict()
            for item in range(len(new_data_from_user)):
                new_question[QUESTION_FIELDS[item]] = new_data_from_user[item]
            csv_writer.writerow(new_question)
    elif data_type == 'answers':
        with open(answers_file, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=ANSWER_FIELDS)
            new_answer = dict()
            for item in range(len(new_data_from_user)):
                new_answer[ANSWER_FIELDS[item]] = new_data_from_user[item]
            csv_writer.writerow(new_answer)


def find_row_index_id(table, id_find):
    for index in range(len(table)):
        if int(table[index]["id"]) == id_find:
            return index
