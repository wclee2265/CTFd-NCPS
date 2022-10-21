from flask import request, render_template, Blueprint, abort

from .model import NCPSAttackHistory

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
    def get_dashboard():
        return render_template("NCPS_dashboard.html")

    @ncps_bp.route("/attack_history", methods=["GET"])
    def get_attack_history():
        query = NCPSAttackHistory.query
        attack_history = query.all()

        return render_template(
            "NCPS_attackhistory.html",
            attack_histories=attack_history,
        )

    return ncps_bp
