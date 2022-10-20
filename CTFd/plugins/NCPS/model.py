from CTFd.models import Challenges, db


class NCPSChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "NCPS"}
    id = db.Column(
        None, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    attack_interval = db.Column(db.Integer)
    attack_point = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super(NCPSChallenge, self).__init__(**kwargs)
