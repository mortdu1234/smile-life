from flask import Flask, redirect, request, url_for, jsonify
from flask_socketio import SocketIO
from backend.webSocket import init_socketio
import logging
from backend import cleanup

socketio = SocketIO()


def create_app(secret_key: str = 'change-me-in-production') -> Flask:
    app = Flask(__name__)
    app.secret_key = secret_key

    # ── lancement du cleaner de salles ────────────────────────────────
    cleanup.start_cleanup_worker()

    # ── SocketIO — init avant les blueprints ────────────────────────────────
    socketio.init_app(app, async_mode='gevent', cors_allowed_origins='*')
    init_socketio(socketio)

    # ── Blueprints ──────────────────────────────────────────────────────────
    from routes.hub import hub_bp
    from routes.game import game_bp, register_socket_events

    # Enregistre les handlers WS maintenant que socketio est prêt
    register_socket_events(socketio)

    app.register_blueprint(game_bp)
    app.register_blueprint(hub_bp)

    # ── Routes ──────────────────────────────────────────────────────────────
    @app.route('/')
    def root():
        return redirect(url_for('hub.index'))

    return app


if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)