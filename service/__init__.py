"""
Accounts Service

Flask application factory with Talisman security headers and CORS policies.
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

db = SQLAlchemy()
talisman = Talisman()


def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI", "sqlite:///accounts.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    if test_config:
        app.config.update(test_config)

    # Security headers (X-Frame-Options, X-Content-Type-Options,
    # Content-Security-Policy, Referrer-Policy)
    talisman.init_app(
        app, force_https=os.getenv("FORCE_HTTPS", "true").lower() == "true"
    )

    # CORS policies
    CORS(app)

    db.init_app(app)

    with app.app_context():
        from service import routes  # pylint: disable=import-outside-toplevel
        app.register_blueprint(routes.api)
        db.create_all()

    return app
