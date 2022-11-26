from flask import request, render_template, Blueprint, abort, url_for
from CTFd.models import Challenges
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.modes import get_model
from CTFd.utils.decorators import admins_only


from .model import NCPSChallenge, NCPSAttackHistory

ncps_bp = Blueprint(
    "NCPS",
    __name__,
    template_folder="templates",
    static_folder="assets",
    url_prefix="/NCPS",
)


def load_bp():
    # Handle GET requests: serve the config page with pre-filled values
    @ncps_bp.route("/dashboard", methods=["GET"])
    @admins_only
    def get_dashboard():
        ncps_challenges = NCPSChallenge.query.all()
        print(ncps_challenges)
        for chal in ncps_challenges:
            print(chal.name)

        return render_template(
            "NCPS_dashboard.html",
            ncps_challenges=ncps_challenges,
        )

    @ncps_bp.route("/attack_history", methods=["GET"])
    @admins_only
    def get_attack_history():

        q = request.args.get("q")
        field = request.args.get("field")
        page = abs(request.args.get("page", 1, type=int))

        filters = build_model_filters(
            model=NCPSAttackHistory,
            query=q,
            field=field,
            extra_columns={
                "challenge_name": Challenges.name,
                "account_id": NCPSAttackHistory.account_id,
            },
        )

        Model = get_model()

        attack_histories = (
            NCPSAttackHistory.query.filter(*filters)
            .join(Challenges)
            .join(Model)
            .order_by(NCPSAttackHistory.date.desc())
            .paginate(page=page, per_page=50)
        )

        args = dict(request.args)
        args.pop("page", 1)

        return render_template(
            "NCPS_attackhistory.html",
            attack_histories=attack_histories,
            prev_page=url_for(request.endpoint, page=attack_histories.prev_num, **args),
            next_page=url_for(request.endpoint, page=attack_histories.next_num, **args),
        )

    return ncps_bp
