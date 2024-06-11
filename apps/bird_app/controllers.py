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

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_sightings_url = URL('get_sightings'),
        get_species_url = URL('get_species'),
    )

@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=4)

@action('location')
@action.uses('location.html', db, auth, url_signer)
def location():
    ne_lat = request.params.get('ne_lat')  # get values from url
    ne_lng = request.params.get('ne_lng')  # 
    sw_lat = request.params.get('sw_lat')  # 
    sw_lng = request.params.get('sw_lng')  # 
    
    return dict(
        # COMPLETE: return here any signed URLs you need.
        load_sightings_url = URL('load_sightings'),
        load_species_url = URL('load_species'),
        load_info_url = URL('load_info'),
        my_callback_url = URL('my_callback', signer=url_signer),
        load_names_url = URL('load_names'),
        ne_lat = ne_lat,
        ne_lng = ne_lng,
        sw_lat = sw_lat,
        sw_lng = sw_lng,
    )

@action('load_names', method="POST")
@action.uses(db, session, auth)
def load_names():
    # The return value should be a dictionary that will be sent as JSON.
    bird_name = request.json.get("bird_name")
    #latitude = request.json.get('latitude')
    ne_lat = request.json.get('ne_lat')
    ne_lng = request.json.get('ne_lng')
    sw_lat = request.json.get('sw_lat')
    sw_lng = request.json.get('sw_lng')

    # Calculate the bounding box for the region
    lat_min = float(sw_lat)
    lat_max = float(ne_lat)
    long_min = float(sw_lng)
    long_max = float(ne_lng)

    # Query for the checklists within the specified region
    checklists = db((db.checklist.latitude >= lat_min) &
                    (db.checklist.latitude <= lat_max) &
                    (db.checklist.longitude >= long_min) &
                    (db.checklist.longitude <= long_max)).select().as_list()

    sampling_ids = [checklist['sampling_id'] for checklist in checklists]

    # Query for the sightings of the specific bird name within the sampling IDs
    sightings = db((db.sightings.sighting_id.belongs(sampling_ids)) &
                   (db.sightings.name == bird_name)).select().as_list()
    # Aggregate the count of sightings over time
    from collections import defaultdict
    from datetime import datetime
    
    counts_by_date = defaultdict(int)
    for sighting in sightings:
        sampling_id = sighting['sighting_id']
        observation_date = db(db.checklist.sampling_id == sampling_id).select(db.checklist.date).first()
        date_str = observation_date.date.strftime("%Y-%m-%d")
        counts_by_date[date_str] += sighting['observation_count']

    # Sort dates and prepare data for the chart
    sorted_dates = sorted(counts_by_date.keys())
    counts = [counts_by_date[date] for date in sorted_dates]
    
    return dict(labels=sorted_dates, values=counts)



@action('load_info')
@action.uses(db, session, auth) # Add here things like db, auth, etc.
def load_info():
    ne_lat = request.params.get('ne_lat')
    ne_lng = request.params.get('ne_lng')
    sw_lat = request.params.get('sw_lat')
    sw_lng = request.params.get('sw_lng')

    # Calculate the bounding box for the region
    lat_min = float(sw_lat)
    lat_max = float(ne_lat)
    long_min = float(sw_lng)
    long_max = float(ne_lng)

    # Query for the checklists within the specified region
    checklists = db((db.checklist.latitude >= lat_min) &
                    (db.checklist.latitude <= lat_max) &
                    (db.checklist.longitude >= long_min) &
                    (db.checklist.longitude <= long_max)).select().as_list()
    
    # Extract sampling IDs from checklists
    sampling_ids = [checklist['sampling_id'] for checklist in checklists]

    # Find sightings corresponding to the sampling IDs
    sightings = db(db.sightings.sighting_id.belongs(sampling_ids)).select().as_list()

    # Count sightings for each species
    species_count = {}
    for sighting in sightings:
        species = sighting['name']
        if species in species_count:
            species_count[species] += 1
        else:
            species_count[species] = 1

    # Filter species with more than 1 sighting
    species_with_multiple_sightings = [species for species, count in species_count.items() if count > 1]

    # Get species details from the species table
    unique_species = db(db.species.type.belongs(species_with_multiple_sightings)).select().as_list()

    # Calculate the total number of sightings in the region
    total_sightings = sum(sighting['observation_count'] for sighting in sightings)

    # Calculate the top three users with the most sightings
    user_sighting_counts = {}
    for checklist in checklists:
        user_email = checklist['email']
        if user_email in user_sighting_counts:
            user_sighting_counts[user_email] += 1
        else:
            user_sighting_counts[user_email] = 1

    # Sort users by their sighting counts and get the top three
    top_users = sorted(user_sighting_counts.items(), key=lambda item: item[1], reverse=True)[:3]
    

    return dict(
        checklists=checklists,
        species=unique_species,
        total_sightings=total_sightings,
        top_users=top_users
    )

#controllers for index:
@action('get_sightings', method=["GET"])
@action.uses(db)
def get_sightings():
    query = (db.sightings.sighting_id == db.checklist.sampling_id)
    sightings_list = db(query).select(
        db.sightings.ALL, 
        db.checklist.latitude, 
        db.checklist.longitude
    ).as_list()
    return dict(sightings=sightings_list)

@action('get_species', method=["GET"])
@action.uses(db)
def get_species():
    species_list = db(db.species).select().as_list()
    return dict(species=species_list)