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
                Field('sampling_id', 'string'),
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
                Field('sightings_id', 'string'),
                #Field('species_id', 'reference species'),
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
            db.species.insert(type=row[0])


if db(db.checklist).isempty():
    with open(checklist_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row (header)
        for row in reader:
            duration = 0 if row[6] == '' else float(row[6])  # Convert to float first
            (db.checklist.insert(sampling_id = row[0],
                                    latitude = row[1],
                                    longitude = row[2],
                                    date = row[3],
                                    time = row[4],
                                    email = row[5] + ("@example.com"),
                                    duration = int(duration)
                                    ))
db.sightings.truncate()

if db(db.sightings).isempty():
    with open(sightings_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the first row (header)
        for row in reader:
            observation_count = 0 if row[2] == 'X' else int(row[2])
            db.sightings.insert(sightings_id=row[0], name=row[1], observation_count=observation_count)

db.commit()

