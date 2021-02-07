from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from util import os
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm, QuestionForm
from flask_login import current_user, login_required
import data_manager
import util

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.update(
    ENV='development',
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
    MAX_CONTENT_LENGTH=3 * 1024 * 1024,
    UPLOAD_EXTENSIONS=['.jpg', '.png', '.jpeg'],
    UPLOAD_PATH='static/img')

app.jinja_env.globals.update(
    func_tags=data_manager.count_tags,
    questions_count=data_manager.count_questions
)


def save_image(file_ext, img, img_name):
    if file_ext in app.config['UPLOAD_EXTENSIONS']:
        img.save(os.path.join(app.config['UPLOAD_PATH'], img_name))
        return True

    elif img and file_ext not in app.config['UPLOAD_EXTENSIONS']:
        return False


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(413)
def too_large(e):
    flash('File too large. You can upload only 3MB')
    return redirect(url_for('route_add_question', )), 413, {"Refresh": "0; url=/add-question"}


@app.route("/register", methods=['GET', 'POST'])
def route_register():
    form = RegistrationForm(request.form)
    if request.method == 'GET':
        return render_template('register.html', form=form)

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    img = request.files['picture']
    img_name = img.filename

    if len(img_name) > 0:
        img_name = secure_filename(img_name)
        file_ext = os.path.splitext(img_name)[1]

        if not save_image(file_ext=file_ext, img=img, img_name=img_name):
            flash('Wrong image extension, you can upload only .jpg, jpeg and .png files', 'danger')
            return redirect(request.referrer)
    else:
        img_name = 'default.png'

    if password != confirm_password:
        flash("Passwords are not the same!")
        return render_template('register.html', form=form)
    hash_pswd = util.hash_password(password)
    data_manager.register_new_user(username, email, hash_pswd, picture=img_name)
    flash("Welcome in our team :) !!!")
    return redirect("register")


@app.route("/logout", methods=["GET"])
def route_logout():
    session.pop("email", None)
    resp = make_response(redirect(url_for('route_list')))
    resp.set_cookie('user_name', 'user')
    flash("See You later :) !")
    return resp


@app.route("/")
@app.route("/list", methods=['GET', 'POST'])
def route_list(order_by=data_manager.DEFAULT_ORDER_BY, order_direction=data_manager.DEFAULT_ORDER_DIR):
    questions = []
    is_search = False
    pagination_size = 20
    switch_order_direction = ''
    last_order_by = order_by
    last_tag_id = 'all'
    last_search_phrase = ''

    #---------------------Sorting
    if request.args.get('order_by') is not None:
        last_order_by = request.args.get('last_order_by')
        order_by = request.args.get('order_by')
        order_direction = request.args.get('order_direction')
        if order_by == last_order_by:
            switch_order_direction = data_manager.switch_asc_desc(order_direction=order_direction)
        else:
            if order_by == 'title':
                switch_order_direction = 'ASC'
            else:
                switch_order_direction = 'DESC'
    elif request.args.get('last_order_by') is not None:
        last_order_by = request.args.get('last_order_by')
        order_by = last_order_by
        order_direction = request.args['asc_desc']
        switch_order_direction = request.args['asc_desc']
    else:
        switch_order_direction = 'DESC'

    #---------------------Tags
    if 'last_tag_id' in request.args and request.args['last_tag_id'] != last_tag_id:
        last_tag_id = request.args['last_tag_id']
        questions = data_manager.get_questions_data_by_tag(
            sort_column_by=order_by, asc_desc=switch_order_direction, tag_id=str(last_tag_id))
    elif 'tag_id' in request.args:
        last_tag_id = request.args['tag_id']
        questions = data_manager.get_questions_data_by_tag(
            sort_column_by=order_by, asc_desc=switch_order_direction, tag_id=request.args['tag_id'])
    else:
        questions = data_manager.get_questions_data(sort_column_by=order_by, asc_desc=switch_order_direction)
        last_tag_id = 'all'

    # ---------------------Search
    if 'search_phrase' in request.form:
        questions = data_manager.search_phrase(questions=questions, phrase=request.form.get('search_phrase'))
        is_search = True
        last_search_phrase = request.form.get('search_phrase')
    elif 'last_search_phrase' in request.args:
        if request.args['last_search_phrase'] != '':
            questions = data_manager.search_phrase(questions=questions, phrase=request.args['last_search_phrase'])
            is_search = True
            last_search_phrase = request.args['last_search_phrase']

    # ---------------------Pagination
    pagination_index = request.args['pagination_index'] if 'pagination_index' in request.args else 0
    pag_questions = (data_manager.pagination(data=questions, pagination_range=pagination_size))
    questions = pag_questions[int(pagination_index)]

    # ---------------------Render

    resp = make_response(render_template(
        'list.html', questions=questions, asc_desc=switch_order_direction,
        pagination_count=len(pag_questions), last_tag_id=last_tag_id, last_order_by=order_by, is_search=is_search,
        last_search_phrase=last_search_phrase
    ))
    if 'email' not in session:
        resp.set_cookie('user_name', 'user')
        resp.set_cookie('email', '')
    return resp


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    if request.method == 'GET':

        tags = data_manager.fetch_tags()

        return render_template("add_question.html", question=None, tags=tags)

    data = request.form
    new_question_all_data = data_manager.add_question()
    img = request.files['file']
    img_name = img.filename

    if len(img_name) > 0:
        img_name = secure_filename(img_name)
        file_ext = os.path.splitext(img_name)[1]

        if not save_image(file_ext=file_ext, img=img, img_name=img_name):
            flash('Wrong image extension, you can upload only .jpg, jpeg and .png files', 'danger')
            return redirect(request.referrer)
    else:
        img_name = 'default.png'

    new_question_all_data.update(
        {
            "title": request.form.get('title'),
            "message": request.form.get('message'),
            "image": img_name,
            "tag_id": request.form.get('tag_name')
        }
    )

    if 'email' in session:
        user_name = data_manager.get_user_name_by_email(email=session.get('email'))
        new_question_all_data.update({'user_name': user_name[0]['user_name']})
    else:
        new_question_all_data.update({'user_name': 'user'})

    data_manager.save_question(new_question_all_data)

    return redirect(url_for('route_list'))


@app.route('/edit/<int:question_id>', methods=['GET', 'POST'])
def route_edit_question(question_id):
    question = data_manager.find_question_by_id(question_id=question_id)

    if question == None:
        return redirect(url_for('route_list'))

    if request.method == 'GET':
        tags = data_manager.fetch_tags()
        for element in tags:
            tags.remove(element) if element['tag_name'] == list(question)[0]['tag'] else None
        return render_template('add_question.html', question=list(question)[0], tags=tags)

    elif request.method == 'POST':
        img = request.files['file']
        img_name = img.filename
        if len(img_name) > 0:
            img_name = secure_filename(img_name)
            file_ext = os.path.splitext(img_name)[1]

            if not save_image(file_ext=file_ext, img=img, img_name=img_name):
                flash('Wrong image extension, you can upload only .jpg, jpeg and .png files')
                return redirect(request.referrer)
        else:
            img_name = question[0]['image']
        new_question = {
            "title": request.form.get('title'),
            "message": request.form.get('message'),
            "image": img_name
        }
        data_manager.edit_question(question_id, new_question)
        return redirect(url_for('route_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/<int:question_id>', methods=['GET', 'POST'])
def route_edit_answer(answer_id, question_id):
    answer = data_manager.find_answer_by_id(answer_id=answer_id)
    question = data_manager.find_question_by_id(question_id=question_id)

    if answer == None:
        return render_template('404.html')

    if request.method == 'GET':
        return render_template('edit_answer.html', answer=answer, question=question)

    if request.method == 'POST':
        new_data = {
            "message": request.form.get('message'),
            "image": request.form.get('image')
        }
        data_manager.edit_answer(answer_id, new_data)

        return redirect(url_for('route_question', question_id=question_id))


@app.route("/question/<int:question_id>/", methods=["GET", "POST"])
def route_question(question_id):
    question = data_manager.find_question_by_id(question_id=question_id)
    answers_list = data_manager.find_all_answers_by_question_id(question_id=question_id)
    data_to_modify = dict(request.args)
    list_comments_for_question = data_manager.find_comment_by_question_id(question_id=question_id)

    answer_id = None

    if question == None:
        return render_template('404.html')

    if data_to_modify:
        try:
            answer_id = int(data_to_modify.get('answer_id'))
        except:
            pass

        if 'remove_question' in data_to_modify:
            data_manager.remove_question(question_id=question_id)
            return redirect(url_for('route_list'))

        elif 'remove_answer' in data_to_modify:
            data_manager.remove_answer(question_id=question_id, answer_id=answer_id)
            return redirect(url_for('route_question', question_id=question_id))

        reputation_target = []
        if 'reputation_target' in request.args:
            reputation_target = request.args.get('reputation_target')

        data_manager.modify_views_votes(data_to_modify=data_to_modify, question=question, answers_list=answers_list,
                                        reputation_target=reputation_target,
                                        reputation_giver=data_manager.get_user_name_by_email(session.get('email'))[0]['user_name'])

        return redirect(url_for('route_question', question_id=question_id))

    if request.method == 'GET':

        list_comments_for_answers = data_manager.find_comment_by_answer_id

        q_pos_neg = data_manager.question_positive_negative_vote(question_id=question_id)
        a_pos_neg = data_manager.answers_positive_negative_vote(question_id=question_id)

        return render_template('question.html', question=question[0], answers=answers_list,
                               comments_for_question=list_comments_for_question,
                               comments_for_answers=list_comments_for_answers, a_pos_neg=a_pos_neg,
                               q_pos_neg=q_pos_neg)

    elif request.method == 'POST':
        new_answer = {'message': request.form["message"]}
        if 'email' in session:
            new_answer['user_name'] = data_manager.get_user_name_by_email(session.get('email'))[0]['user_name']
        else:
            new_answer['user_name'] = 'user'
        data_manager.add_answer(new_answer['message'], question_id, user_name=new_answer['user_name'])
        return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<int:question_id>/new_question_comment", methods=["GET", "POST"])
def route_add_comment_for_question(question_id):
    if request.method == "POST":
        new_comment = {
            "message": request.form.get('comments_for_question'),
            "type": 'question',
            "answer_id": None,
            "question_id": question_id
        }
        if 'email' in session:
            user_name = data_manager.get_user_name_by_email(email=session.get('email'))
            new_comment.update({'user_name': user_name[0]['user_name']})
        else:
            new_comment.update({'user_name': 'user'})

        data_manager.add_comment(new_comment)
        return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<int:question_id>/<int:answer_id>", methods=["GET", "POST"])
def route_add_comment_for_answer(question_id, answer_id):
    if request.method == "POST":
        question = request.form
        new_comment = {
            "message": request.form.get('comments_for_answer'),
            "type": 'answer',
            "answer_id": answer_id,
            "question_id": None
        }

        if 'email' in session:
            user_name = data_manager.get_user_name_by_email(email=session.get('email'))
            new_comment.update({'user_name': user_name[0]['user_name']})
        else:
            new_comment.update({'user_name': 'user'})

        data_manager.add_comment(new_comment)
        return redirect(url_for("route_question", question_id=question_id))


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "GET":
        return render_template("login.html", form=form)

    email = request.form['email']
    plain_password = request.form['password']

    if data_manager.find_user_email(email):
        hashed_pswd = data_manager.get_password_database(email)
        if util.check_password(plain_password, hashed_pswd):
            session['email'] = email
            flash("You are logged in!")
            resp = make_response(redirect(url_for("route_list", form=form)))
            resp.set_cookie('user_name', data_manager.get_user_name_by_email(email=email)[0]["user_name"])
            resp.set_cookie('email', email)
            return resp
    flash("Invalid email or password, try again!")
    return render_template("login.html", form=form)


@app.route("/reputation")
def route_reputation() -> 'html':
    users = data_manager.get_users_data()
    return render_template('reputation_list.html', users=users)


@app.route("/account")
def route_account() -> 'html':
    user_name = request.args.get("user_name")
    user_data = data_manager.get_user_data(user_name)


    return render_template('account.html', user_data = user_data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
