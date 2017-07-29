$(function() {

    var $vis_select = $('#vis-select');
    $.ajax({
        type: 'GET',
        url: '/api/visualizers',
        success: function(data) {
            $.each(data.visualizers, function(i, visualization) {
                $vis_select.append('<option>'+ visualization.name +'</option>');
            });
        }
    });
});
