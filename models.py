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


db.define_table('species', 
                Field('name', 'string', requires = IS_NOT_EMPTY()))


# For the date and time fields maybe we should define a function like the 
# one above so it's automatic.
db.define_table('checklist', 
                Field('event', requires = IS_NOT_EMPTY()),
                Field('latitude', requires = IS_NOT_EMPTY()),
                Field('longitude', requires = IS_NOT_EMPTY()),
                Field('date', requires = IS_NOT_EMPTY()),
                Field('time', requires = IS_NOT_EMPTY()),
                Field('checklist_id', requires = IS_NOT_EMPTY()),
                Field('duration'),
                )

db.define_table('sightings',
                Field('sightings_id'),
                Field('name', requires = IS_NOT_EMPTY()),
                Field('count', requires = IS_NOT_EMPTY())
                )

# I also named the ids of the checklist table and sightings table different
# from just id so that there's no confusion between the assigned id and the
# id listed in the table.

db.commit()
