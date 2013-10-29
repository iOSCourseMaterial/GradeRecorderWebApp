#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

import endpoints
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb

from models import Assignment
from models import GradeEntry
import time
import logging

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            grades = [];
            assignment_query = Assignment.query().order(Assignment.assignment_name).filter(Assignment.owner == user)
            for an_assignment in assignment_query:
                assignment_dict = {'assignment_name': an_assignment.assignment_name}
                grade_entries = []
                grade_entry_query = GradeEntry.query().order(GradeEntry.student_name).filter(GradeEntry.owner == user).filter(GradeEntry.assignment_id == an_assignment.id)
                for a_grade_entry in grade_entry_query:
                    grade_entries.append(a_grade_entry)
                assignment_dict['grade_entries'] = grade_entries
                grades.append(assignment_dict)
            self.response.out.write(template.render('templates/graderecorder.html',
                                                    {'grades': grades,
                                                     'assignments': assignment_query,
                                                     'use_hardcoded_roster': True,
                                                     'user_email': user.email(),
                                                     'logout_link': users.create_logout_url("/")}))

    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        if (self.request.get('type') == 'Assignment'):
            new_assignment = Assignment(assignment_name = self.request.get('assignment_name'), owner=user)
            new_assignment.put()
        else:
            an_assignment_key = ndb.Key(Assignment, int(self.request.get('assignment_id')))
            assignment_for_entry = an_assignment_key.get()
            if assignment_for_entry is None:
                raise endpoints.NotFoundException('Assignment id not found')
            if user != assignment_for_entry.owner:
                raise endpoints.ForbiddenException("You can only edit/create grade entries in your own Assignments.")
            new_grade_entry = GradeEntry(student_name = self.request.get('student_name'),
                               score = int(self.request.get('score')),
                               assignment_id = int(self.request.get('assignment_id')),
                               parent = assignment_for_entry.key,
                               owner=user)
            new_grade_entry.put()
        time.sleep(0.5)
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
