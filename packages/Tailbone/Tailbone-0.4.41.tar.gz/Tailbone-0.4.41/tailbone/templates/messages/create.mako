## -*- coding: utf-8 -*-
<%inherit file="/master/create.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.javascript_link(request.static_url('tailbone:static/js/lib/tag-it.min.js'))}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/jquery.tagit.css'))}
  <script type="text/javascript">
    $(function() {

        var recipients = $('.recipients ul');

        recipients.tagit({
            fieldName: 'Message--recipients',
            autocomplete: {
                delay: 0,
                minLength: 2,
                autoFocus: true,
                source: function(request, response) {
                    $.get('${url('messages.recipients')}', {term: request.term}, response);
                },
                select: function(event, ui) {
                    recipients.tagit('createTag', ui.item.value + ',' + ui.item.label);
                    // Preventing the tag input to be updated with the chosen value.
                    return false;
                }
            },
            beforeTagAdded: function(event, ui) {
                var label = ui.tagLabel.split(',');
                var value = label.shift();
                $(ui.tag).find('.tagit-hidden-field').val(value);
                $(ui.tag).find('.tagit-label').text(label.join());
            },
            removeConfirmation: true
        });

        // set focus to recipients field
        recipients.data('ui-tagit').tagInput.focus();

    });
  </script>
  <style type="text/css">

    .field-wrapper.subject .field input[type="text"] {
        width: 99%;
    }

  </style>
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('messages.list'):
      <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
      <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
      <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
  % endif
</%def>

${parent.body()}
