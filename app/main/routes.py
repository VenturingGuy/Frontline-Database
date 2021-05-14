from flask import Blueprint, request, render_template, redirect, url_for, flash
from datetime import date, datetime
from app.models import Mech, MechAttack, User
from app.main.forms import MechForm, MechAttackForm
from flask_login import login_user, logout_user, login_required, current_user

# Import app and db from events_app package so that we can run app
from app import app, db

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_mechs = Mech.query.all()
    print(all_mechs)
    return render_template('home.html', all_mechs=all_mechs)

@main.route('/new_mech', methods=['GET', 'POST'])
@login_required
def new_mech():
    form = MechForm()

    if form.validate_on_submit():
        new_mech = Mech(
            name=form.name.data,
            series=form.series.data,
            category=form.category.data
        )
        db.session.add(new_mech)
        db.session.commit()
        flash('New unit was created successfully.')
        return redirect(url_for('main.mech_detail', mech_id=new_mech.id))
    return render_template('new_mech.html', form=form)

@main.route('/new_attack', methods=['GET', 'POST'])
@login_required
def new_attack():
    form = MechAttackForm()
    if form.validate_on_submit():
        new_attack = MechAttack(
            name=form.name.data,
            attack_potency=form.attack_potency.data,
            mech=form.mech.data
        )
        db.session.add(new_attack)
        db.session.commit()
        flash('New attack was created successfully.')
        return redirect(url_for('main.attack_detail', mech_id=new_attack.mech.id, attack_id = new_attack.id))
    return render_template('new_attack.html', form=form)

@main.route('/mech/<mech_id>', methods=['GET', 'POST'])
@login_required
def mech_detail(mech_id):
    mech = Mech.query.get(mech_id)
    form = MechForm(obj=mech)
    if form.validate_on_submit():
        mech.name=form.name.data
        mech.series=form.series.data
        mech.category=form.category.data
        db.session.add(mech)
        db.session.commit()
        flash('Mech\'s info has been successfully updated.')
        return redirect(url_for('main.mech_detail', mech_id = mech_id))

    return render_template('mech_detail.html', mech=mech, form=form)

@main.route('/attack/<mech_id>/<attack_id>', methods=['GET', 'POST'])
@login_required
def attack_detail(mech_id, attack_id):
    mech = Mech.query.get(mech_id)
    attack = MechAttack.query.get(attack_id)
    form = MechAttackForm(obj=attack)
    if form.validate_on_submit():
        attack.name = form.name.data
        attack.attack_potency = form.attack_potency.data
        attack.mech = form.mech.data
        db.session.add(attack)
        db.session.commit()
        flash('Attack has been successfully updated.')
        return redirect(url_for('main.attack_detail', mech_id=mech_id, attack_id = attack_id))
    attack = MechAttack.query.get(attack_id)
    return render_template('attack_detail.html', mech=mech, attack=attack, form=form)

@main.route('/delete_attack/<mech_id>/<attack_id>', methods=['POST'])
@login_required
def delete_attack(attack_id, mech_id):
    attack = MechAttack.query.get(attack_id)
    db.session.delete(attack)
    db.session.commit()
    flash('Attack has been successfully deleted.')
    return redirect(url_for('main.mech_detail', mech_id = mech_id))

