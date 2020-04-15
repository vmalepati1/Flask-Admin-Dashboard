from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel
from flask_uploads import UploadSet, IMAGES, configure_uploads
import flask_login as login

# Create app and database
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

login_manager = login.LoginManager()
login_manager.init_app(app)

# Configure image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# Initialize babel (handles translations)
babel = Babel(app)

@babel.localeselector
def get_locale():
    override = request.args.get('lang')

    if override:
        # Store locale in session
        session['lang'] = override

    return session.get('lang', 'en')

# Import main dashboard module
import dashboard.models, dashboard.views
