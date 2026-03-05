"""
Factory Flask — create_app().
"""
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # --- Configuration ---
    from config import config
    app.config.from_object(config[config_name])

    # --- Injection de l'emit SocketIO dans io_context ---
    from app.core import io_context
    from flask_socketio import emit as socketio_emit
    io_context.set_emit(socketio_emit)

    # --- Blueprints / routes ---
    from app.interfaces.web.routes import web_bp
    app.register_blueprint(web_bp)

    # --- SocketIO ---
    socketio.init_app(app)
    from app.interfaces.web import events  # noqa: F401 — enregistre les handlers

    return app
