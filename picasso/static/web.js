$("document").ready(function() {

    var select_vis = $('#select_vis');
    var div_settings_list = $('#div_settings_list');
    var button_visualize = $('#button_visualize');
    var input_file_upload = $('#input_file_upload');

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

    function postFile(event) {
        return $.ajax({
            type: 'POST',
            url: '/api/images',
            data: new FormData($('form')[0]),
            cache: false,
            contentType: false,
            processData: false,
            success: function(data) {
                console.log(data)
            },
            error: function(err) {
                console.log(err),
                alert('error: ('+ err.status + ') ' + err.statusText)
            },
        });
    }

    function loadVisualizerSettings(visualizerSettings) {
        var settingItems = '';
        $.each(visualizerSettings, function(setting, options) {
            settingItems += setting + '<select class="form-control" id=' + setting + '-setting></select>';
        });
        div_settings_list.append(settingItems);
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
        select_vis.append(visItems)
        select_vis.change()
    });

    select_vis.on('change', function() {
        var selected_vis = this.options[this.selectedIndex].text;
        var visualizerSettings;
        div_settings_list.empty();
        getVisualizerSettings(selected_vis).done(function(data) {
            selected_vis_settings = data.settings;
            loadVisualizerSettings(selected_vis_settings);
            loadVisualizerOptions(selected_vis_settings);
        });
    });

    button_visualize.on('click', function() {
        postFile().done(function(data) {
            // do something when done
        })
    })
});
