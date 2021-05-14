from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length
from app.models import MechCategory, Mech

class MechForm(FlaskForm):
    """Form for adding/updating a Mech."""

    name = StringField('Mech Name', validators=[DataRequired(), Length(min=5, max=80)])
    series = StringField('Series Name', validators=[DataRequired(), Length(min=5, max=100)])
    category = SelectField('Mech Category', choices=MechCategory.choices())
    submit = SubmitField('Submit')

class MechAttackForm(FlaskForm):
    """Form for adding/updating an attack/weapon."""

    name = StringField('Attack Name', validators=[DataRequired(), Length(min=3, max=80)])
    attack_potency = IntegerField('Attack Potency', validators=[DataRequired()])
    mech = QuerySelectField('Mech', query_factory=lambda: Mech.query)
    submit = SubmitField('Submit')