## -*- coding: utf-8 -*-
<div class="newgrid-wrapper">
  % if grid.filterable:
      ${grid.render_filters()|n}
  % endif
  % if tools:
      <div class="grid-tools">
        ${tools|n}
      </div>
  % endif
  ${grid.render_grid()|n}
</div><!-- newgrid-wrapper -->
