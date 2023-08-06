# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
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
Message Views
"""

from __future__ import unicode_literals, absolute_import

from rattail import enum
from rattail.db import model

import formalchemy
from pyramid import httpexceptions
from webhelpers.html import tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView


class SubjectFieldRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        subject = self.raw_value
        if not subject:
            return ''
        return tags.link_to(subject, self.request.route_url('messages.view', uuid=self.field.parent.model.uuid))


class SenderFieldRenderer(forms.renderers.UserFieldRenderer):

    def render_readonly(self, **kwargs):
        sender = self.raw_value
        if sender is self.request.user:
            return 'you'
        return super(SenderFieldRenderer, self).render_readonly(**kwargs)


class RecipientsFieldRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        recipients = self.raw_value
        if not recipients:
            return ''
        recips = filter(lambda r: r.recipient is not self.request.user, recipients)
        recips = sorted([r.recipient.display_name for r in recips])
        if len(recips) < len(recipients):
            recips.insert(0, 'you')
        return ', '.join(recips)


class TerseRecipientsFieldRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        recipients = self.raw_value
        if not recipients:
            return ''
        recips = filter(lambda r: r.recipient is not self.request.user, recipients)
        recips = sorted([r.recipient.display_name for r in recips])
        if len(recips) < 5:
            return ', '.join(recips)
        return "{}, ...".format(', '.join(recips[:4]))


class MessagesView(MasterView):
    """
    Base class for message views.
    """
    model_class = model.Message
    creatable = False
    editable = False
    deletable = False
    checkboxes = True

    def get_index_url(self):
        # not really used, but necessary to make certain other code happy
        return self.request.route_url('messages.inbox')

    def index(self):
        if not self.request.user:
            raise httpexceptions.HTTPForbidden
        return super(MessagesView, self).index()

    def get_instance(self):
        if not self.request.user:
            raise httpexceptions.HTTPForbidden
        message = super(MessagesView, self).get_instance()
        if not self.associated_with(message):
            raise httpexceptions.HTTPForbidden
        return message

    def associated_with(self, message):
        if message.sender is self.request.user:
            return True
        for recip in message.recipients:
            if recip.recipient is self.request.user:
                return True
        return False

    def query(self, session):
        return session.query(model.Message)\
            .outerjoin(model.MessageRecipient)\
            .filter(model.MessageRecipient.recipient == self.request.user)

    def configure_grid(self, g):

        g.joiners['sender'] = lambda q: q.join(model.User, model.User.uuid == model.Message.sender_uuid).outerjoin(model.Person)
        g.filters['sender'] = g.make_filter('sender', model.Person.display_name,
                                            default_active=True, default_verb='contains')
        g.sorters['sender'] = g.make_sorter(model.Person.display_name)

        g.filters['subject'].default_active = True
        g.filters['subject'].default_verb = 'contains'

        g.default_sortkey = 'sent'
        g.default_sortdir = 'desc'

        g.configure(
            include=[
                g.subject.with_renderer(SubjectFieldRenderer),
                g.sender.with_renderer(SenderFieldRenderer).label("From"),
                g.recipients.with_renderer(TerseRecipientsFieldRenderer).label("To"),
                g.sent.with_renderer(forms.renderers.DateTimeFieldRenderer(self.rattail_config)),
            ],
            readonly=True)

    def row_attrs(self, row, i):
        recip = self.get_recipient(row)
        if recip:
            return {'data-uuid': recip.uuid}
        return {}

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.subject,
                fs.sender.with_renderer(SenderFieldRenderer).label("From"),
                fs.recipients.with_renderer(RecipientsFieldRenderer).label("To"),
                fs.sent.with_renderer(forms.renderers.DateTimeFieldRenderer(self.rattail_config)),
                fs.body,
            ])
        if self.viewing:
            del fs.body

    def get_recipient(self, message):
        for recip in message.recipients:
            if recip.recipient is self.request.user:
                return recip

    def template_kwargs_view(self, **kwargs):
        message = kwargs['instance']
        return {'message': message,
                'recipient': self.get_recipient(message)}

    def move(self):
        """
        Move a message, either to the archive or back to the inbox.
        """
        message = self.get_instance()
        recipient = None
        for recip in message.recipients:
            if recip.recipient is self.request.user:
                recipient = recip
                break
        if not recipient:
            raise httpexceptions.HTTPForbidden

        dest = self.request.GET.get('dest')
        if dest not in ('inbox', 'archive'):
            self.request.session.flash("Sorry, I couldn't make sense out of that request.")
            return self.redirect(self.request.get_referrer(
                default=self.request.route_url('messages_inbox')))

        new_status = enum.MESSAGE_STATUS_INBOX if dest == 'inbox' else enum.MESSAGE_STATUS_ARCHIVE
        if recipient.status != new_status:
            recipient.status = new_status
        return self.redirect(self.request.route_url('messages.{}'.format(
            'archive' if dest == 'inbox' else 'inbox')))

    def move_bulk(self):
        """
        Move messages in bulk, to the archive or back to the inbox.
        """
        dest = self.request.POST.get('destination', 'archive')
        if self.request.method == 'POST':
            uuids = self.request.POST.get('uuids', '').split(',')
            if uuids:
                new_status = enum.MESSAGE_STATUS_INBOX if dest == 'inbox' else enum.MESSAGE_STATUS_ARCHIVE
                for uuid in uuids:
                    recip = Session.query(model.MessageRecipient).get(uuid) if uuid else None
                    if recip and recip.recipient is self.request.user:
                        if recip.status != new_status:
                            recip.status = new_status
        route = 'messages.{}'.format('archive' if dest == 'inbox' else 'inbox')
        return self.redirect(self.request.route_url(route))


class InboxView(MessagesView):
    """
    Inbox message view.
    """
    url_prefix = '/messages/inbox'
    grid_key = 'messages.inbox'

    def get_index_url(self):
        return self.request.route_url('messages.inbox')

    def query(self, session):
        q = super(InboxView, self).query(session)
        return q.filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_INBOX)


class ArchiveView(MessagesView):
    """
    Archived message view.
    """
    url_prefix = '/messages/archive'
    grid_key = 'messages.archive'

    def get_index_url(self):
        return self.request.route_url('messages.archive')

    def query(self, session):
        q = super(ArchiveView, self).query(session)
        return q.filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_ARCHIVE)


class SentView(MessagesView):
    """
    Sent messages view.
    """
    url_prefix = '/messages/sent'
    grid_key = 'messages.sent'
    checkboxes = False

    def get_index_url(self):
        return self.request.route_url('messages.sent')

    def query(self, session):
        return session.query(model.Message)\
            .filter(model.Message.sender == self.request.user)

    def configure_grid(self, g):
        super(SentView, self).configure_grid(g)
        g.filters['sender'].default_active = False


def includeme(config):

    # inbox
    config.add_route('messages.inbox', '/messages/inbox/')
    config.add_view(InboxView, attr='index', route_name='messages.inbox')

    # archive
    config.add_route('messages.archive', '/messages/archive/')
    config.add_view(ArchiveView, attr='index', route_name='messages.archive')

    # move bulk
    config.add_route('messages.move_bulk', '/messages/move-bulk')
    config.add_view(MessagesView, attr='move_bulk', route_name='messages.move_bulk')

    # sent
    config.add_route('messages.sent', '/messages/sent/')
    config.add_view(SentView, attr='index', route_name='messages.sent')

    # view
    config.add_route('messages.view', '/messages/{uuid}')
    config.add_view(MessagesView, attr='view', route_name='messages.view')

    # move (single)
    config.add_route('messages.move', '/messages/{uuid}/move')
    config.add_view(MessagesView, attr='move', route_name='messages.move')
