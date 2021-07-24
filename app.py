from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from decouple import config

from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
db.create_all()


def filter_tags_and_save(tags, other_id, form):
    for tag in tags:
        if tag.name in form:
            pt = PostTag(post_id=other_id, tag_id=tag.id)
            db.session.add(pt)
            db.session.commit()
    return

@app.route('/')
def home():
    """Route used to redirect to the main page
       of all users."""
    return redirect(url_for('user_list'))


@app.route('/users')
def user_list():
    """The main page that displays all registered users."""
    users = User.query.all()
    if users:
        users = [[f'{user.last_name}, {user.first_name}', user.id] for user in users]
        return render_template('userlist.html', users=users)
    
    return render_template('userlist.html')


@app.route('/users/new', methods=['GET', 'POST'])
def add_user():
    """Adds a user to the db and the user profiles page"""
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
    """Shows a user's profile."""
    user = User.query.get(id)
    if user:
        posts = user.posts
        return render_template('userdisplay.html', user=user, posts=posts)
    return redirect(url_for('not_found'))


@app.route('/users/<id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    """Returns a form for a user to edit their profile."""
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
    """When the delete profile button is clicked, 
       profile deletion is handled via this route,
       and the user is redirected to the main page."""
    user = User.query.get(id)
    if user:
        for post in user.posts:
            db.session.delete(post)
        db.session.delete(user)
        db.session.commit()
    
    return redirect(url_for('user_list'))


@app.route('/users/<id>/posts/new', methods=['GET', 'POST'])
def add_post(id):
    """Adds a post to the database and links it
       with a user, IF the user id is valid."""
    user = User.query.get(id)
    if user:
        tags = Tag.query.all()
        if request.method == 'GET':
            return render_template('add_post.html', user=user, tags=tags)
        
        form = request.form
        post = Post(title=form['title'], content=form['content'], created_at=datetime.now(), user_id=id)
        db.session.add(post)
        db.session.commit()
        post = Post.query.all()[-1]
        filter_tags_and_save(tags, post.id, form.getlist('tag'))
        return redirect(url_for('show_user', id=id))
    
    return redirect(url_for('not_found'))


@app.route('/posts/<postid>')
def show_post(postid):
    """When a post link is clicked, this link handles
       routing the user to the post."""
    post = Post.query.get(postid)
    if post:
        tags = post.tags
        return render_template('show_post.html', post=post, tags=tags)
    return redirect(url_for('not_found'))


@app.route('/posts/<postid>/edit', methods=['GET', 'POST'])
def edit_post(postid):
    """Allows a user to edit a post and change either
       the title, content, or both."""
    post = Post.query.get(postid)
    if post:
        tags = Tag.query.all()
        if request.method == 'GET':
            return render_template('edit_post.html', post=post, tags=tags)
        
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
        filter_tags_and_save(tags, post.id, form.getlist('tag'))
        return redirect(url_for('show_post', postid=post.id))
    return redirect(url_for('not_found'))


@app.route('/posts/<postid>/delete')
def delete_post(postid):
    """Similar to the delete user route, this handles
       deletion of a post from the database, and thus
       the UI."""
    post = Post.query.get(postid)
    user_id = post.users.id
    if post:
        db.session.delete(post)
        db.session.commit()
    
    return redirect(url_for('show_user', id=user_id))


@app.route('/tags/new', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'GET':
        return render_template('add_tags.html')
    
    form = request.form
    new_tag = Tag(name=form['newtag'])
    db.session.add(new_tag)
    db.session.commit()
    return redirect(url_for('show_tags'))


@app.route('/tags')
def show_tags():
    all_tags = Tag.query.all()
    return render_template('show_tags.html', tags=all_tags)


@app.route('/tags/<tag_id>')
def get_tag_by_id(tag_id):
    tag = Tag.query.get(tag_id)
    if tag:
        return render_template('one_tag.html', tag=tag)
    return redirect(url_for('not_found'))


@app.route('/tags/<tag_id>/edit', methods=['GET', 'POST'])
def edit_tags(tag_id):
    tag = Tag.query.get(tag_id)
    if tag:
        if request.method == 'GET':
            return render_template('edit_tag.html', tag=tag)
        
        form = request.form
        new_tag_name = form['changedtag']
        tag.name = new_tag_name
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('get_tag_by_id', tag_id=tag.id))


@app.route('/tags/<tag_id>/delete')
def delete_tag(tag_id):
    """Similar to the delete user route, this handles
       deletion of a tag from the database, and thus
       the UI."""
    tag = Tag.query.get(tag_id)
    if tag:
        for posttag in tag.join_tags:
            db.session.delete(posttag)
        db.session.delete(tag)
        db.session.commit()
    
    return redirect(url_for('show_tags'))


@app.route('/404')
def not_found():
    """A catch all page that is used when the user types
       in a bad route. It automatically redirects after 
       three seconds."""
    return render_template('404.html')