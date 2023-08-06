## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">New ${model_title}</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {0}".format(model_title_plural), index_url)}</li>
</%def>

<ul id="context-menu">
  ${self.context_menu_items()}
</ul>

<div class="form-wrapper">
  ${form.render()|n}
</div><!-- form-wrapper -->
