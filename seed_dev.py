# Seed script to create dev users and sample posts (includes 3 admin accounts)
import os
from app import create_app, db
from app.models import User, Post
app = create_app()
app.app_context().push()

def seed():
    db.create_all()
    if User.query.count() > 0:
        print('Already seeded')
        return
    admins = []
    for i in range(1,4):
        u = User(email=f'admin{i}@example.com', username=f'admin{i}', role='admin')
        u.set_password('AdminPass!234')
        admins.append(u)
        db.session.add(u)
    for i in range(1,8):
        u = User(email=f'user{i}@example.com', username=f'user{i}', role='student')
        u.set_password('UserPass!234')
        db.session.add(u)
    db.session.commit()
    # sample posts
    users = User.query.limit(5).all()
    for i, u in enumerate(users, start=1):
        p = Post(user_id=u.id, title=f'Sample {i}', body='This is sample content to bootstrap the app.')
        db.session.add(p)
    db.session.commit()
    print('Seed complete. Admins: admin1@..., admin2@..., admin3@... (password AdminPass!234)')

if __name__ == '__main__':
    seed()
