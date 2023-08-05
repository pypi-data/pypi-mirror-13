## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">${model_title}: ${instance_title}</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {0}".format(model_title_plural), url(route_prefix))}</li>
  % if master.editable and request.has_perm('{0}.edit'.format(permission_prefix)):
      <li>${h.link_to("Edit this {0}".format(model_title), action_url('edit', instance))}</li>
  % endif
  % if master.deletable and master.deletable_instance(instance) and request.has_perm('{0}.delete'.format(permission_prefix)):
      <li>${h.link_to("Delete this {0}".format(model_title), action_url('delete', instance))}</li>
  % endif
</%def>

<ul id="context-menu">
  ${self.context_menu_items()}
</ul>

<div class="form-wrapper">
  ${form.render()|n}
</div><!-- form-wrapper -->
