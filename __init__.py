import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    '''
    Function to create the app using Flask
    '''
    app = Flask(__name__)
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(CONFIG_TYPE)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes
        if CONFIG_TYPE != 'config.ProductionConfig':
            db.drop_all()
            print("Dropped All Tables")
            db.create_all()

        print("Created All Tables From Models")
        return app
