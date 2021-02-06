""" Layer between the server and the data. Functions here should be called from the server.py and these should use generic functions from the connection.py """
from util import List, get_actual_time
from datetime import datetime

from psycopg2.extras import RealDictCursor


import connection

DEFAULT_ORDER_BY = 'submission_time'
DEFAULT_ORDER_DIR = 'ASC'


@connection.connection_handler
def remove_question(cursor: RealDictCursor, question_id: int) -> None:
    answers_id = get_answers_id_by_question(question_id=question_id)
    for id in answers_id:
        remove_answer(question_id=question_id, answer_id=id['id'])
    command = """
    delete from comment 
    where question_id = %(question_id)s;
    
    delete from question_tag 
    where question_id = %(question_id)s;
    
    delete from answer 
    where question_id = %(question_id)s;
    
    delete from question
    where id = %(question_id)s;
    """
    param = {'question_id': question_id}
    cursor.execute(command, param)


@connection.connection_handler
def get_questions_data(cursor: RealDictCursor, asc_desc: str, sort_column_by: str) -> dict:
    query = """ 
    select
    question.id,
    title as "title",
    question.submission_time as "time",
    view_number as "views",
    question.vote_number as "votes",
    question.message, tag.name as tag,
    count(answer.message) as answers_count,
    count(comment.message) as comments_count,
    question.user_name
    from question
    left join comment
    on question.id = comment.question_id
    INNER JOIN question_tag
    on question_tag.question_id = question.id
    inner join tag
    on tag.id = question_tag.tag_id
    left join answer
    on answer.question_id = question.id
    group by question.id, tag.name
    order by question.{0} {1};
    """.format(sort_column_by, asc_desc)
    parameter = {'asc_desc': asc_desc, 'sort_column_by': sort_column_by}
    cursor.execute(query, parameter)
    return cursor.fetchall()


@connection.connection_handler
def get_questions_data_by_tag(cursor: RealDictCursor, asc_desc: str, sort_column_by: str, tag_id: int) -> dict:
    query = """ 
    select
    question.id,
    title as "title",
    question.submission_time as "time",
    view_number as "views",
    question.vote_number as "votes",
    question.message, tag.name as tag,
    count(answer.message) as answers_count,
    count(comment.message) as comments_count,
    question.user_name
    from question
    left join comment
    on question.id = comment.question_id
    INNER JOIN question_tag
    on question_tag.question_id = question.id and question_tag.tag_id = {2}
    inner join tag
    on tag.id = question_tag.tag_id
    left join answer
    on answer.question_id = question.id
    group by question.id, tag.name
    order by question.{0} {1};
    """.format(sort_column_by, asc_desc, tag_id)
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_user_data(cursor: RealDictCursor, user_name):
    query = """
    SELECT
    users.email,
    users.user_name as user_name,
    register_date as "date",
    reputation as "rep",
    users.picture as "picture",
    count(answer.message) as answers_count,
    count(question.message) as question_count,
    count(comment.message) as comment_count
    from users
    left join answer
    on answer.user_name = users.user_name
    left join question
    on question.user_name = users.user_name
    left join comment
    on comment.user_name = users.user_name
    where users.user_name = %(user_name)s
    group by users.email, users.user_name, register_date, reputation, users.picture;
    """
    param = {"user_name": user_name}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def find_comment_by_question_id(cursor: RealDictCursor, question_id: str) -> list:
    query = """
    SELECT * FROM comment WHERE question_id= %(question_id)s ORDER BY submission_time asc; """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def find_comment_by_answer_id(cursor: RealDictCursor, answer_id: str) -> list:
    query = """
    SELECT * FROM comment WHERE answer_id= %(answer_id)s ORDER BY submission_time asc; """
    param = {'answer_id': answer_id}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def find_question_by_id(cursor: RealDictCursor, question_id: str) -> list:
    query = """
    select  question.id, question.submission_time, question.view_number, question.vote_number,
     question.title, question.message, question.image, question.user_name, tag.name as tag
    from question, question_tag, tag
    where question.id = %(question_id)s and question_tag.question_id = question.id and question_tag.tag_id = tag.id;"""
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def find_answer_by_id(cursor, answer_id):
    query = """
    select  * from answer where id = %(id)s;"""
    param = {'id': answer_id}
    cursor.execute(query, param)
    answer_data = cursor.fetchall()
    return answer_data


@connection.connection_handler
def find_all_answers_by_question_id(cursor: RealDictCursor, question_id: str) -> list:
    query = """
    select  * from answer where question_id = %(question_id)s;"""
    param = {'question_id': question_id}
    cursor.execute(query, param)
    data = cursor.fetchall()
    return data


@connection.connection_handler
def modify_question_views(cursor: RealDictCursor, question_id: str) -> None:
    command = """
    update question 
    set view_number = (view_number+1)
    where id = %(question_id)s
    """
    param = {'question_id': question_id}
    cursor.execute(command, param)


@connection.connection_handler
def remove_answer(cursor: RealDictCursor, question_id: int, answer_id: int) -> None:
    command = """
    delete from comment 
    where answer_id = %(answer_id)s;
    
    delete from answer 
    where id = %(answer_id)s and question_id = %(question_id)s;
    """
    param = {'answer_id': answer_id, 'question_id': question_id}
    cursor.execute(command, param)


@connection.connection_handler
def remove_comment(cursor: RealDictCursor, comment_id: int) -> None:
    command = """
    delete from answer 
    where id = %(comment_id)s;
    """
    param = {'comment_id': comment_id}
    cursor.execute(command, param)


@connection.connection_handler
def remove_tag(cursor: RealDictCursor, tag_id: int, question_id: int) -> None:
    command = """
    delete from question_tag
    where question_id = %(question_id)s 
    and tag_id = %(tag_id)s;
    """
    param = {'tag_id': tag_id, 'question_id': question_id}
    cursor.execute(command, param)


@connection.connection_handler
def modify_question_votes(cursor: RealDictCursor, value: int, question_id: str) -> None:
    command = """
    update question
    set vote_number = (vote_number + %(value)s)
    where id = %(question_id)s;
    """
    param = {'question_id': question_id, 'value': value}
    cursor.execute(command, param)


@connection.connection_handler
def modify_answer_votes(cursor: RealDictCursor, question_id: str, answer_id: str, value: int) -> None:
    command = """
    update answer
    set vote_number = (vote_number+%(value)s)
    where id = %(answer_id)s and question_id = %(question_id)s
    """
    param = {'question_id': question_id, 'answer_id': answer_id, 'value': value}
    cursor.execute(command, param)


@connection.connection_handler
def find_all_answers_by_question_id(cursor: RealDictCursor, question_id: str):
    query = """
    select *
    from answer
    where question_id = %(question_id)s
    order by submission_time desc;
    """

    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


def modify_views_votes(data_to_modify: dict, question: list, answers_list: list, reputation_target: str, reputation_giver: str) -> None:
    for key in data_to_modify.keys():
        if key == 'questions_votes':
            if is_user_name_available(user_name=reputation_target):
                uppdate_user_reputation(user_name=reputation_target, value=data_to_modify.get(key))
            #Funkcja która dodaje odpowied vote: question_id, ansver_id, user_name, status(positive and negative)
            add_vote_reg(question_id=question[0]['id'], answer_id=None, user_name=reputation_giver,
                         status='Positive' if int(data_to_modify.get(key)) > 0 else 'Negative')
            modify_question_votes(question_id=question[0]['id'], value=data_to_modify.get(key))
        elif key == 'questions_views':
            modify_question_views(question_id=question[0]['id'])
        elif key == 'answers_votes':
            answer = []
            for row in answers_list:
                if (str(row['question_id']) == str(question[0]['id'])) and (str(row['id']) == str(data_to_modify['answer_id'])):
                    answer.append(row)
            if is_user_name_available(user_name=reputation_target):
                uppdate_user_reputation(user_name=reputation_target, value=data_to_modify.get(key))
            # Funkcja która dodaje odpowied vote: question_id, ansver_id, user_name, status(positive and negative)
            add_vote_reg(question_id=question[0]['id'], answer_id=answer[0]['id'], user_name=reputation_giver,
                         status='Positive' if int(data_to_modify.get(key)) > 0 else 'Negative')
            modify_answer_votes(question_id=question[0]['id'], answer_id=answer[0]['id'], value=data_to_modify.get(key))


def switch_asc_desc(order_direction):
    return 'DESC' if order_direction == 'ASC' else 'ASC'


def get_time():
    time = datetime.now().replace(microsecond=0)
    return time


@connection.connection_handler
def get_new_ques_id(cursor):
    try:
        cursor.execute("""SELECT MAX(id) from question;""")
        new_id = cursor.fetchall()[0]["max"] + 1
    except KeyError:
        new_id = 0
    return new_id


@connection.connection_handler
def get_answer_id(cursor):
    try:
        cursor.execute("""SELECT MAX(id) from answer;""")
        new_id = cursor.fetchall()[0]['max'] + 1
    except KeyError:
        new_id = 0
    return new_id


@connection.connection_handler
def get_user_id(cursor):
    try:
        cursor.execute("""SELECT MAX(user_id) from users;""")
        new_id = cursor.fetchall()[0]['max'] + 1
    except KeyError:
        new_id = 0
    return new_id


@connection.connection_handler
def get_comment_id(cursor):
    try:
        cursor.execute("""SELECT MAX(id) from comment;""")
        new_id = cursor.fetchall()[0]['max'] + 1
    except Exception:
        new_id = 0
    return new_id


def add_question():
    new_question = {
        "id": get_new_ques_id(),
        "submission_time": get_time(),
        "view_number": 0,
        "vote_number": 0
    }
    return new_question


@connection.connection_handler
def save_question(cursor: RealDictCursor, data):
    command = """INSERT INTO question VALUES (%(new_id_value)s, %(new_submission_time_value)s, %(new_view_number_value)s, 
                    %(new_vote_number_value)s, %(new_title_value)s, %(new_message_value)s, %(new_image_value)s, %(user_name)s);
                    INSERT INTO question_tag VALUES (%(new_id_value)s, %(tag_id)s);"""
    param = {"new_id_value": data['id'],
                    "new_submission_time_value": data['submission_time'],
                    "new_view_number_value": data['view_number'],
                    "new_vote_number_value": data['vote_number'],
                    "new_title_value": data['title'],
                    "new_message_value": data['message'],
                    "new_image_value": data['image'],
                    "tag_id": data['tag_id'],
                    "user_name": data['user_name']}
    cursor.execute(command, param)


@connection.connection_handler
def edit_question(cursor, question_id, edited_data):
    cursor.execute("""UPDATE question
                      SET submission_time = %(submission_time_value)s, title = %(title_value)s, 
                      message = %(message_value)s, image = %(image_value)s
                      WHERE id=%(id)s;""",
                   {"submission_time_value": get_time(),
                    "title_value": edited_data['title'],
                    "message_value": edited_data['message'],
                    "image_value": edited_data['image'],
                    "id": question_id})


@connection.connection_handler
def save_answer(cursor: RealDictCursor, data):
    cursor.execute("""INSERT INTO answer VALUES (%(new_id_value)s, %(new_submission_time_value)s, %(new_vote_number_value)s, 
                    %(new_question_id_value)s, %(new_message_value)s, %(new_image_value)s, %(user_name)s);""",
                   {"new_id_value": data['id'],
                    "new_submission_time_value": data['submission_time'],
                    "new_vote_number_value": data['vote_number'],
                    "new_question_id_value": data['question_id'],
                    "new_message_value": data['message'],
                    "new_image_value": data['image'],
                    "user_name": data['user_name']})


def add_answer(new_answer, question_id, user_name):
    new_answer_data = {
        "id": get_answer_id(),
        "submission_time": get_time(),
        "vote_number": "0",
        "question_id": question_id,
        "message": new_answer,
        "image": "",
        "user_name": user_name
    }
    save_answer(new_answer_data)


@connection.connection_handler
def edit_answer(cursor, answer_id, edited_data):
    cursor.execute("""UPDATE answer
                      SET submission_time = %(submission_time_value)s, message = %(message_value)s,
                      image = %(image_value)s
                      WHERE id=%(id)s;""",
                   {"submission_time_value": get_time(),
                    "message_value": edited_data['message'],
                    "image_value": edited_data['image'],
                    "id": answer_id})


@connection.connection_handler
def add_comment(cursor, data):
    cursor.execute("""INSERT INTO comment VALUES (%(id_value)s, %(question_id_value)s, %(answer_id_value)s, 
                    %(message_value)s, %(submission_time_value)s, %(edited_count_value)s, %(user_name)s);""",
                   {"id_value": get_comment_id(),
                    "question_id_value": data['question_id'],
                    "answer_id_value": data['answer_id'],
                    "message_value": data['message'],
                    "submission_time_value": get_time(),
                    "edited_count_value": None,
                    "user_name": data['user_name']})


@connection.connection_handler
def edit_comment(cursor, comment_id, new_data):
    cursor.execute("""UPDATE comment
                      SET submission_time = %(submission_time_value)s, message = %(message_value)s,
                      edited_count = %(new_count_value)s
                      WHERE id=%(id)s;""",
                   {"message_value": new_data['message'],
                    "submission_time_value": get_time(),
                    "new_count_value": new_data['edited_count'],
                    "id": comment_id})


@connection.connection_handler
def get_answers_id_by_question(cursor: RealDictCursor, question_id: int):
    query = """
    SELECT id FROM answer
    WHERE question_id = %(question_id)s;
    """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


def fetch_tags():
    return


@connection.connection_handler
def fetch_tags(cursor: RealDictCursor) -> list:
    query = """SELECT id AS tag_id, name AS tag_name FROM tag"""
    cursor.execute(query)
    tags = cursor.fetchall()
    return list(tags)


@connection.connection_handler
def count_tags(cursor: RealDictCursor) -> list:
    query = """
    SELECT tag.name as tag_name, count(question_tag.tag_id) as count, tag.id as tag_id
    from tag, question_tag
    where tag_id = tag.id
    group by tag.name, tag.id
    order by tag.name;
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def count_questions(cursor: RealDictCursor) -> int:
    query = """
    SELECT count(question.id) as questions_count
    from question;
    """
    cursor.execute(query)
    return cursor.fetchall()[0]['questions_count']


def pagination(data: list, pagination_range: int = 10) -> list:
    full_list_count = len(data) // pagination_range #data change to len(data) !!!!!
    remainder = len(data) % pagination_range  #data change to len(data)   !!!!!
    count_of_pagination = [pagination_range for index in range(full_list_count)]
    count_of_pagination.append(remainder)
    result = []
    first_index = 0
    for index in range(len(count_of_pagination)):
        result.append([])
        for count in range(count_of_pagination[index]):
            result[index].append(data[first_index])
            data.remove(data[first_index])
    return result


def sort_questions(questions: list, sort_by: str, asc_desc: str):
    return sorted(questions, key=lambda question: question[sort_by], reverse=True if asc_desc == 'asc' else False)


def search_phrase(questions: list, phrase: str) -> list:
    result = []

    for question in questions:
        ready_to_put, question['title'] = search_into_string(question['title'], phrase)
        ready_to_put, question['message'] = search_into_string(question['message'], phrase)
        if ready_to_put:
            result.append(question)

    return result


def search_into_string(line: str,phrase: str):
    mark_start = '<span class="bg-primary text-white">'
    mark_end = '</span>'
    phrase_count = 0
    result = ''
    ready_to_put = False

    for element in line:
        if element.lower() == str(phrase[phrase_count]).lower():
            result += element
            if result.lower() == phrase.lower():
                #line = line.replace(result, mark_start + result + mark_end)
                line = line.replace(result, '<span class="bg-primary text-white">%s</span>' % (result))
                #"<div>" + getLink(text=_('Test'), fn.getUrl()) + "</div>"
                phrase_count = 0
                result = ''
                ready_to_put = True
            else:
                phrase_count += 1
        else:
            phrase_count = 0
            result = ''

    return ready_to_put, line


@connection.connection_handler
def find_all_emails(cursor: RealDictCursor, email: str):
    query = """
    select * from users
    where email = %(email)s
    """
    param = {'email': email}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def check_login(cursor: RealDictCursor, email):
    query = """
    select email from users
    where email = %(email)s
    """
    cursor.execute(query, {"email": email})
    compare = cursor.fetchall()
    if len(compare) == 0:
        return False
    else:
        return True


@connection.connection_handler
def check_password(cursor: RealDictCursor, password, email):
    query = """
    select password from users
    where password = %(password)s and email = %(email)s
    """
    cursor.execute(query, {"password": password, "email": email})
    compare = cursor.fetchall()
    if len(compare) == 0:
        return False
    else:
        return True


@connection.connection_handler
def register_new_user(cursor: RealDictCursor, user_name, email, password, picture):
    cursor.execute("""
                    INSERT INTO users
                    VALUES (%(user_id)s, %(user_name)s, %(email)s, %(password)s, %(register_date)s, 0, %(picture)s);
                    """, {'user_id': get_user_id(), 'user_name': user_name, 'email': email, 'password': password, 'register_date': get_time(), 'picture': picture})


@connection.connection_handler
def get_user_name_by_email(cursor: RealDictCursor, email: str) -> str:
    query = """
    select users.user_name
    from users
    where users.email = %(email)s;
    """
    param = {'email': email}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def find_user_email(cursor, email):
    cursor.execute("""
                    SELECT email FROM users
                    """)
    list_of_all_user_emails = [email['email'] for email in cursor.fetchall()]

    return email in list_of_all_user_emails


@connection.connection_handler
def get_password_database(cursor, email):
    cursor.execute("""
                    SELECT password FROM users
                    WHERE email = %(email)s
                    """, {'email': email})
    hashed_password = cursor.fetchone()
    return hashed_password['password']

@connection.connection_handler
def uppdate_user_reputation(cursor: RealDictCursor, user_name: str, value: int):
    command = """
    UPDATE users
    SET reputation = reputation + %(value)s
    where user_name = %(user_name)s;
    """
    param = {'user_name': user_name, 'value': value}
    cursor.execute(command, param)

@connection.connection_handler
def is_user_name_available(cursor: RealDictCursor, user_name: str):
    query = """SELECT users.user_name 
    FROM users
    WHERE users.user_name = %(user_name)s"""
    param = {'user_name': user_name}
    cursor.execute(query, param)
    user = cursor.fetchall()
    if len(user) == 1:
        return True
    else:
        return False

@connection.connection_handler
def get_users_data(cursor: RealDictCursor) -> list:
    query = """
    SELECT users.user_name, users.reputation, users.picture
    from users
    ORDER BY users.reputation DESC;
    """
    cursor.execute(query)
    return cursor.fetchall()

@connection.connection_handler
def add_vote_reg(cursor: RealDictCursor, question_id: int, answer_id: int, user_name: str, status: str):
    command = """
    INSERT INTO reg_votes
    VALUES ( %(question_id)s, %(answer_id)s, %(user_name)s, %(status)s );
    """
    param = {
        'question_id': question_id,
        'answer_id': answer_id,
        'user_name': user_name,
        'status': status
    }
    cursor.execute(command, param)

@connection.connection_handler
def question_positive_negative_vote(cursor: RealDictCursor, question_id: int):
    querry = """
    SELECT reg_votes.question_id as id, reg_votes.user_name, reg_votes.status
    FROM reg_votes
    WHERE reg_votes.question_id = %(question_id)s AND reg_votes.answer_id IS NULL;
    """
    param = {'question_id': question_id}
    cursor.execute(querry, param)
    pos_neg = split_answers_questions_votes(cursor.fetchall())

    return pos_neg


def split_answers_questions_votes(vote_data: list):
    pos_neg = {}
    if len(vote_data) > 0:
        for element in vote_data:
            if element['id'] not in pos_neg:
                pos_neg[element['id']] = []
            pos_neg[element['id']].append(element['user_name'])

    return pos_neg

@connection.connection_handler
def answers_positive_negative_vote(cursor: RealDictCursor, question_id: int):
    querry = """
        SELECT reg_votes.answer_id as id, reg_votes.user_name, reg_votes.status
        FROM reg_votes
        WHERE reg_votes.question_id = %(question_id)s and reg_votes.answer_id IS NOT NULL ;
        """
    param = {'question_id': question_id}
    cursor.execute(querry, param)
    pos_neg = split_answers_questions_votes(cursor.fetchall())

    return pos_neg

# --------------------------------------------------------------------------------------- AskMate v.1
FIRST_ITEM = 0
SECOND_ITEM = 1


def fetch_all_data(data_type: str, order_by: str = DEFAULT_ORDER_BY, order_direction: str = DEFAULT_ORDER_DIR) -> List[dict]:
    data = connection.load_data(data_type)
    data.sort(key=lambda key: key[order_by], reverse=True if order_direction == 'desc' else False)
    return data


def generate_id(id_type: str, data_type: str) -> int:
    latest_id = connection.get_latest_id(id_type, data_type)
    return latest_id + 1


def generate_id_type(data_type: str) -> int:
    if data_type == 'questions':
        return generate_id('question_id', data_type)

    elif data_type == 'answers':
        return generate_id('answer_id', data_type)


def find_data_by_id(data_type: str, question_id: int = None, answer_id: int = None) -> dict:
    if data_type == 'questions':
        for question in fetch_all_data(data_type):
            if question_id == question['question_id']:
                return question

    if data_type == 'answers':
        for answer in fetch_all_data(data_type):
            if answer['answer_id'] == answer_id and answer['question_id'] == question_id:
                return answer


def modify_numbers(data_to_modify: dict, question_id: int = None, answer_id: int = None) -> None:
    convert_str_to_int = int([*data_to_modify.values()][FIRST_ITEM])
    data_type = next(iter(data_to_modify.keys())).split('_')[FIRST_ITEM]
    key_type = next(iter(data_to_modify.keys())).split('_')[SECOND_ITEM]
    connection.change_numbers(data_type=data_type, question_id=question_id, key_type=key_type, number=convert_str_to_int, answer_id=answer_id)


def fill_in_all_data(data_type: str, new_data: dict, question_id: int = None) -> None:
    time = str(get_actual_time())
    views = 0
    votes = 0
    if data_type == 'questions':
        id = generate_id('question_id', data_type)
        pic = new_data['pic']
        title = new_data['title']
        message = new_data['message']
        question_list = [id, pic, title, time, views, votes, message]
        connection.write_new_data_to_file(data_type, question_list)
    elif data_type == 'answers':
        answer_id = generate_id('answer_id', data_type)
        pic = ''
        message = new_data['message']
        answer_list = [question_id, answer_id, pic, time, votes, message]
        connection.write_new_data_to_file(data_type, answer_list)


def remove_data(data_type: str, data_to_delete: dict) -> None:
    data = connection.load_data(data_type)

    if data_to_delete in data:
        data.remove(data_to_delete)

    if data_type == "questions":
        connection.write_all_data(connection.question_file, data, connection.QUESTION_FIELDS)

    elif data_type == "answers":
        connection.write_all_data(connection.answers_file, data, connection.ANSWER_FIELDS)


def edit_question_or_answer(data_type: str, question_or_answer: dict = None, updated_data: dict = None) -> None:
    data = connection.load_data(data_type)

    if question_or_answer in data:
        find_index = data.index(question_or_answer)
        data[find_index].update(updated_data)

    if data_type == "questions":
        connection.write_all_data(connection.question_file, data, connection.QUESTION_FIELDS)

    elif data_type == 'answers':
        connection.write_all_data(connection.answers_file, data, connection.ANSWER_FIELDS)
