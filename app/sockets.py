# Basic socket handlers: join private rooms for one-to-one messaging
from . import socketio, db
from flask_socketio import emit, join_room, leave_room
from .models import Message, User
from flask_login import current_user
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    print('socket connected')

@socketio.on('private_join')
def on_private_join(data):
    # data: {'room':'user1_user2'}
    room = data.get('room')
    join_room(room)
    emit('status', {'msg':'joined '+room}, room=room)

@socketio.on('private_message')
def on_private_message(data):
    # data contains: room, to_user_id, message
    room = data.get('room')
    to_user = data.get('to_user')
    body = data.get('message')
    # Save message to DB if possible
    try:
        m = Message(sender_id=current_user.id, recipient_id=to_user, body=body, created_at=datetime.utcnow())
        db.session.add(m)
        db.session.commit()
    except Exception as e:
        print('socket save error', e)
    emit('new_message', {'from': current_user.username, 'body': body, 'created_at': datetime.utcnow().isoformat()}, room=room)
