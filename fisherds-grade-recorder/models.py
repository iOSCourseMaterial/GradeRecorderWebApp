
from google.appengine.ext import ndb

class GradeEntry(ndb.model):
    """ Score for a student on an assignment. """
    student_name = ndb.StringProperty()
    score = ndb.IntegerProperty()
    assignment_id = ndb.IntegerProperty()
    last_touch_date_time = ndb.DateTimeProperty(auto_now=True)
    owner = ndb.UserProperty()

class Assignment(ndb.model):
    """ Assignment. """
    assignment_name = ndb.StringProperty()
    last_touch_date_time = ndb.DateTimeProperty(auto_now=True)
    owner = ndb.UserProperty()
    