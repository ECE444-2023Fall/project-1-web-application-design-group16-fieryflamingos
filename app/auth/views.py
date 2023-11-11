from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import RegularUser, OrganizationUser, User
from .forms import LoginForm, RegistrationRegularForm, RegistrationOrganizationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # check if regular exists by the email
        user = User.get_user_by_username(username=form.username.data)
        if user is not None and user.verify_password(form.password.data):
            user_without_password = User.get_user_by_id(user.id)
            login_user(user_without_password, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        else:
            form.password.errors.append("Invalid username/password.")
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register_regular():
    form = RegistrationRegularForm()
    if form.validate_on_submit():
        try:
            user = RegularUser(first_name=form.first_name.data.strip().capitalize(),
                        last_name=form.last_name.data.strip().capitalize(),
                        email=form.email.data.strip(),
                        username=form.username.data.strip(),
                        password=form.password.data)
            user.save()
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            pass
    return render_template('auth/register.html', form=form)


@auth.route('/register-org', methods=['GET', 'POST'])
def register_org():
    form = RegistrationOrganizationForm()
    if form.validate_on_submit():
        try:
            user = OrganizationUser(name=form.name.data,
                        email=form.email.data.strip(),
                        username=form.username.data.strip(),
                        password=form.password.data)
            user.save()
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            pass
    return render_template('auth/register-org.html', form=form)