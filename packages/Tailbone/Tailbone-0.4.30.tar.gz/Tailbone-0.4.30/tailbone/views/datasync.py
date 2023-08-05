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
DataSync Views
"""

from __future__ import unicode_literals

from rattail.db import model

from tailbone import forms
from tailbone.views import MasterView


class DataSyncChangeView(MasterView):
    """
    Master view for the DataSyncChange model.
    """
    model_class = model.DataSyncChange
    model_title = "DataSync Change"

    creatable = False
    viewable = False
    editable = False
    deletable = False

    def configure_grid(self, g):
        g.default_sortkey = 'obtained'
        g.obtained.set(renderer=forms.DateTimeFieldRenderer(self.rattail_config))
        g.configure(
            include=[
                g.source,
                g.payload_type,
                g.payload_key,
                g.deletion,
                g.obtained,
                g.consumer,
            ],
            readonly=True)


def includeme(config):
    DataSyncChangeView.defaults(config)
