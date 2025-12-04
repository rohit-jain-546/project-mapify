from flask import Flask, render_template, url_for, redirect, request , session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import input_required, length, ValidationError,Email
from flask_bcrypt import Bcrypt

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/map"
app.config['SECRET_KEY'] = 'ROHIT'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))


class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phno = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class RegisterForm(FlaskForm):
    name = StringField(validators=[input_required(), length(min=4, max=50)], render_kw={'placeholder': 'full name'})
    email = StringField(validators=[input_required(), Email()], render_kw={'placeholder': 'email'})
    phno = StringField(validators=[input_required(), length(min=4, max=20)], render_kw={'placeholder': 'phone number'})
    unm = StringField(validators=[input_required(), length(min=4, max=20)], render_kw={'placeholder': 'user name'})
    passwd = PasswordField(validators=[input_required(), length(min=4, max=20)], render_kw={'placeholder': 'password'})
    submit = SubmitField('register')

    def validate_unm(self, unm):
        exist_unm = user.query.filter_by(username=unm.data).first()
        if exist_unm:
            raise ValidationError("user name not available")


class LoginForm(FlaskForm):
    unm = StringField(validators=[input_required(), length(min=4, max=20)], render_kw={'placeholder': 'user name'})
    passwd = PasswordField(validators=[input_required(), length(min=4, max=20)], render_kw={'placeholder': 'password'})
    submit = SubmitField('Login')


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html',name=session['name'])


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = user.query.filter_by(username=form.unm.data).first()
        if u and bcrypt.check_password_hash(u.password, form.passwd.data):
            session['name'] = u.name
            login_user(u)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        has_pass = bcrypt.generate_password_hash(form.passwd.data)
        new_user = user(name=form.name.data,email=form.email.data,phno=form.phno.data,username=form.unm.data, password=has_pass)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route("/map", methods=["GET", "POST"])
@login_required
def map_page():
    lat = None
    lon = None

    if request.method == "POST":
        lat = request.form.get("lat")
        lon = request.form.get("lon")

    return render_template("map.html", lat=lat, lon=lon)



app.run(debug=True)

