from app import create_app
from app.extension import socketio

app = create_app()

if __name__ == "__main__":
    # Development
    if app.config.get('DEBUG'):
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        # Production with eventlet
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)