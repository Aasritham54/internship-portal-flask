from flask import Flask, render_template, redirect, url_for, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Internship, Application

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------- ROUTES --------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# -------------------- INTERNSHIP FEATURES --------------------

@app.route("/add-internship", methods=["GET", "POST"])
@login_required
def add_internship():
    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        description = request.form["description"]

        internship = Internship(
            title=title,
            company=company,
            description=description
        )
        db.session.add(internship)
        db.session.commit()

        return redirect(url_for("view_internships"))

    return render_template("add_internship.html")


@app.route("/internships")
@login_required
def view_internships():
    internships = Internship.query.all()
    return render_template("internships.html", internships=internships)


@app.route("/apply/<int:internship_id>")
@login_required
def apply(internship_id):
    application = Application(
        user_id=current_user.id,
        internship_id=internship_id
    )
    db.session.add(application)
    db.session.commit()

    return redirect(url_for("view_internships"))


# -------------------- MAIN --------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
