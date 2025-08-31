from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash, jsonify, send_file
from .models import User, Post, File, Message
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .storage import upload_file_to_s3
import os, uuid, io

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/')
def index():
    q = request.args.get('q','')
    if q:
        posts = Post.query.filter(Post.body.ilike(f'%{q}%')).order_by(Post.created_at.desc()).limit(20).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
    return render_template('index.html', posts=posts)

@bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        username = request.form['username'].strip()
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('main.signup'))
        if User.query.filter_by(username=username).first():
            flash('Username taken', 'danger')
            return redirect(url_for('main.signup'))
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('main.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('main.index'))

@bp.route('/profile/<username>', methods=['GET','POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST' and user.id == current_user.id:
        current_user.bio = request.form.get('bio','')
        current_user.institution = request.form.get('institution','')
        current_user.year_level = request.form.get('year_level','')
        # dark mode toggle
        current_user.dark_mode = bool(request.form.get('dark_mode',False))
        # avatar upload
        avatar = request.files.get('avatar')
        if avatar:
            res = upload_file_to_s3(avatar, filename=f"avatars/{uuid.uuid4()}_{avatar.filename}")
            current_user.profile_pic = res.get('url') or res.get('storage_key')
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('profile.html', user=user)

@bp.route('/post/create', methods=['GET','POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title','')
        body = request.form.get('body','')
        post = Post(user_id=current_user.id, title=title, body=body)
        db.session.add(post)
        db.session.commit()
        files = request.files.getlist('files')
        for f in files:
            if f:
                res = upload_file_to_s3(f, filename=f"posts/{uuid.uuid4()}_{f.filename}")
                file_rec = File(post_id=post.id, filename=f.filename, content_type=f.content_type, size=0, storage_key=res.get('storage_key'))
                db.session.add(file_rec)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_post.html')

@bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    f = File.query.get_or_404(file_id)
    # For S3, return a signed URL or proxy download; here we proxy local files if provider=local
    if os.path.exists(f.storage_key):
        return send_file(f.storage_key, as_attachment=True, download_name=f.filename)
    # otherwise redirect to S3 public URL (remember we uploaded as private; production should generate presigned URL)
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_REGION','us-east-1')
    if bucket and f.storage_key:
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{f.storage_key}"
        return redirect(url)
    return 'File not available', 404

# Basic API for posts (JSON)
@bp.route('/api/posts', methods=['GET'])
def api_posts():
    page = int(request.args.get('page',1))
    per = int(request.args.get('per',10))
    q = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per, error_out=False)
    items = []
    for p in q.items:
        items.append({'id':p.id,'title':p.title,'body':p.body,'created_at':p.created_at.isoformat(),'author':p.author.username})
    return jsonify({'items':items,'page':page,'total':q.total})

# Simple search endpoint
@bp.route('/search')
def search():
    q = request.args.get('q','').strip()
    users = []
    posts = []
    if q:
        users = User.query.filter(User.username.ilike(f'%{q}%')).limit(10).all()
        posts = Post.query.filter(Post.body.ilike(f'%{q}%') | Post.title.ilike(f'%{q}%')).limit(20).all()
    return render_template('search.html', users=users, posts=posts, q=q)
