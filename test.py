from unittest import TestCase
from datetime import datetime

from decouple import config
from werkzeug.wrappers import request

from app import app
from models import User, Post, Tag, db

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
    
    def make_post(self, id):
        post = Post(title='hi', content='hello', created_at=datetime.now(), user_id=id)
        db.session.add(post)
        db.session.commit()
        return post
    
    def delete_post(self, post):
        db.session.delete(post)
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
            data = dict(title= 'This is my title.', content='And this is my content')
            resp = client.post(f'/users/{1}/posts/new', data=data)
            post = Post.query.first()
            self.assertEqual(resp.status_code, 302)
            self.assertNotEqual(post, None)
            self.assertEqual(user.id, 1)
            self.assertIn(str(user.id), resp.get_data(as_text=True))
        self.delete_user(user)
    

    def test_show_posts(self):
        with app.test_client() as client:
            user = self.make_user()
            post = self.make_post(user.id)
            resp = client.get(f'/posts/{post.id}')
            self.assertEqual(resp.status_code, 200)
            resp2 = client.get(f'/posts/{401}')
            self.assertEqual(resp2.status_code, 302)
        self.delete_user(user)
        self.delete_post(post)
    
    
    def test_edit_post(self):
        with app.test_client() as client:
            user = self.make_user()
            post = self.make_post(user.id)
            data = dict(title='new title.com', content='ok, new content', tag='yay!')
            resp = client.post(f'/posts/{post.id}/edit', data=data)
            self.assertEqual(resp.status_code, 302)
        self.delete_post(post)
        self.delete_user(user)
    

    def test_delete_post(self):
        with app.test_client() as client:
            user = self.make_user()
            post = self.make_post(user.id)
            resp = client.get(f'/posts/{post.id}/delete')
            self.assertEqual(resp.status_code, 302)
            all_posts = Post.query.all()
            self.assertEqual(len(all_posts), 0)
        self.delete_user(user)
        self.delete_post(post)
    

    def test_add_tag(self):
        with app.test_client() as client:
            data = dict(newtag='wow!')
            resp = client.post('/tags/new', data=data, follow_redirects=True)
            tag = Tag.query.first()
            self.assertEqual(resp.status_code, 200)
            self.assertIn(tag.name, resp.get_data(as_text=True))
    

    def test_show_tags(self):
        with app.test_client() as client:
            newtag = Tag(name='hello!')
            db.session.add(newtag)
            db.session.commit()
            tag = Tag.query.first()
            resp = client.get('/tags')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(tag.name, resp.get_data(as_text=True))
            db.session.delete(tag)
            db.session.commit()
    

    def test_edit_tag(self):
        with app.test_client() as client:
            newtag = Tag(name='yeah!')
            db.session.add(newtag)
            db.session.commit()
            tag = Tag.query.first()
            data = {'changedtag': 'uhuhuh'}
            resp = client.post(f'/tags/{tag.id}/edit', data=data, follow_redirects=True)
            tag = Tag.query.all()[-1]
            self.assertEqual(resp.status_code, 200)
            self.assertIn(tag.name, resp.get_data(as_text=True))
            db.session.delete(tag)
            db.session.commit()
    

    def test_delete_tag(self):
        with app.test_client() as client:
            newtag = Tag(name='sure')
            db.session.add(newtag)
            db.session.commit()
            tag = Tag.query.all()[-1]
            all_tags_length = len(Tag.query.all())
            resp = client.get(f'/tags/{tag.id}/delete')
            tag = Tag.query.all()[-1]
            new_tags_length = len(Tag.query.all())
            self.assertEqual(resp.status_code, 302)
            self.assertLess(new_tags_length, all_tags_length)
            self.assertNotEqual(tag.name, 'sure')
    

    def test_404_route(self):
        with app.test_client() as client:
            resp = client.get('/404')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sorry', resp.get_data(as_text=True))
