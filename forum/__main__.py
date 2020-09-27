from flask import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder = './templates', static_folder = './static')
app.config['SECRET_KEY'] = 'PUT A SECRET KEY HERE!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy(app)

if __name__ == "__main__":
    from forum.routes import *
    app.run(debug=True)

