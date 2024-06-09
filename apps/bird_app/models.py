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

#def get_time():
 #   return datetime.datetime.utcnow()

def get_curr_time():
    return datetime.datetime.utcnow().time()

def get_date():
    return datetime.datetime.utcnow().date()

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
                Field('sighting_id'),
                #Field('species_id', 'reference species'),
                Field('name', 'string'),
                Field('observation_count', 'integer', default=0), 
                #Field('user_email', default=get_user_email),                
                )
db.checklist.truncate()
(db.checklist.insert(sampling_id = "2002",
                                    latitude = 37.06096445677006,
                                    longitude = 37.06096445677006,
                                    date = "2021-02-03",
                                    time = "10:55:00",
                                    email = "resh20.rm@gmail.com",
                                    duration = 20
                                    ))
(db.checklist.insert(sampling_id = "2001",
                                    latitude = 37.06096445677006,
                                    longitude = 37.06096445677006,
                                    date = "2021-02-03",
                                    time = "10:55:00",
                                    email = "resh20.rm@gmail.com",
                                    duration = 20
                                    ))
(db.checklist.insert(sampling_id = "2003",
                                    latitude = 37.06096445677006,
                                    longitude = 37.06096445677006,
                                    email = "resh20.rm@gmail.com",
                                    duration = 20
                                    ))
db.sightings.truncate()

db.sightings.insert(sighting_id="2002", name="2002 Robin", observation_count=2)
db.sightings.insert(sighting_id="2002", name="2002 Pigeon", observation_count=2)
db.sightings.insert(sighting_id="2001", name="2001 Crow", observation_count=2)
db.sightings.insert(sighting_id="2001", name="2001 Swan", observation_count=2)
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
            observation_count = 0 if row[2] == 'X' else int(row[2])
            print(row[0])
            #print(db.sightings._insert(name=row[1], observation_count=observation_count))
            db.sightings.insert(sighting_id=row[0], name=row[1], observation_count=observation_count)

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


#print(db.species._insert(name='Alex'))

"""
things = db(db.sightings).select()
checklist = db(db.checklist).select()
sightings_list = db(db.sightings.sighting_id == db.checklist.sampling_id)
for row in sightings_list.select():
    print(row.checklist.sampling_id, row.sightings.name)
"""
db.commit()

#print to check if db was properly filled

#things = db(db.sightings.name).select()
s_id = "2002"
checklist = db((db.checklist.email == "resh20.rm@gmail.com")).select()
#for c in checklist:
 #   print(c, "sampling")
"""
print(checklist)
sightings_data = db(db.sightings).select()
print("Sightings Data:")
for record in sightings_data:
    print(record)

"""