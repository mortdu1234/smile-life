from flask import Flask, redirect, request, url_for, jsonify
from flask_socketio import SocketIO
from backend.webSocket import init_socketio
import logging
from backend import cleanup
from werkzeug.middleware.proxy_fix import ProxyFix

socketio = SocketIO()

def create_app(secret_key: str = 'change-me-in-production') -> Flask:
    app = Flask(__name__)
    app.secret_key = secret_key
    app.config['APPLICATION_ROOT'] = '/game-smile-life'  # ← avant tout

    # Corrige les redirects derrière nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)

    cleanup.start_cleanup_worker()
    socketio.init_app(app, async_mode='gevent', cors_allowed_origins='*')
    init_socketio(socketio)

    from routes.hub import hub_bp
    from routes.game import game_bp, register_socket_events
    register_socket_events(socketio)
    app.register_blueprint(game_bp)
    app.register_blueprint(hub_bp)

    @app.route('/')
    def root():
        return redirect(url_for('hub.index'))

    return app

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)