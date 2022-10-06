from flask import request, render_template, Blueprint, abort

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

    return ncps_bp
