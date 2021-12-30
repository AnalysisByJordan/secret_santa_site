import os
import secrets
import random
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from secret_santa_flask.models import User
from secret_santa_flask.forms import RegistrationForm, LoginForm, UpdateAccountForm
from secret_santa_flask import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    users = User.query.all()
    user_data = {}
    for user in users:
        user_data[user.username] = [url_for('static', filename='profile_pics/' + user.image_file), user.likes]
    home_pic1 = url_for('static', filename='meme_pics/everybody_bigman.jpg')
    home_pic2 = url_for('static', filename='meme_pics/everybody_tubes.jpg')
    home_pic3 = url_for('static', filename='meme_pics/eddy_chief.jpg')
    return render_template('home.html', user_data=user_data, home_pic1=home_pic1, home_pic2=home_pic2, home_pic3=home_pic3)


@app.route("/about")
def about():
    virus_pic = url_for('static', filename='meme_pics/eddy_bigdick.jpg')
    return render_template('about.html', title='Virus Page', virus_pic=virus_pic)

@app.route("/forget")
def forget():
    return render_template('forget.html', title='Forget')

@app.route("/info")
def info():
    return render_template('info.html', title='Info')

@app.route("/register", methods=['GET', 'POST'])
def register():
    reg_pic1 = url_for('static', filename='meme_pics/jordan_ry.jpg')
    reg_pic2 = url_for('static', filename='meme_pics/kevin_cocaine.jpg')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(message='Your account has been created! You can log in now', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, reg_pic1=reg_pic1, reg_pic2=reg_pic2)

@app.route("/login", methods=['GET', 'POST'])
def login():
    login_pic1 = url_for('static', filename='meme_pics/girls_hotguys.jpg')
    login_pic2 = url_for('static', filename='meme_pics/jordan_unitard.jpg')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Check your username and password', category='danger')
    return render_template('login.html', title='Login', form=form, login_pic1=login_pic1, login_pic2=login_pic2)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (225, 225)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def get_giftee_likes(user):
    giftee = User.query.filter_by(username = user.giftee).first()
    if giftee:
        return giftee.likes
    else:
        return 'Not Available'


def create_random_giftee():
    all = User.query.all()
    users = [user.username for user in all]
    giftee_dict = {}
    pickable = users.copy()
    for user in users:
        choice = random.choice([x for x in pickable if x != user])
        giftee_dict[user] = choice
        pickable.remove(choice)
    return giftee_dict

def assign_giftee():
    for k, v in create_random_giftee().items():
        User.query.filter_by(username=k).first().giftee = v
        db.session.commit()
    return 

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Randomize Assignees':
            assign_giftee()
    return render_template('admin.html')

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    giftee_likes = get_giftee_likes(current_user)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.likes = form.likes.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.likes.data = current_user.likes
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, giftee_likes=giftee_likes)
