## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">${model_title}: ${unicode(instance)}</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {0}".format(model_title_plural), url(route_prefix))}</li>
  % if master.viewable and request.has_perm('{0}.view'.format(permission_prefix)):
      <li>${h.link_to("View this {0}".format(model_title), action_url('view', instance))}</li>
  % endif
  % if master.deletable and request.has_perm('{0}.delete'.format(permission_prefix)):
      <li>${h.link_to("Delete this {0}".format(model_title), action_url('delete', instance))}</li>
  % endif
</%def>

<ul id="context-menu">
  ${self.context_menu_items()}
</ul>

<div class="form-wrapper">
  ${form.render()|n}
</div><!-- form-wrapper -->
