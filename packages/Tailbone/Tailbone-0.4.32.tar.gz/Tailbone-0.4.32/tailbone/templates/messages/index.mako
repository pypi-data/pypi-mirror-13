## -*- coding: utf-8 -*-
<%inherit file="/master/index.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  <script type="text/javascript">

    var destination = null;

    function update_move_button() {
        var count = $('.newgrid tbody td.checkbox input:checked').length;
        $('form[name="move-selected"] button')
            .button('option', 'label', "Move " + count + " selected to " + destination)
            .button('option', 'disabled', count < 1);
    }

    $(function() {

        update_move_button();

        $('.newgrid-wrapper').on('click', 'thead th.checkbox input', function() {
            update_move_button();
        });

        $('.newgrid-wrapper').on('click', 'tbody td.checkbox input', function() {
            update_move_button();
        });

        $('form[name="move-selected"]').submit(function() {
            var uuids = [];
            $('.newgrid tbody td.checkbox input:checked').each(function() {
                uuids.push($(this).parents('tr:first').data('uuid'));
            });
            if (! uuids.length) {
                return false;
            }
            $(this).find('[name="uuids"]').val(uuids.toString());
            $(this).find('button')
                .button('option', 'label', "Moving " + uuids.length + " messages to " + destination + "...")
                .button('disable');
        });

    });

  </script>
  <style type="text/css">
    .newgrid table {
        position: relative;
        top: -32px;
    }
    .newgrid .pager {
        position: relative;
        top: -32px;
    }
  </style>
</%def>

${parent.body()}
