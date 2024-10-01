from flask import (
    current_app,
    render_template,
    url_for,
    redirect,
    session,
)
from app.routes.auth import bp
from .forms import IssuerAccessForm, AdminAccessForm


# @bp.before_request
# def before_request_callback():
#     if "token" not in session:
#         return redirect(url_for("auth.logout"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    admin_access_form = AdminAccessForm()
    issuer_access_form = IssuerAccessForm()
    session['invitation'] = 'my_qr_code'
    if admin_access_form.submit.data and admin_access_form.validate():
        session['token'] = True
        return redirect(url_for('main.index'))
    if issuer_access_form.submit.data and issuer_access_form.validate():
        pass
    return render_template(
        "pages/auth/index.jinja",
        title='Login',
        admin_access_form=admin_access_form,
        issuer_access_form=issuer_access_form,
    )


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))