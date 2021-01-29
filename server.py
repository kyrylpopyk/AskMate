from flask import Flask, render_template, request, redirect, url_for, flash, session
from util import os
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm, QuestionForm
import data_manager

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
    print(session)
    print(request.form)
    form = RegistrationForm()

    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def route_login():
    print(request.form)
    print(session)
    form = LoginForm()

    return render_template('login.html', form=form)


@app.route("/logout")
def route_logout():
    # logout_user()
    return redirect(url_for('route_list'))


@app.route("/")
@app.route("/list", methods=['GET'])
def route_list(order_by=data_manager.DEFAULT_ORDER_BY, order_direction=data_manager.DEFAULT_ORDER_DIR):
    pagination_size = 20
    switch_order_direction = ''
    last_order_by = order_by
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

    questions = []
    last_tag_id = 'all'

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

    questions = data_manager.pagination(data=questions, pagination_range=20)


    pagination_index = request.args['pagination_index'] if 'pagination_index' in request.args else 0

    return render_template(
        'list.html', questions=questions[int(pagination_index)], asc_desc=switch_order_direction,
        pagination_count=len(questions), last_tag_id=last_tag_id, last_order_by=order_by
    )


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

    data_manager.save_question(new_question_all_data)

    return redirect(url_for('route_list'))


@app.route('/edit/<int:question_id>', methods=['GET', 'POST'])
def route_edit_question(question_id):
    question = data_manager.find_question_by_id(question_id=question_id)

    if question == None:
        return redirect(url_for('route_list'))

    if request.method == 'GET':
        tags = data_manager.fetch_tags()
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

        data_manager.modify_views_votes(data_to_modify=data_to_modify, question=question, answers_list=answers_list)
        return redirect(url_for('route_question', question_id=question_id))

    if request.method == 'GET':
        list_comments_for_answers = data_manager.find_comment_by_answer_id

        return render_template('question.html', question=question[0], answers=answers_list, comments_for_question=list_comments_for_question, comments_for_answers=list_comments_for_answers)

    elif request.method == 'POST':
        new_answer = request.form["message"]
        data_manager.add_answer(new_answer, question_id)
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
    data_manager.add_comment(new_comment)
    return redirect(url_for("route_question", question_id=question_id))



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
