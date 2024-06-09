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
        my_callback_url = URL('my_callback', signer=url_signer),
        user_stats_url = URL('user_stats')
    )

@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=4)

@action('user_stats')
@action.uses('user_stats.html', db, auth.user)
def user_stats():
    return dict(
        load_species_url = URL('load_species'),
        order_first_seen_url = URL('order_first_seen'),
        order_recently_seen_url = URL('order_recently_seen')
    )

@action('load_species')
@action.uses(db,auth.user)
def load_species():
    # Out of the checklists that have the same email as the user, if the 
    # checklist sampling id matches the sample id, then this person saw it.
    #rows = db(
        #(db.checklist.email == get_user_email()) &
        #(db.checklist.sampling_id == db.sightings.sample_id)).select(
           #db.sightings.name, distinct =True).as_list()
    
    # Select rows that have the current user email in checklist and also have the same sampling_id/sample_id
    # Select the name, date and time. 
    rows = db(
        (db.checklist.email == get_user_email()) &
        (db.checklist.sampling_id == db.sightings.sample_id)).select(
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

    for row in final_list:
        print(row) 

    plot_data = db((db.checklist.email == get_user_email()) &
        (db.checklist.sampling_id == db.sightings.sample_id)).select(
            db.checklist.date, db.sightings.observation_count).as_list()
    for row in plot_data:
        print(row)

    return dict(species_list=final_list, query="", all_sightings_list=plot_data)


@action('order_first_seen', method='POST')
@action.uses(db, auth.user)
def order_first_seen():
    myorder = db.checklist.date | db.checklist.time
    #rows = db(
    #(db.checklist.email == get_user_email()) & 
    #(db.checklist.sampling_id == db.sightings.sample_id)
    #).select(db.sightings.name, distinct=True, orderby=myorder)

    # Join tables and select those that have the same email as the current user, also order by date and time.
    rows = db((db.checklist.sampling_id == db.sightings.sample_id) & 
              (db.checklist.email == get_user_email())).select(
                  db.sightings.name, db.checklist.date, db.checklist.time, orderby=myorder).as_list()
    
    # Now that the bird names are ordered by date and time, we just need to add to the final list all the distinct
    # names, aka all names that are not yet in the list. 
    #final_list = []
    #temp_list = []
    #for row in rows:
    #    if row['name'] not in temp_list:
    #        temp_list.append(row['name'])
    #        final_list.append(dict(name=row['name']))
    final_list = []
    temp_list = []
    for row in rows:
        if row['sightings']['name'] not in temp_list:
            temp_list.append(row['sightings']['name'])
            final_list.append(dict(
                name=row['sightings']['name'],
                date=row['checklist']['date'],
                time=row['checklist']['time']))

    print("length 1 " + str(len(rows)))
    print(final_list)
    print(len(final_list))

    # Tests to see if it works for the reverse order.
    #rows2 = db((db.checklist.sampling_id == db.sightings.sample_id)
    #          & (db.checklist.email == get_user_email())).select(db.sightings.name, orderby=~myorder).as_list()

    #final_list2 = []
    #temp_list2 = []
    #for row in rows2:
    #    if row['name'] not in temp_list2:
    #        temp_list2.append(row['name'])
    #        final_list2.append(dict(name=row['name']))

    #print("length 2 " + str(len(rows2)))
    #print(final_list2)
    #print(len(final_list2))

    return dict(species_list=final_list)


@action('order_recently_seen', method='POST')
@action.uses(db, auth.user)
def order_first_seen():
    myorder = ~db.checklist.date | ~db.checklist.time

    rows = db((db.checklist.sampling_id == db.sightings.sample_id) & 
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

    print(final_list)
    print(len(final_list))

    return dict(species_list=final_list)
    