"""
This file defines the database models
"""

import datetime
import os
import csv
from .common import db, Field, auth
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

db.define_table('species',
                Field('type', 'string'),
                )


db.define_table('sightings',
                Field('sampling_id', 'reference checklist'),
                Field('species_id', 'reference species'),
                Field('name', 'string'),
                Field('observation_count', 'integer', default=0),               
                )


# Get the path to the species.csv file
current_dir = os.path.dirname(__file__)
sightings_file_path = os.path.join(current_dir, 'uploads', 'sightings.csv')
species_file_path = os.path.join(current_dir, 'uploads', 'species.csv')
checklist_file_path = os.path.join(current_dir, 'uploads', 'checklists.csv')


if db(db.species).isempty():
    with open(species_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row (header)
        for row in reader:
            #print(row)
            db.species.insert(type=row[0])

if db(db.sightings).isempty():
    with open(sightings_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row (header)
        for row in reader:
            #print(row)
            observation_count = 0 if row[2] == 'X' else int(row[2])
            #print(db.sightings._insert(name=row[1], observation_count=observation_count))
            db.sightings.insert(name=row[1], observation_count=observation_count)

if db(db.checklist).isempty():
    with open(checklist_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row (header)
        for row in reader:
            #print(row)
            duration = 0 if row[6] == '' else float(row[6])  # Convert to float first
            (db.checklist.insert(sampling_id = row[0],
                                    latitude = row[1],
                                    longitude = row[2],
                                    date = row[3],
                                    time = row[4],
                                    email = row[5] + ("@example.com"),
                                    duration = int(duration)
                                    ))
#print(db.species)
#print(db.species._insert(name='Alex'))

db.commit()

#print to check if db was properly filled
things = db(db.sightings).select()
print(things)
