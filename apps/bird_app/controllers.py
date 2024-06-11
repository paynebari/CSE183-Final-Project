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
import uuid
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_sightings_url = URL('get_sightings'),
        get_species_url = URL('get_species'),
        create_checklist_url = URL('create_checklist')
    )
#checklist stuff
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

# end of checklist stuff

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

@action('create_checklist', method=["POST"])
@action.uses(db, auth.user)
def create_checklist():
    print("Create checklist endpoint called")
    data = request.json
    sampling_id = data.get('sampling_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    date = data.get('date')
    time = data.get('time')
    duration = data.get('duration')
    user_email = get_user_email()

    if not all([sampling_id, latitude, longitude, date, time, duration, user_email]):
        abort(400, "Missing required fields")

    print(f"Creating checklist with data: {data}")
    print(f"User email: {user_email}")

    db.checklist.insert(
        sampling_id=sampling_id,
        latitude=latitude,
        longitude=longitude,
        date=date,
        time=time,
        email=user_email,
        duration=duration
    )
    
    # Commit the transaction
    db.commit()
    
    return dict(sampling_id=sampling_id)

@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=4)

# location stuff

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

# end of location stuff

# start of user stat stuff

@action('user_stats')
@action.uses('user_stats.html', db, auth.user)
def user_stats():
    return dict(
        load_species_url = URL('load_species'),
        order_first_seen_url = URL('order_first_seen'),
        order_recently_seen_url = URL('order_recently_seen'),
        reset_url = URL('reset'),
    )

@action('load_species')
@action.uses(db,auth.user)
def load_species():
    # Select rows that have the current user email in checklist and also have the same sampling_id/sample_id
    # Select the name, date and time. 
    rows = db(
        (db.checklist.email == get_user_email()) &
        (db.checklist.sampling_id == db.sightings.sighting_id)).select(
            db.sightings.name, db.checklist.date, db.checklist.time).as_list()
 
    # Final list will be the list returned. It will have dicts that have the name, date and time, and are
    # distinct. With the way they are added to the list, the order should be preserved. 
    final_list = []
    temp_list = []
    for row in rows:
        if row['sightings']['name'] not in temp_list:
            temp_list.append(row['sightings']['name'])
            final_list.append(dict(
                name=row['sightings']['name'],
                date=row['checklist']['date'],
                time=row['checklist']['time']))

    data = db((db.checklist.email == get_user_email()) &
        (db.checklist.sampling_id == db.sightings.sighting_id)).select(
            db.checklist.date, db.sightings.observation_count).as_list()

    print("data in controllers.py")
    for row in data:
        print(row)

    return dict(species_list=final_list, query="", plot_data=data)

@action('order_first_seen', method='POST')
@action.uses(db, auth.user)
def order_first_seen():
    myorder = db.checklist.date | db.checklist.time
    
    # Join tables and select those that have the same email as the current user, also order by date and time.
    rows = db((db.checklist.sampling_id == db.sightings.sighting_id) & 
              (db.checklist.email == get_user_email())).select(
                  db.sightings.name, db.checklist.date, db.checklist.time, orderby=myorder).as_list()
    
    # Now that the bird names are ordered by date and time, we just need to add to the final list all the distinct
    # names, aka all names that are not yet in the list. 
    final_list = []
    temp_list = []
    for row in rows:
        if row['sightings']['name'] not in temp_list:
            temp_list.append(row['sightings']['name'])
            final_list.append(dict(
                name=row['sightings']['name'],
                date=row['checklist']['date'],
                time=row['checklist']['time']))

    return dict(species_list=final_list)

@action('order_recently_seen', method='POST')
@action.uses(db, auth.user)
def order_first_seen():
    myorder = ~db.checklist.date | ~db.checklist.time

    rows = db((db.checklist.sampling_id == db.sightings.sighting_id) & 
              (db.checklist.email == get_user_email())).select(
                  db.sightings.name, db.checklist.date, db.checklist.time, orderby=myorder).as_list()
    
    final_list = []
    temp_list = []
    for row in rows:
        if row['sightings']['name'] not in temp_list:
            temp_list.append(row['sightings']['name'])
            final_list.append(dict(
                name=row['sightings']['name'],
                date=row['checklist']['date'],
                time=row['checklist']['time']))

    return dict(species_list=final_list)

@action('reset', method='POST')
@action.uses(db, auth.user)
def reset():
    rows = db(
        (db.checklist.email == get_user_email()) &
        (db.checklist.sampling_id == db.sightings.sighting_id)).select(
            db.sightings.name, db.checklist.date, db.checklist.time).as_list()
    
    final_list = []
    temp_list = []
    for row in rows:
        if row['sightings']['name'] not in temp_list:
            temp_list.append(row['sightings']['name'])
            final_list.append(dict(
                name=row['sightings']['name'],
                date=row['checklist']['date'],
                time=row['checklist']['time']))
   
    return dict(species_list=final_list)

# end of user stat stuff