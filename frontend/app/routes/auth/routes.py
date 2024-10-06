from flask import (
    current_app,
    render_template,
    url_for,
    redirect,
    session,
    jsonify
)
from app.routes.auth import bp
from app.plugins.traction import TractionController
from app.plugins.db import SQLite
from .forms import IssuerAccessForm, AdminAccessForm


@bp.before_request
def before_request_callback():
    if not session.get('traction_token'):
        session['traction_token'] = TractionController().request_token()


@bp.route("/login", methods=["GET", "POST"])
def login():
    admin_access_form = AdminAccessForm()
    issuer_access_form = IssuerAccessForm()
    
    invitation = TractionController(session['traction_token']).new_presentation_request()
    invitation_id = invitation['pres']['@id']
    # SQLite().new_invitation(invitation_id, invitation)
    
    session['invitation'] = url_for('auth.invitation', invitation_id)
    
    if admin_access_form.submit.data and admin_access_form.validate():
        session['token'] = True
        return redirect(url_for('main.index'))
    if issuer_access_form.submit.data and issuer_access_form.validate():
        pass
    return render_template(
        "pages/auth/index.jinja",
        title='Login',
        form=issuer_access_form,
        admin_access_form=admin_access_form,
        issuer_access_form=issuer_access_form,
    )

@bp.route("/invitation/{invitation_id}", methods=["GET"])
def invitation(invitation_id: str):
    invitation = SQLite().get_invitation(invitation_id)
    return jsonify(invitation)


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))