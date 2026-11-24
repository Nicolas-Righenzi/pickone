from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Devi fare il login per vedere questa pagina."
    login_manager.login_message_category = "warning"

    # importo i blueprint qui, dopo aver creato db e login_manager
    from .auth import bp as auth_bp
    from .routes import bp as main_bp
    from .admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # crea le tabelle se non esistono (niente migrazioni)
    with app.app_context():
        db.create_all()

    return app
