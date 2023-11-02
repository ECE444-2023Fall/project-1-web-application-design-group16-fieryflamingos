from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import RegularUser
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = RegularUser.objects(email=form.email.data).get()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)
            flash('Invalid username or password.')
        except:
            flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = RegularUser(first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        email=form.email.data,
                        password=form.password.data)
            user.save()
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        except:
            pass
    return render_template('auth/register.html', form=form)