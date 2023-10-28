from flask import Flask
from flask import request, render_template, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import bcrypt
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
match_app = Flask(__name__)
login_manager.init_app(match_app)
match_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
match_app.config["SECRET_KEY"] = "KEY"
user_db = SQLAlchemy()
user_db.init_app(match_app)

class User(UserMixin, user_db.Model):
    __tablename__ = 'user'

    id = user_db.Column(user_db.Integer, primary_key=True)
    email = user_db.Column(user_db.String, unique=True, nullable=False)
    pwd = user_db.Column(user_db.String, nullable=False)


with match_app.app_context():
    user_db.create_all()

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@match_app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        pwd_hashed = bcrypt.hashpw(request.form.get("pwd").encode('utf-8'), bcrypt.gensalt())
        user = User(email=email, pwd=pwd_hashed)
        user_db.session.add(user)
        user_db.session.commit()
        return "register success"
    return "register page"


@match_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email")).first()
        if user and bcrypt.checkpw(request.form.get("pwd").encode('utf-8'), user.pwd):
            login_user(user)
            return "login success"
        else:
            return "login failed"
    return "login page"

@match_app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return "logout success"

@match_app.route('/', methods=['GET'])
def index():
    return "Team Matcher"

@match_app.route('/browse', methods=['GET'])
@login_required
def browse():
    return "browse projects"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


if __name__ == '__main__':
    match_app.run()
