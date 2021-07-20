from unittest import TestCase
from datetime import datetime

from decouple import config

from app import app
from models import User, Post, db

app.config['SQLALCHEMY_DATABASE_URI'] = config('TEST_DB')
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class BloglyTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        user = User(first_name='Brian', last_name='Ramirez')
        db.session.add(user)
        db.session.commit()
    

    def tearDown(self) -> None:
        db.session.rollback()


    def test_users_route(self):
        with app.test_client() as client:
            resp = client.get('/')
            self.assertEqual(resp.status_code, 302)
            new_resp = client.get('/users')
            self.assertEqual(new_resp.status_code, 200)
    

    def test_profile_pages(self):
        with app.test_client() as client:
            user = User.query.filter_by(first_name='Brian').first()
            resp = client.get(f'/users/{user.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>First Name: Brian</p>', resp.get_data(as_text=True))
            bad_route = client.get('/users/29', follow_redirects=True)
            self.assertEqual(bad_route.status_code, 200)
            self.assertIn('<h1>We\'re Sorry!</h1>', bad_route.get_data(as_text=True))
    

    def test_edit_page(self):
        user = User.query.filter_by(first_name='Brian').first()
        with app.test_client() as client:
            data = {
                'first_name': 'Marcelo',
                'last_name': '',
                'image_url': ''
            }

            resp = client.post(f'/users/{user.id}/edit', data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<li><a href="/users/{user.id}">Ramirez, Marcelo</a></li>', resp.get_data(as_text=True))
            

    def test_delete_profile(self):
        user = User.query.filter_by(first_name='Brian').first()
        with app.test_client() as client:
            resp = client.get(f'/users/{user.id}/delete')
            self.assertEqual(resp.status_code, 302)
            all_users = User.query.all()
            self.assertEqual(all_users, [])
    

    def test_add_profile(self):
        data = {
                'first': 'Jake',
                'last': 'State Farm',
                'image': ''
        }
        with app.test_client() as client:
            resp = client.post('/users/new', data=data)
            self.assertEqual(resp.status_code, 302)
            all_users = User.query.all()
            self.assertEqual(len(all_users), 2)
    

    def test_add_post(self):
        data = {
            'title': 'This is my title.',
            'content': 'And this is my content'
        }
        with app.test_client() as client:
            resp = client.post(f'/users/{7}/posts/new', data=data)
            self.assertEqual(resp.status_code, 302)
            