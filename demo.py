from app import app
from app import app, db
from app.models import User, Post
from datetime import datetime
app.app_context().push()

# Create data
# --------------
# u = User(username='john', email='john@example.com')
# db.session.add(u)
# db.session.commit()
#
# u = User(username='susan', email='susan@example.com')
# db.session.add(u)
# db.session.commit()
#
# p = Post(id=1, temp1=12, temp2=13, time1=14, time2=15, status=1, comment="first", user_id=1)
# db.session.add(p)
# db.session.commit()

# Get All data in class
# --------------
# users = User.query.all()
# for u in users:
#     print(u.id, u.username)
# posts = Post.query.all()
# for p in posts:
#     print(p.id, p.author.username, p.body, p.timestamp)

# Get post by writer
# --------------
# u = User.query.get(1)
# print(u)
# posts = u.posts.all()
# print(posts)
# u = User.query.get(2)
# print(u)
# posts = u.posts.all()
# print(posts)

# Get data in class
# --------------
# u = User.query.get(1)
# print(u)
# p = Post.query.get(1)
# print(p)

# Clear database
# --------------
# users = User.query.all()
# for u in users:
#     db.session.delete(u)
#
# posts = Post.query.all()
# for p in posts:
#     db.session.delete(p)
#
# db.session.commit()
#
# users = User.query.all()
# print(users)
# posts = Post.query.all()
# print(posts)

# Password Hashing
# from werkzeug.security import generate_password_hash
# from werkzeug.security import check_password_hash
# hash = generate_password_hash('foobar')
# print(hash)
# print(check_password_hash(hash, 'barfoo'))
# print(check_password_hash(hash, 'foobar'))

# Set Check password
# u = User(username='susan', email='susan@example.com')
# u.set_password('mypassword')
# print(u.check_password('anotherpassword'))
# print(u.check_password('mypassword'))

# Firebase connection
# from firebase import firebase
# firebase = firebase.FirebaseApplication('https://demo01-7dd93-default-rtdb.firebaseio.com', None)
# # get
# print(firebase.get('/user', None))
# print(firebase.get('/user', '1'))
# print(firebase.get('/user', 2))
# print(firebase.get('/user', '3'))
# print(firebase.get('/user', '4'))
# print(firebase.get('/user', '4a'))
# # post
# data =  { 'Name': 'John Doe',
#           'RollNo': 3,
#           'Percentage': 70.02
#           }
# result = firebase.post('/python-example-f6d0b/Students/',data)
# print(result)
# # update
# firebase.put('/user','4a','1000')
# print('Record Updated')
