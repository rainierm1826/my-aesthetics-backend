from flask_socketio import emit, join_room, leave_room
from .extension import socketio

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'Connected to WebSocket server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('join_appointments')
def handle_join_appointments(data=None):
    """Join the appointments room to receive real-time updates"""
    room = 'appointments'
    join_room(room)
    print(f'Client joined {room} room')
    emit('joined_room', {'room': room, 'message': 'Successfully joined appointments room'})

@socketio.on('leave_appointments')
def handle_leave_appointments(data=None):
    """Leave the appointments room"""
    room = 'appointments'
    leave_room(room)
    print(f'Client left {room} room')
    emit('left_room', {'room': room, 'message': 'Successfully left appointments room'})

def emit_new_appointment(appointment_data):
    """
    Emit new appointment event to all clients in the appointments room
    This function should be called from the appointment controller
    """
    socketio.emit('new_appointment', {
        'appointment': appointment_data,
        'message': 'New appointment created'
    }, room='appointments')

def emit_appointment_updated(appointment_data):
    """
    Emit appointment update event to all clients in the appointments room
    """
    socketio.emit('appointment_updated', {
        'appointment': appointment_data,
        'message': 'Appointment updated'
    }, room='appointments')

def emit_appointment_deleted(appointment_id):
    """
    Emit appointment deletion event to all clients in the appointments room
    """
    socketio.emit('appointment_deleted', {
        'appointment_id': appointment_id,
        'message': 'Appointment deleted'
    }, room='appointments')
