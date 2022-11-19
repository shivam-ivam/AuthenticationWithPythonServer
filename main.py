from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////study/python_bootcamp_2/Day68_authentication_login_page/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# line below is creting loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.

# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # hashing the password
        hashed_password = generate_password_hash(
            request.form["password"],
            method="pbkdf2:sha256",
            salt_length=8)
        if User.query.filter_by(email=request.form["email"]).first() is None:
            with app.app_context():
                new_user = User(
                    email=request.form["email"],
                    password=hashed_password,
                    name=request.form["name"]
                )
                db.session.add(new_user)
                db.session.commit()

                # log in and authenticate user after adding details to database.
                login_user(new_user)

            return redirect(url_for("secrets"))
        else:
            flash("User already exist")
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = User.query.filter_by(email=request.form["email"]).first()
        if data is not None:
            if check_password_hash(data.password, request.form["password"]):
                login_user(data)
                return redirect(url_for('secrets'))
            else:
                flash('You entered wrong password')
                # return render_template("login.html")
        else:
            flash('User does note exist!')
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(directory='static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
