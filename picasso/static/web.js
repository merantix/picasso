$("document").ready(function() {

    var vis_select = $('#vis-select');
    var settings_list = $('#settings-list');
    var visItems = "";

    $.ajax({
        type: 'GET',
        url: '/api/visualizers',
        success: function(data) {
            $.each(data.visualizers, function(i, visualization) {
                visItems += '<option>'+ visualization.name +'</option>';
            });
            vis_select.append(visItems)
            vis_select.change()
        }
    });

    vis_select.on('change', function() {
        var optionItems = "";
        var selected_vis = this.options[this.selectedIndex].text;
        settings_list.empty();
        $.ajax({
            type: 'GET',
            url: '/api/visualizers/' + selected_vis,
            success: function(data) {
                $.each(data.settings, function(setting, options) {
                    optionItems += '<li>' + setting + '<select class="form-control" id=' + setting + '-setting></select></li>';
                });
                settings_list.append(optionItems);
            }
        });
    });
});
