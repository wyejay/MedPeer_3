from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import User, Post, Flag, AdminAction
from . import db
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__)

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        return fn(*args, **kwargs)
    return wrapper

@bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
    flags = Flag.query.order_by(Flag.created_at.desc()).limit(50).all()
    return render_template('admin/dashboard.html', users=users, posts=posts, flags=flags)

@bp.route('/user/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    u = User.query.get_or_404(user_id)
    u.is_active = False
    db.session.add(AdminAction(admin_id=current_user.id, action='suspend', target=f'user:{u.id}'))
    db.session.commit()
    flash('User suspended', 'success')
    return redirect(url_for('admin.dashboard'))
