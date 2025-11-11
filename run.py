import sys
from app import create_app
from app.extension import socketio

# Force stdout to be unbuffered so print statements show immediately
sys.stdout.reconfigure(line_buffering=True)

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Flask application...")
    print(f"Debug mode: {app.config.get('DEBUG')}")
    print(f"Environment: {app.config.get('ENV', 'development')}")
    print("=" * 50)
    
    # Development
    if app.config.get('DEBUG'):
        print("Running in DEBUG mode")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    else:
        print("Running in PRODUCTION mode")
        # Production with eventlet
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)