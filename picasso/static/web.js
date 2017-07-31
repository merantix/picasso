$("document").ready(function() {

    var vis_select = $('#vis-select');
    var settings_list = $('#settings-list');

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

    function loadVisualizerSettings(visualizerSettings) {
        var settingItems = '';
        $.each(visualizerSettings, function(setting, options) {
            settingItems += setting + '<select class="form-control" id=' + setting + '-setting></select>';
        });
        settings_list.append(settingItems);
    }

    function loadVisualizerOptions(visualizerSettings) {
        $.each(visualizerSettings, function(setting, options) {
            var optionItems = '';
            $.each(options, function(i, option) {
                optionItems += '<option>'+ option + '</option>';
            })
            $('#'+setting+'-setting').append(optionItems);
        })
    }

    getVisualizers().done(function(data) {
        var visItems = "";
        $.each(data.visualizers, function(i, visualization) {
            visItems += '<option>'+ visualization.name +'</option>';
        });
        vis_select.append(visItems)
        vis_select.change()
    });

    vis_select.on('change', function() {
        var selected_vis = this.options[this.selectedIndex].text;
        var visualizerSettings;
        settings_list.empty();
        getVisualizerSettings(selected_vis).done(function(data) {
            selected_vis_settings = data.settings;
            loadVisualizerSettings(selected_vis_settings);
            loadVisualizerOptions(selected_vis_settings);
        });
    });
});
