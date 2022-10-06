from flask import Blueprint
from CTFd.utils.modes import get_model
from CTFd.models import Awards
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins import register_plugin_assets_directory

from .model import NCPSChallenge
from .blueprint import load_bp


class NCPS(BaseChallenge):
    id = "NCPS"  # Unique identifier used to register challenges
    name = "NCPS"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": "/plugins/NCPS/assets/create.html",
            "update": "/plugins/NCPS/assets/update.html",
            "view": "/plugins/NCPS/assets/view.html",
        }
    )
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/NCPS/assets/create.js",
        "update": "/plugins/NCPS/assets/update.js",
        "view": "/plugins/NCPS/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/NCPS/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "NCPS",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = NCPSChallenge

    @classmethod
    def update_awards(
        cls, challenge
    ):  # update awards that received from the NCPS challenge
        Model = get_model()
        awards = Awards.query.filter_by(challenge_id=challenge.id).all()
        # TODO: update awards value from the NCPS challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = NCPSChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "attack_point", "attack_interval"):
                value = float(value)
            setattr(challenge, attr, value)

        NCPS.update_awards(challenge)
        return challenge

    @staticmethod
    def attempt(challenge, request):
        return False, "NCPS attempt method is not used"

    @staticmethod
    def solve(user, team, challenge, request):
        """NCPS solve method is not used"""

    @staticmethod
    def fail(user, team, challenge, request):
        """NCPS fail method is not used"""


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/NCPS/assets/")
    CHALLENGE_CLASSES["NCPS"] = NCPS

    ncps_bp = load_bp()
    app.register_blueprint(ncps_bp)
    print("NCPS plugin is ready!")
