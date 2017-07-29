$("document").ready(function() {

    var vis_select = $('#vis-select');
    var settings_list = $('#settings-list');
    $.ajax({
        type: 'GET',
        url: '/api/visualizers',
        success: function(data) {
            $.each(data.visualizers, function(i, visualization) {
                vis_select.append('<option>'+ visualization.name +'</option>');
            });
        }
    });

    $('#vis-select').on('change', function() {
        var selected_vis = this.options[this.selectedIndex].text;
        settings_list.empty();
        $.ajax({
            type: 'GET',
            url: '/api/visualizers/' + selected_vis,
            success: function(data) {
                $.each(data.settings, function(setting, options) {
                    settings_list.append('<li>' + setting + '<select class="form-control" id='+setting+'-setting></select></li>')
                });
            }
        });
    });
});
