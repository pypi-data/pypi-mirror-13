## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <% bounce = form.fieldset.model %>
  <li>${h.link_to("Back to Email Bounces", url('emailbounces'))}</li>
  % if not bounce.processed and request.has_perm('emailbounces.process'):
      <li>${h.link_to("Mark this Email Bounce as Processed", url('emailbounce.process', uuid=bounce.uuid))}</li>
  % elif bounce.processed and request.has_perm('emailbounces.unprocess'):
      <li>${h.link_to("Mark this Email Bounce as UN-processed", url('emailbounce.unprocess', uuid=bounce.uuid))}</li>
  % endif
</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">
    #message {
        border: 1px solid #000000;
        height: 400px;
        overflow: auto;
        padding: 4px;
    }
  </style>
  <script type="text/javascript">

    function autosize_message(scrolldown) {
        var msg = $('#message');
        var height = $(window).height() - msg.offset().top - 50;
        msg.height(height);
        if (scrolldown) {
            msg.animate({scrollTop: msg.get(0).scrollHeight - height}, 250);
        }
    }

    $(function () {
        autosize_message(true);
        $('#message').focus();
    });

    $(window).resize(function() {
        autosize_message(false);
    });

  </script>
</%def>

${parent.body()}

<pre id="message">
${message}
</pre>
