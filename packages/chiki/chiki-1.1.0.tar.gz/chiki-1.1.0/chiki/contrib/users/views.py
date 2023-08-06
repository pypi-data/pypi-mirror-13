# coding: utf-8
from chiki.web import error
from chiki.contrib.users.base import user_manager as um
from flask import Blueprint, request, render_template, redirect
from flask import url_for, current_app
from flask.ext.login import current_user, login_user, logout_user, login_required

bp = Blueprint('users', __name__)


@bp.route('/register.html')
def register():
    next = request.args.get('next', url_for('users.login'))
    if current_user.is_authenticated():
        return redirect(next)

    email_form = um.forms.RegisterEmailForm()
    phone_form = um.forms.RegisterPhoneForm()
    return render_template(um.tpls.register,
        next=next, email_form=email_form, phone_form=phone_form)


@bp.route('/register/email.html')
def register_email():
    next = request.args.get('next', url_for('users.login'))
    if current_user.is_authenticated():
        return redirect(next)

    token = request.args.get('token')
    code = um.models.EmailCode.get(token)
    if not code:
        return error('该链接已过期')

    form = um.forms.RegisterEmailAccessForm()
    form.email.data = code.email
    form.authcode.data = code.code
    return render_template(um.tpls.register_email,
        next=next, code=code, form=form)


def login_from_account(next):
    form = um.forms.LoginForm()
    if not um.allow_email or not um.allow_phone:
        form.account.label.text = '帐号'
    return render_template(um.tpls.login, form=form)


@bp.route('/login.html')
def login():
    """ 用户登录 """
    next = request.args.get('next', um.config.login_next)
    if current_user.is_authenticated():
        return redirect(next)

    if hasattr(current_app, 'wxauth'):
        wxauth = current_app.wxauth
        action = request.args.get('action', '')
        if action == 'account':
            return login_from_account(next)
        if action == 'mp':
            return wxauth.auth(wxauth.ACTION_MP, next)
        if action == 'qrcode':
            return wxauth.auth(wxauth.ACTION_QRCODE, next)

        ua = request.headers.get('User-Agent', '').lower()
        if 'micromessenger' in ua:
            return wxauth.auth(wxauth.ACTION_MP, next)

    return login_from_account(next)


@bp.route('/logout.html')
def logout():
    next = request.args.get('next', url_for('users.login'))
    if current_user.is_authenticated():
        logout_user()
    return redirect(next)


@bp.route('/reset_password.html')
def reset_password():
    next = request.args.get('next', url_for('users.login'))
    if current_user.is_authenticated():
        return redirect(next)

    email_form = um.forms.ResetPasswordEmailForm()
    phone_form = um.forms.ResetPasswordPhoneForm()
    return render_template(um.tpls.reset_password,
        next=next, email_form=email_form, phone_form=phone_form)


@bp.route('/reset_password/email.html')
def reset_password_email():
    next = request.args.get('next', url_for('users.login'))
    if current_user.is_authenticated():
        return redirect(next)

    token = request.args.get('token')
    code = um.models.EmailCode.get(token)
    if not code:
        return error('该链接已过期')

    form = um.forms.ResetPasswordEmailAccessForm()
    form.email.data = code.email
    form.authcode.data = code.code
    return render_template(um.tpls.reset_password_email,
        next=next, code=code, form=form)


@bp.route('/bind.html')
@login_required
def bind():
    next = request.args.get('next', url_for('users.login'))
    if current_user.is_user():
        return redirect(next)

    if current_user.user:
        user = um.models.User.objects(id=current_user.user).first()
        if user:
            login_user(user)
        return redirect(next)

    email_form = um.forms.BindEmailForm()
    phone_form = um.forms.BindPhoneForm()
    return render_template(um.tpls.bind,
        next=next, email_form=email_form, phone_form=phone_form)
