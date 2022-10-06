from CTFd.models import Challenges, db


class NCPSChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "NCPS"}
    id = db.Column(None, db.ForeignKey("challenges.id"), primary_key=True)
    initial = db.Column(db.Integer)
    minimum = db.Column(db.Integer)
    attack_interval = db.Column(db.Integer)
    attack_point = db.Column(db.Integer)

    def __init__(
        self,
        name,
        description,
        value,
        category,
        type="NCPS",
        minimum=1,
        attack_interval=10,
        attack_point=1,
    ):
        self.name = name
        self.description = description
        self.value = value
        self.initial = value
        self.category = category
        self.type = type
        self.minimum = minimum
        self.attack_interval = attack_interval
        self.attack_point = attack_point
