from flask import (
    current_app,
    render_template,
    url_for,
    redirect,
    session,
)
from app.routes.auth import bp
from .forms import AccessForm


# @bp.before_request
# def before_request_callback():
#     if "token" not in session:
#         return redirect(url_for("auth.logout"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = AccessForm()
    session['invitation'] = 'my_qr_code'
    if form.submit.data and form.validate():
        session['token'] = True
        return redirect(url_for('main.index'))
    return render_template(
        "pages/auth/index.jinja",
        title='Login',
        form=form
    )


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))