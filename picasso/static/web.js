$("document").ready(function() {

    var vis_select = $('#vis-select');
    var settings_list = $('#settings-list');
    var visItems = "";

    function getVisualizers() {
        return $.ajax({
            type: 'GET',
            url: '/api/visualizers',
        });
    }

    function getVisualizerSettings(visualizer) {
        return $.ajax({
            type: 'GET',
            url: '/api/visualizers/' + visualizer,
        });
    }

    getVisualizers().done(function(data) {
        $.each(data.visualizers, function(i, visualization) {
            visItems += '<option>'+ visualization.name +'</option>';
        });
        vis_select.append(visItems)
        vis_select.change()
    });


    vis_select.on('change', function() {
        var optionItems = "";
        var selected_vis = this.options[this.selectedIndex].text;
        settings_list.empty();
        getVisualizerSettings(selected_vis).done(function(data) {
            $.each(data.settings, function(setting, options) {
                optionItems += '<li>' + setting + '<select class="form-control" id=' + setting + '-setting></select></li>';
            });
            settings_list.append(optionItems);

        });
    });
});
