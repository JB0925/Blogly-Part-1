from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from decouple import config

from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

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
        posts = user.posts
        return render_template('userdisplay.html', user=user, posts=posts)
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


@app.route('/users/<id>/posts/new', methods=['GET', 'POST'])
def add_post(id):
    user = User.query.get(id)
    if user:
        if request.method == 'GET':
            return render_template('add_post.html', user=user)
        
        form = request.form
        print(form)
        post = Post(title=form['title'], content=form['content'], created_at=datetime.now(), user_id=id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('show_user', id=id))
    
    return redirect(url_for('not_found'))


@app.route('/posts/<postid>')
def show_post(postid):
    post = Post.query.get(postid)
    if post:
        return render_template('show_post.html', post=post)
    return redirect(url_for('not_found'))


@app.route('/posts/<postid>/edit', methods=['GET', 'POST'])
def edit_post(postid):
    print(str(datetime.now()))
    post = Post.query.get(postid)
    if post:
        if request.method == 'GET':
            return render_template('edit_post.html', post=post)
        
        form = request.form
        categories = 'title content'.split()
        for i in range(len(categories)):
            if i == 0 and form['title']:
                post.title = form['title']
            else:
                if form['content']:
                    post.content = form['content']

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('show_post', postid=post.id))
    return redirect(url_for('not_found'))


@app.route('/posts/<postid>/delete')
def delete_post(postid):
    post = Post.query.get(postid)
    user_id = post.users.id
    if post:
        db.session.delete(post)
        db.session.commit()
    
    return redirect(url_for('show_user', id=user_id))


@app.route('/404')
def not_found():
    return render_template('404.html')