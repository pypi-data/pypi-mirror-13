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
Email Views
"""

from __future__ import unicode_literals, absolute_import

from pyramid.httpexceptions import HTTPFound

from rattail import mail

from tailbone import forms
from tailbone.views import MasterView, View
from tailbone.newgrids import Grid, GridColumn


class ProfilesView(MasterView):
    """
    Master view for email admin (settings/preview).
    """
    normalized_model_name = 'emailprofile'
    model_title = "Email Profile"
    model_key = 'key'
    url_prefix = '/email/profiles'

    grid_factory = Grid
    filterable = False
    pageable = False

    creatable = False
    editable = False
    deletable = False

    def get_data(self, session=None):
        data = []
        for email in mail.iter_emails(self.rattail_config):
            key = email.key or email.__name__
            email = email(self.rattail_config, key)
            data.append(self.normalize(email))
        return data

    def normalize(self, email):
        def get_recips(type_):
            recips = email.get_recips(type_)
            if recips:
                return ', '.join(recips)
        data = email.sample_data(self.request)
        return {
            'key': email.key,
            'fallback_key': email.fallback_key,
            'description': email.__doc__,
            'prefix': email.get_prefix(data),
            'subject': email.get_subject(data),
            'sender': email.get_sender(),
            'replyto': email.get_replyto(),
            'to': get_recips('to'),
            'cc': get_recips('cc'),
            'bcc': get_recips('bcc'),
        }

    def configure_grid(self, g):
        g.columns = [
            GridColumn('key'),
            GridColumn('prefix'),
            GridColumn('subject'),
            GridColumn('to'),
        ]

        g.sorters['key'] = g.make_sorter('key', foldcase=True)
        g.sorters['prefix'] = g.make_sorter('prefix', foldcase=True)
        g.sorters['subject'] = g.make_sorter('subject', foldcase=True)
        g.sorters['to'] = g.make_sorter('to', foldcase=True)
        g.default_sortkey = 'key'

        # g.main_actions = []
        g.more_actions = []

    def get_instance(self):
        key = self.request.matchdict['key']
        return self.normalize(mail.get_email(self.rattail_config, key))

    def get_instance_title(self, email):
        return email['key']

    def make_form(self, email, **kwargs):
        """
        Make a simple form for use with CRUD views.
        """
        # TODO: This needs all kinds of help still...

        class EmailSchema(forms.Schema):
            pass

        form = forms.SimpleForm(self.request, schema=EmailSchema(), obj=email)
        form.creating = self.creating
        form.editing = self.editing
        form.readonly = self.viewing

        if self.creating:
            form.cancel_url = self.get_index_url()
        else:
            form.cancel_url = self.get_action_url('view', email)

        form.fieldset = forms.FieldSet()
        form.fieldset.fields['key'] = forms.Field('key', value=email['key'])
        form.fieldset.fields['fallback_key'] = forms.Field('fallback_key', value=email['fallback_key'])
        form.fieldset.fields['prefix'] = forms.Field('prefix', value=email['prefix'], label="Subject Prefix")
        form.fieldset.fields['subject'] = forms.Field('subject', value=email['subject'], label="Subject Text")
        form.fieldset.fields['description'] = forms.Field('description', value=email['description'])
        form.fieldset.fields['sender'] = forms.Field('sender', value=email['sender'], label="From")
        form.fieldset.fields['replyto'] = forms.Field('replyto', value=email['replyto'], label="Reply-To")
        form.fieldset.fields['to'] = forms.Field('to', value=email['to'])
        form.fieldset.fields['cc'] = forms.Field('cc', value=email['cc'])
        form.fieldset.fields['bcc'] = forms.Field('bcc', value=email['bcc'])

        return form

    def template_kwargs_view(self, **kwargs):
        key = self.request.matchdict['key']
        kwargs['email'] = mail.get_email(self.rattail_config, key)
        return kwargs


class EmailPreview(View):
    """
    Lists available email templates, and can show previews of each.
    """

    def __call__(self):

        # Forms submitted via POST are only used for sending emails.
        if self.request.method == 'POST':
            self.email_template()
            return HTTPFound(location=self.request.get_referrer(
                default=self.request.route_url('emailprofiles')))

        # Maybe render a preview?
        key = self.request.GET.get('key')
        if key:
            type_ = self.request.GET.get('type', 'html')
            return self.preview_template(key, type_)

        assert False, "should not be here"

    def email_template(self):
        recipient = self.request.POST.get('recipient')
        if recipient:
            keys = filter(lambda k: k.startswith('send_'), self.request.POST.iterkeys())
            key = keys[0][5:] if keys else None
            if key:
                email = mail.get_email(self.rattail_config, key)
                data = email.sample_data(self.request)
                msg = email.make_message(data)

                subject = msg['Subject']
                del msg['Subject']
                msg['Subject'] = "[preview] {0}".format(subject)

                del msg['To']
                del msg['Cc']
                del msg['Bcc']
                msg['To'] = recipient

                mail.deliver_message(self.rattail_config, msg)

                self.request.session.flash("Preview for '{0}' was emailed to {1}".format(key, recipient))

    def preview_template(self, key, type_):
        email = mail.get_email(self.rattail_config, key)
        template = email.get_template(type_)
        data = email.sample_data(self.request)
        self.request.response.text = template.render(**data)
        if type_ == 'txt':
            self.request.response.content_type = b'text/plain'
        return self.request.response


def includeme(config):
    ProfilesView.defaults(config)

    config.add_route('email.preview', '/email/preview/')
    config.add_view(EmailPreview, route_name='email.preview',
                    renderer='/email/preview.mako',
                    permission='admin')
