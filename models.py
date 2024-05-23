"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table('checklist',
                Field('sampling_id'),
                Field('latitude'),
                Field('longitude'),
                Field('date', 'date'), #re-check (create function like get_time?)
                Field('time', 'time'), #re-check
                Field('email', default=get_user_email),
                Field('duration', 'integer')
                )

db.define_table('sightings',
                Field('sampling_id', 'reference checklist'),
				Field('name', 'string'),
				Field('observation_count', 'integer', default=0),               
                )

db.define_table('species',
                Field('name', 'reference sightings'),
                )
db.commit()

