from flask import Flask
from flask import request, render_template, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
match_app = Flask(__name__)
login_manager.init_app(match_app)
match_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
match_app.config["SECRET_KEY"] = "KEY"
db = SQLAlchemy()
db.init_app(match_app)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    pwd = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    projects = db.Column(db.String, nullable=True)

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    requirement = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    complete = db.Column(db.Integer, nullable=False)


with match_app.app_context():
    db.create_all()

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@match_app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        pwd_hashed = bcrypt.hashpw(request.form.get("pwd").encode('utf-8'), bcrypt.gensalt())
        user = User(email=email, pwd=pwd_hashed, first_name=None, last_name=None)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@match_app.route('/register-q', methods=['GET', 'POST'])
@login_required
def registerQuestion():
    if request.method == "POST":
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        user = current_user
        user.first_name = first_name
        user.last_name = last_name
        db.session.commit()
        return redirect("/post")
    return render_template("registerQuestion.html")

@match_app.route('/project', methods=['GET'])
@login_required
def project():
    id = request.args.get('id')
    project = Project.query.filter_by(id=id).first()
    creator = User.query.filter_by(id=project.created_by).first()
    return render_template("project.html",
                           name=project.name,
                           requirement=project.requirement,
                           description=project.description,
                           created_by="{} {}".format(creator.first_name, creator.last_name),
                           email=creator.email
                           )

@match_app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == "POST":
        name = request.form.get("name")
        requirement = request.form.get("requirement")
        description = request.form.get("description")
        user = current_user
        created_by = user.id
        complete = 0
        project = Project(name=name, requirement=requirement, description=description,
                          created_by=created_by, complete=complete)
        db.session.add(project)
        db.session.commit()
        if user.projects:
            user.projects += " {}".format(project.id)
        else:
            user.projects = "{}".format(project.id)
        db.session.commit()
        return redirect("/browse")
    return render_template("post.html")

@match_app.route('/complete', methods=['GET'])
@login_required
def complete():
    id = request.args.get('id')
    project = Project.query.filter_by(id=id).first()
    user = current_user
    if project.created_by == user.id:
        project.complete = 1
        db.session.commit()
    return redirect("/profile")

@match_app.route('/profile', methods=['GET'])
@login_required
def profile():
    user = current_user
    num_projects = 0
    ids = []
    names = []
    descriptions = []
    creators = []
    completes = []
    if current_user.projects:
        project_ids = [int(id) for id in current_user.projects.split()]
        for id in project_ids:
            project = Project.query.filter_by(id=id).first()
            num_projects += 1
            ids.append(project.id)
            names.append(project.name)
            descriptions.append("{}...".format(project.description[:(min(300, len(project.description)))]))
            completes.append(project.complete)
    return render_template("profile.html",
                           first_name=user.first_name,
                           last_name=user.last_name,
                           email=user.email,
                           num_projects=num_projects,
                           ids=ids,
                           names=names,
                           descriptions=descriptions,
                           completes=completes)

@match_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email")).first()
        if user and bcrypt.checkpw(request.form.get("pwd").encode('utf-8'), user.pwd):
            login_user(user)
            if user.first_name and user.last_name:
                return redirect("/browse")
            else:
                return redirect("/register-q")
        else:
            return "login failed"
    return render_template("login.html")

@match_app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

@match_app.route('/', methods=['GET'])
def index():
    return redirect("/browse")

@match_app.route('/browse', methods=['GET'])
@login_required
def browse():
    projects = Project.query.all()
    num_projects = 0
    ids = []
    names = []
    descriptions = []
    creators = []
    completes = []
    for project in projects:
        if project.complete != 1:
            num_projects += 1
            ids.append(project.id)
            names.append(project.name)
            descriptions.append("{}...".format(project.description[:(min(300, len(project.description)))]))
            creator = User.query.filter_by(id=project.created_by).first()
            creators.append("{} {}".format(creator.first_name, creator.last_name))

    return render_template("home.html",
                           num_projects=num_projects,
                           ids=ids,
                           names=names,
                           descriptions=descriptions,
                           creators=creators)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

if __name__ == '__main__':
    match_app.run(debug=True)
