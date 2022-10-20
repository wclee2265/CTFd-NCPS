from apscheduler.schedulers.background import BackgroundScheduler
from CTFd import utils
from CTFd.utils.modes import get_model
from CTFd.models import db, Awards, Challenges, Teams
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins import register_plugin_assets_directory
from flask import Blueprint
from flask_apscheduler import APScheduler

from logging import basicConfig, getLogger, DEBUG, ERROR

from .model import NCPSChallenge
from .blueprint import load_bp
from pickle import dump, load as pickle
from os import getcwd, path

basicConfig(level=ERROR)
logger = getLogger(__name__)

NCPS_timers = dict()
NCPS_timers_pickle = path.join(path.dirname(__file__), ".NCPS_timers.pkl")


def _team_name(session_id):
    """
    :param session_id:
    :return: the team name for the given team id
    """
    try:
        return Teams.query.filter_by(id=session_id).first().name
    except Exception:
        return None


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


def init_NCPS_worker():
    """
    Load the cached timer data if it exists
    """
    global NCPS_timers
    if path.exists(NCPS_timers_pickle):
        with open(NCPS_timers_pickle, "rb+") as FILE:
            try:
                NCPS_timers = pickle(FILE)
            except EOFError:
                pass


def NCPS_worker():
    """
    Iterate over each of the hash-cracking challenges and give hold points to each king when the hold counter is zero
    """
    global NCPS_timers
    # TODO have a settings page where this can be manually paused and restarted in case it misbehaves
    # TODO On the settings page also show the status of this thread (I.E. Running/stopped) and who is king of every hill
    with db.app.app_context():
        if not utils.ctf_paused() and not utils.ctf_ended():
            chals = Challenges.query.filter_by(type="NCPS").all()
            for c in chals:
                assert isinstance(c, NCPSChallenge)

                chal_name = c.name
                chal_id = c.id
                attack_interval = c.attack_interval

                teams = c.teams
                for t in teams:
                    team_name = t.name
                    if NCPS_timers.get(chal_id, None) is None:
                        logger.debug("Initializing '{}' timer".format(chal_name))
                        NCPS_timers[chal_id] = 0
                    else:
                        if NCPS_timers[chal_id] < attack_interval:
                            logger.debug("Incrementing '{}' timer'".format(chal_name))
                            NCPS_timers[chal_id] += 1
                        if NCPS_timers[chal_id] == attack_interval:
                            # Reset Timer
                            logger.debug("Resetting '{}' timer".format(chal_name))
                            NCPS_timers[chal_id] = 0

                            # TODO: test attack, availabliity

                            # Timer has maxed out, give points to the king
                            solve = Awards(teamid=team_name, name=chal_id, value=10)
                            solve.description = "Team '{}' is king of '{}'".format(
                                _team_name(team_name), chal_name
                            )
                            db.session.add(solve)

                            db.session.commit()
                            # db.session.expunge_all()
                    logger.debug(
                        "'{}' timer is at '{}'".format(
                            chal_name, NCPS_timers.get(chal_id, 0)
                        )
                    )
        else:
            logger.debug("Game is paused")
    # Save the current state of the timers in a pickle file
    with open(NCPS_timers_pickle, "wb+") as PICKLE:
        dump(NCPS_timers, PICKLE, protocol=2)


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/NCPS/assets/")
    CHALLENGE_CLASSES["NCPS"] = NCPS

    init_NCPS_worker()
    db.app = app
    if hasattr(app, "NCPS_scheduler"):
        pass  # TODO use the existing scheduler or give a more unique name to this scheduler?
    # The timezone is necessary for the BackgroundScheduler to be initialized correctly but further than that doesn't matter
    NCPS_scheduler = BackgroundScheduler(timezone="MST")
    NCPS_scheduler.add_job(
        NCPS_worker,
        max_instances=1,
        id="NCPS_worker",
        trigger="interval",
        seconds=60,
    )
    app.NCPS_scheduler = APScheduler(app=app, scheduler=NCPS_scheduler)
    app.NCPS_scheduler.start()

    ncps_bp = load_bp()
    app.register_blueprint(ncps_bp)
    print("NCPS plugin is ready!")
