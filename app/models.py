from sqlalchemy_utils import URLType
from app import db
from app.utils import FormEnum

from flask_login import UserMixin

class MechCategory(FormEnum):
    """Categories of mechs."""
    SUPER = 'Super'
    REAL = 'Real'

class Mech(db.Model):
    """Mecha model."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    series = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Enum(MechCategory), default=MechCategory.SUPER)
    attacks = db.relationship('MechAttack', back_populates='mech')

    def __str__(self):
        return f"<Mech: {self.name}>"

    def __repr__(self):
        return f"<Mech: {self.name}>"

class MechAttack(db.Model):
    """Weapon/Attack model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    attack_potency = db.Column(db.Integer, nullable=False)
    mech = db.relationship('Mech', back_populates='attacks')
    mech_id = db.Column(db.Integer, db.ForeignKey('mech.id'), nullable=False)

    def __str__(self):
        return f"<Attack: {self.name}>"

    def __repr__(self):
        return f"<Attack: {self.name}>"
        
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"<User: {self.username}>"

mech_attack_table = db.Table(
    "mech_attack_table",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("mech_id", db.Integer, db.ForeignKey("mech.id")),
)