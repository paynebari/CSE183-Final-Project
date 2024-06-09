"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('checklist')
@action.uses('checklist.html', db, auth.user)
def checklist():
    sampling_id = request.params.get('sampling_id')
    print(f"Received sampling_id: {sampling_id}")
    return dict(
        sampling_id=sampling_id,
        load_sightings_url = URL('load_sightings'),
        inc_sightings_url = URL('inc_sightings'),
        add_sightings_url = URL('add_sightings'),
        del_sightings_url = URL('del_sightings')
    )

@action('view_checklists')
@action.uses('view_checklists.html', db, auth.user)
def view_checklists():
    return dict(
        load_checklists_url = URL('load_checklists'),
        del_checklists_url = URL('del_checklists'),
    )

@action('load_checklists')
@action.uses(db, auth.user)
def load_checklists():
    #user_email = get_user_email()
    checklists = db(db.checklist.email == get_user_email).select().as_list()
    return dict(checklists=checklists)

@action('load_sightings')
@action.uses(db, session, auth.user)
def load_sightings():
    #sightings_list = db(db.sightings.user_email == get_user_email()).select().as_list()
    #(db.checklist.email == get_user_email) &
    sampling_id = request.params.get('sampling_id')
    sightings_list = db( 
        (db.checklist.sampling_id == sampling_id) &
        (db.checklist.sampling_id == db.sightings.sighting_id)
    ).select(db.sightings.id, db.sightings.name, db.sightings.observation_count).as_list()
    #print("sightingslist",sightings_list)
    return dict(sightings=sightings_list)

@action('add_sightings', method='POST')
@action.uses(db, session, auth.user)
def add_sightings():
    name = request.json.get('name')
    observation_count = request.json.get('observation_count')
    sighting_id = request.json.get('sighting_id')
    #sighting_id = db.checklist.sampling_id
    id = db.sightings.insert(sighting_id=sighting_id, name=name, observation_count=observation_count)
    return dict(id=id)

@action('inc_sightings', method='POST')
@action.uses(db, session, auth.user)
def inc_sightings():
    id = request.json.get('id')
    bird = db(db.sightings.id == id).select().first()
    #assert bird.user_email == get_user_email() # Only the owner of the observation can inc it. 
    bird.observation_count += 1
    bird.update_record()
    return dict(bird_count=bird.observation_count)

@action('del_sightings', method='POST')
@action.uses(db, auth.user)
def del_sightings():
    # Complete.
    id = request.json.get('id')
    bird = db(db.sightings.id == id).select().first()
    #assert bird.user_email == get_user_email() # Only the owner of the observation can inc it. 
    db(db.sightings.id == id).delete()
    return dict(success=True)

@action('del_checklists', method='POST')
@action.uses(db, auth.user)
def del_checklists():
    # Complete.
    id = request.json.get('id')
    check = db(db.checklist.id == id).select().first()
    assert check.email == get_user_email() # Only the owner of the observation can inc it. 
    db(db.checklist.id == id).delete()
    return dict(success=True)
# You can add other controllers here.

