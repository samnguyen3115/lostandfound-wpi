
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app import db
from app.auth import auth_blueprint as bp_auth 
from app.auth.auth_forms import RegistrationForm, LoginForm
import sqlalchemy as sqla
from app.main.models import User


@bp_auth.route('/user/register', methods=['GET', 'POST'])
def register():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        user = User(
            firstname = rform.first_name.data,
            lastname = rform.last_name.data,
            email = rform.email.data,
            wpi_id = rform.wpi_id.data,
            phonenum = rform.phonenum.data,)
        user.set_password(rform.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulation, you are now registered")
        return redirect(url_for('main.index'))

    return render_template('register.html',form = rform)

@bp_auth.route('/user/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    lform = LoginForm()
    if lform.validate_on_submit():
        query = sqla.select(User).where(User.email == lform.email.data)
        user = db.session.scalars(query).first()
        if user is None or not user.check_password(lform.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=lform.remember_me.data)     
        return redirect(url_for('main.index'))

    return render_template('login.html', form=lform)

@bp_auth.route('/user/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))