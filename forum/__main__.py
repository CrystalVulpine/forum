from flask import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder = './templates', static_folder = './static')
app.config['SECRET_KEY'] = 'PUT A SECRET KEY HERE!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/forum/test.db'
app.config['UPLOAD_FOLDER'] = '/tmp/forum/uploads'
app.config['MAX_CONTENT_PATH'] = 5242880

db = SQLAlchemy(app)

if __name__ == "__main__":
    from forum.routes import *
    app.run(debug=True)

