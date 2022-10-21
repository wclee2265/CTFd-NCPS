from CTFd.models import Challenges, db
import datetime

from sqlalchemy.ext.hybrid import hybrid_property


class NCPSChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "NCPS"}
    id = db.Column(
        None, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    attack_interval = db.Column(db.Integer)
    attack_point = db.Column(db.Integer)

    ncps_attack_histories = db.relationship(
        "NCPSAttackHistory", backref="ncps_challenge"
    )

    def __init__(self, *args, **kwargs):
        super(NCPSChallenge, self).__init__(**kwargs)


class NCPSAttackHistory(db.Model):
    __tablename__ = "ncps_attack_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    chal_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"))
    value = db.Column(db.Integer)
    name = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __mapper_args__ = {"polymorphic_identity": "ncps_attack_history"}
    user = db.relationship(
        "Users", foreign_keys="NCPSAttackHistory.user_id", lazy="select"
    )
    team = db.relationship(
        "Teams", foreign_keys="NCPSAttackHistory.team_id", lazy="select"
    )
    challenge = db.relationship(
        "Challenges", foreign_keys="NCPSAttackHistory.chal_id", lazy="select"
    )

    @hybrid_property
    def account_id(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team_id
        elif user_mode == "users":
            return self.user_id

    @hybrid_property
    def account(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team
        elif user_mode == "users":
            return self.user
