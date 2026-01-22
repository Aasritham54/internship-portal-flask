from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Internship, Application

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ✅ CREATE DATABASE (FLASK 3 SAFE)
with app.app_context():
    db.create_all()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('home.html')

# ---------------- AUTH ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ---------------- INTERNSHIPS ----------------
@app.route('/internships')
@login_required
def internships():
    data = Internship.query.all()
    return render_template('internships.html', internships=data)

@app.route('/add-internship', methods=['GET', 'POST'])
@login_required
def add_internship():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        internship = Internship(
            title=request.form['title'],
            company=request.form['company'],
            description=request.form['description']
        )
        db.session.add(internship)
        db.session.commit()
        flash('Internship added successfully', 'success')
        return redirect(url_for('internships'))

    return render_template('add_internship.html')

# ---------------- APPLY ----------------
@app.route('/apply/<int:id>')
@login_required
def apply(id):
    if current_user.role != 'student':
        flash('Only students can apply', 'error')
        return redirect(url_for('internships'))

    existing = Application.query.filter_by(
        user_id=current_user.id,
        internship_id=id
    ).first()

    if existing:
        flash('You already applied for this internship', 'error')
        return redirect(url_for('internships'))

    application = Application(
        user_id=current_user.id,
        internship_id=id
    )
    db.session.add(application)
    db.session.commit()
    flash('Applied successfully', 'success')
    return redirect(url_for('internships'))

@app.route('/my-applications')
@login_required
def my_applications():
    apps = Application.query.filter_by(user_id=current_user.id).all()
    internships = [Internship.query.get(app.internship_id) for app in apps]
    return render_template('my_applications.html', internships=internships)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
