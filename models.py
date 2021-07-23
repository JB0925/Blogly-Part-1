from enum import unique
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String, default='https://cdn5.vectorstock.com/i/thumb-large/66/14/default-avatar-photo-placeholder-profile-picture-vector-21806614.jpg')

    posts = db.relationship('Post')

    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, first={self.first_name}, last={self.last_name}, img={self.image_url}'


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    users = db.relationship('User')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, title={self.title}, created_at={self.created_at}, users={self.users}'
        