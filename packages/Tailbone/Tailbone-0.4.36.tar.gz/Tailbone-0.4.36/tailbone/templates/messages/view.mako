## -*- coding: utf-8 -*-
<%inherit file="/master/view.mako" />

<%def name="context_menu_items()">
  % if recipient:
      % if recipient.status == rattail.enum.MESSAGE_STATUS_INBOX:
          <li>${h.link_to("Back to Message Inbox", url('messages.inbox'))}</li>
          <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
          <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
          <li>${h.link_to("Move this Message to my Archive", url('messages.move', uuid=instance.uuid) + '?dest=archive')}</li>
      % else:
          <li>${h.link_to("Back to Message Archive", url('messages.archive'))}</li>
          <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
          <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
          <li>${h.link_to("Move this Message to my Inbox", url('messages.move', uuid=instance.uuid) + '?dest=inbox')}</li>
      % endif
  % else:
      <li>${h.link_to("Back to Sent Messages", url('messages.sent'))}</li>
      <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
      <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
  % endif
</%def>

${parent.body()}







