from flask import Flask, render_template, request, redirect, url_for
from decouple import config

from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()


@app.route('/')
def home():
    return redirect(url_for('user_list'))


@app.route('/users')
def user_list():
    users = User.query.all()
    if users:
        users = [[f'{user.last_name}, {user.first_name}', user.id] for user in users]
        return render_template('userlist.html', users=users)
    
    return render_template('userlist.html')


@app.route('/users/new', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('userform.html')
    
    form = request.form
    first = form['first']
    last = form['last']
    image = form['image']

    if image:
        user = User(first_name=first, last_name=last, image_url=image)
    else:
        user = User(first_name=first, last_name=last)
    
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('user_list'))


@app.route('/users/<id>')
def show_user(id):
    user = User.query.get(id)
    if user:
        return render_template('userdisplay.html', user=user)
    return redirect(url_for('not_found'))


@app.route('/users/<id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    user = User.query.get(id)
    categories = 'first_name last_name image_url'.split()
    if user:
        if request.method == 'GET':
            return render_template('edit.html', id=user.id)
    
        form = request.form
        for i in range(len(categories)):
            if form[categories[i]]:
                if i == 0:
                    user.first_name = form[categories[i]]
                elif i == 1:
                    user.last_name = form[categories[i]]
                else:
                    user.image_url = form[categories[i]]

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_list', id=user.id))
    else:
        return redirect(url_for('user_list'))


@app.route('/users/<id>/delete')
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    
    return redirect(url_for('user_list'))


@app.route('/404')
def not_found():
    return render_template('404.html')