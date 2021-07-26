from unittest import TestCase
from datetime import datetime

from decouple import config
from werkzeug.wrappers import request

from app import app
from models import User, Post, db

app.config['SQLALCHEMY_DATABASE_URI'] = config('TEST_DB')
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class BloglyTestCase(TestCase):
    def setUp(self):
        User.query.delete()
    

    def tearDown(self) -> None:
        db.session.rollback()
    

    def make_user(self):
        user = User(first_name='Brian', last_name='Ramirez')
        db.session.add(user)
        db.session.commit()
        return user
    
    def delete_user(self, user):
        db.session.delete(user)
        db.session.commit()


    def test_users_route(self):
        with app.test_client() as client:
            resp = client.get('/')
            self.assertEqual(resp.status_code, 302)
            new_resp = client.get('/users')
            self.assertEqual(new_resp.status_code, 200)
    

    def test_profile_pages(self):
        with app.test_client() as client:
            user = self.make_user()
            resp = client.get(f'/users/{user.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>First Name: Brian</p>', resp.get_data(as_text=True))
            bad_route = client.get('/users/29', follow_redirects=True)
            self.assertEqual(bad_route.status_code, 200)
            self.assertIn('<h1>We\'re Sorry!</h1>', bad_route.get_data(as_text=True))
            self.delete_user(user)
    

    def test_edit_page(self):
        user = self.make_user()
        user = User.query.first()
        with app.test_client() as client:
            data = {
                'first_name': 'Marcelo',
                'last_name': '',
                'image_url': ''
            }

            resp = client.post(f'/users/{user.id}/edit', data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<li><a href="/users/{user.id}">Ramirez, Marcelo</a></li>', resp.get_data(as_text=True))
        self.delete_user(user)
            

    def test_delete_profile(self):
        user = self.make_user()
        user = User.query.first()
        with app.test_client() as client:
            resp = client.get(f'/users/{user.id}/delete')
            self.assertEqual(resp.status_code, 302)
            all_users = User.query.all()
            self.assertEqual(all_users, [])
        self.delete_user(user)
    

    def test_add_profile(self):
        user = self.make_user()
        data = {
                'first': 'Jake',
                'last': 'State Farm',
                'image': ''
        }
        with app.test_client() as client:
            resp = client.post('/users/new', data=data)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(User.query.all()), 2)
            self.assertNotEqual(user, None)
        self.delete_user(user)
    

    def test_add_post(self):
        with app.test_client() as client:
            user = self.make_user()
            data = dict(title= 'This is my title.', content='And this is my content', user_id=user.id)
            resp = client.post(f'/users/{1}/posts/new', data=data)
            # post = Post.query.first()
            self.assertEqual(resp.status_code, 302)
            # self.assertNotEqual(post, None)
            self.assertEqual(user.id, 1)
            self.assertIn(str(user.id), resp.get_data(as_text=True))
        self.delete_user(user)
            
            