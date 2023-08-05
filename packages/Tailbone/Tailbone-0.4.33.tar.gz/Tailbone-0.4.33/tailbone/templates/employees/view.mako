## -*- coding: utf-8 -*-
<%inherit file="/master/view.mako" />

${parent.body()}

<h2>Departments</h2>

% if departments:
    <p>This employee is assigned to the following departments:</p>
    ${departments.render_grid()|n}
% else:
    <p>This employee is not assigned to any departments.</p>
% endif
