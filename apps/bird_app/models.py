"""
This file defines the database models
"""

import datetime
import os
import csv
from common import db, Field, auth
from pydal.validators import *

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

def get_curr_time():
    return datetime.time.utcnow()

def get_date():
    return datetime.date.utcnow()

### Define your table below
print("HELLO!")
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table('checklist',
                Field('sampling_id'),
                Field('latitude','double'),
                Field('longitude', 'double'),
                Field('date', 'date', default=get_date), #re-check (create function like get_time?)
                Field('time', 'time', default=get_curr_time), #re-check
                Field('email', default=get_user_email),
                Field('duration', 'integer')
                )

db.define_table('sightings',
                Field('sampling_id', 'reference checklist'),
                Field('name', 'string'),
                Field('observation_count', 'integer', default=0),               
                )

db.define_table('species',
                Field('name', 'string'),
                )

# Get the path to the species.csv file
current_dir = os.path.dirname(__file__)
species_file_path = os.path.join(current_dir, 'uploads', 'species.csv')

if db(db.species).isempty():
    with open(species_file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            #print(row)
            print(db.species._insert(name=row[0]))
            #db.species.insert(name=row[0])


#db.species.truncate()
#db.sightings.truncate()
#db.checklist.truncate()
#print(db.species)
#print(db.species._insert(name='Alex'))

db.commit()
