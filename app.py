from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "chamber"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def register():
    '''Handle no URL input'''
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def show_registration():
    '''Form for new users to sign up'''
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already taken.')
            return render_template('register.html', form=form)
        session['user'] = new_user.username
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)

@app.route('/users/<username>')
def expose_secrets(username):
    '''Protected route for logged in users only to view user info'''
    if 'user' not in session:
        return redirect('/login')
    user = User.query.get_or_404(username)
    
    #get a list of all of the user's feedback
    all_feedback = user.feedback
    return render_template('user_details.html', user=user, all_feedback=all_feedback)

@app.route('/login', methods=["GET", "POST"])
def show_login():
    '''Render login form, handle invalid logins'''
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['user'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user')
    return redirect('/login')