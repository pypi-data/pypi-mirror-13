import flask
from flask import current_app
from rfhub.authentication import requires_auth

blueprint = flask.Blueprint('dashboard', __name__,
                            template_folder="templates")

@blueprint.route("/")
@requires_auth
def home():
    
    return flask.render_template("dashboard.html")
