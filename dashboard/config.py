import os

# set optional bootswatch theme
# see http://bootswatch.com/3/ for available swatches
FLASK_ADMIN_SWATCH = 'cerulean'

# Secret key for sessions
SECRET_KEY = '123456790'

# URI to the database
SQLALCHEMY_DATABASE_URI = 'mysql://root:HeavenBlessesHardwork@localhost/api_db'

# No event system tracking
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Directory of dashboard project
TOP_LEVEL_DIR = os.path.abspath(os.curdir)

# File Uploads
UPLOADS_DEFAULT_DEST = TOP_LEVEL_DIR + '/dashboard/static/img'
UPLOADS_DEFAULT_URL = 'http://127.0.0.1:5000/static/img/'
 
UPLOADED_IMAGES_DEST = TOP_LEVEL_DIR + '/dashboard/static/img'
UPLOADED_IMAGES_URL = 'http://127.0.0.1:5000/static/img/'
