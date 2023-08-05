# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Employee Views
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail import enum
from rattail.db import model

from tailbone import forms
from tailbone.views import MasterView, AutocompleteView
from tailbone.newgrids.filters import EnumValueRenderer


class EmployeesView(MasterView):
    """
    Master view for the Employee class.
    """
    model_class = model.Employee

    def configure_grid(self, g):

        g.joiners['phone'] = lambda q: q.outerjoin(model.EmployeePhoneNumber, sa.and_(
            model.EmployeePhoneNumber.parent_uuid == model.Employee.uuid,
            model.EmployeePhoneNumber.preference == 1))
        g.joiners['email'] = lambda q: q.outerjoin(model.EmployeeEmailAddress, sa.and_(
            model.EmployeeEmailAddress.parent_uuid == model.Employee.uuid,
            model.EmployeeEmailAddress.preference == 1))

        g.filters['first_name'] = g.make_filter('first_name', model.Person.first_name)
        g.filters['last_name'] = g.make_filter('last_name', model.Person.last_name)

        g.filters['email'] = g.make_filter('email', model.EmployeeEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.EmployeePhoneNumber.number,
                                           label="Phone Number")

        if self.request.has_perm('employees.edit'):
            g.filters['id'].label = "ID"
            g.filters['status'].default_active = True
            g.filters['status'].default_verb = 'equal'
            g.filters['status'].default_value = enum.EMPLOYEE_STATUS_CURRENT
            g.filters['status'].set_value_renderer(EnumValueRenderer(enum.EMPLOYEE_STATUS))
        else:
            del g.filters['id']
            del g.filters['status']

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.sorters['first_name'] = lambda q, d: q.order_by(getattr(model.Person.first_name, d)())
        g.sorters['last_name'] = lambda q, d: q.order_by(getattr(model.Person.last_name, d)())

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.EmployeeEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.EmployeePhoneNumber.number, d)())

        g.default_sortkey = 'first_name'

        g.append(forms.AssociationProxyField('first_name'))
        g.append(forms.AssociationProxyField('last_name'))

        g.configure(
            include=[
                g.id.label("ID"),
                g.first_name,
                g.last_name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                g.status.with_renderer(forms.EnumFieldRenderer(enum.EMPLOYEE_STATUS)),
            ],
            readonly=True)

        if not self.request.has_perm('employees.edit'):
            del g.id
            del g.status

    def query(self, session):
        q = session.query(model.Employee).join(model.Person)
        if not self.request.has_perm('employees.edit'):
            q = q.filter(model.Employee.status == enum.EMPLOYEE_STATUS_CURRENT)
        return q

    def configure_fieldset(self, fs):
        fs.append(forms.AssociationProxyField('first_name'))
        fs.append(forms.AssociationProxyField('last_name'))
        fs.append(forms.AssociationProxyField('display_name'))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.first_name,
                fs.last_name,
                fs.display_name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.status.with_renderer(forms.EnumFieldRenderer(enum.EMPLOYEE_STATUS)),
            ])


class EmployeesAutocomplete(AutocompleteView):
    """
    Autocomplete view for the Employee model, but restricted to return only
    results for current employees.
    """
    mapped_class = model.Person
    fieldname = 'display_name'

    def filter_query(self, q):
        return q.join(model.Employee)\
            .filter(model.Employee.status == enum.EMPLOYEE_STATUS_CURRENT)

    def value(self, person):
        return person.employee.uuid


def includeme(config):

    # autocomplete
    config.add_route('employees.autocomplete',  '/employees/autocomplete')
    config.add_view(EmployeesAutocomplete, route_name='employees.autocomplete',
                    renderer='json', permission='employees.list')

    EmployeesView.defaults(config)
