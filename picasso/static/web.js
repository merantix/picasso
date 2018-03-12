/**
 * Copyright (c) 2017 Merantix GmbH
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Jan Steinke - Restful API
 */
$("document").ready(function() {

    var select_vis = $('#select_vis');
    var div_settings_list = $('#div_settings_list');
    var button_visualize = $('#button_visualize');
    var input_file_upload = $('#input_file_upload');
    var tbody_results = $('#results');
    var tr_text_results = $('#text-results');
    var tr_image_results = $('#image-results');
    var a_appstate_title = $('#appstate_title');
    var div_appstate_backend = $('#appstate_backend');
    var div_appstate_checkpoint = $('#appstate_checkpoint');
    var div_appstate_update = $('#appstate_update');

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

    function getAppState() {
        return $.ajax({
            type: 'GET',
            url: '/api/app_state',
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

    function getVisualize(image_uid) {
        data = {
                image: image_uid,
                visualizer: select_vis[0].options[select_vis[0].selectedIndex].text
            },
        $.each(div_settings_list[0].getElementsByClassName('vizSetting'), function(i, j) {
            data[j.name] = j.options[j.selectedIndex].text
        })
        return $.ajax({
            type: 'GET',
            url: '/api/visualize',
            data: $.param(data),
            cache: false,
            contentType: false,
            processData: false,
            success: function(data) {
                tr_text_results.empty();
                tr_image_results.empty();
                tr_image_results.append('<td align="center"><img src="/api/inputs/'+ data.input_file_name+'" style="width:244px;height:244px;"/></td>');
                if (data.has_processed_input) {
                    tr_image_results.append('<td align="center"><img src="/api/outputs/'+ data.processed_input_file_name+'" style="width:244px;height:244px;"/></td>');
                }
                if (data.has_output) {
                    $.each(data.output_file_names, function(i, j) {
                        tr_image_results.append('<td align="center"><img src="/api/outputs/'+ j +'" style="width:244px;height:244px;"/></td>');
                    })
                }
                tr_text_results.append('<td align="center"><b>'+ data.input_file_name +'</b></td>')
                if (data.has_processed_input) {
                    tr_text_results.append('<td align="center"><b>Processed Image</b></td>')
                }
                $.each(data.predict_probs, function(i, j) {
                    tr_text_results.append('<td align="center"><b>'+ j.name + ': ' + j.prob +'</b></td>');
                })
                console.log(data)
            },
            error: function(err) {
                console.log(err),
                alert('error: ('+ err.status + ') ' + err.statusText)
            },
        })
    }

    function loadVisualizerSettings(visualizerSettings) {
        var settingItems = '';
        $.each(visualizerSettings, function(setting, options) {
            settingItems += setting + '<select name="'+setting+'" class="form-control vizSetting" id=' + setting + '-setting></select>';
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

    getAppState().done(function(data) {
        a_appstate_title.text(data.app_title)
        div_appstate_backend.text(data.model_name)
        div_appstate_checkpoint.text(data.latest_ckpt_name)
        div_appstate_update.text(data.latest_ckpt_time)
    })

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
            getVisualize(data.uid);
        })
    })
});
