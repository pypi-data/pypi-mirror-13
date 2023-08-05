(function (){
    function new_event_sources(event){
        /*
         * Callback when a new_event_sources SSE event is received.
         * This function must update the sources event section in the web page
         */
        function print(event_name){
            /*
             * Auxiliary function used as callback in the addEventListener
             * method of the SSE data pipe.
             */
            return function(data){
                var msg = "<p>" +
                              "<strong>" + event_name + "</strong>: " +
                              pretty(JSON.parse(data.data), 0, true) +
                          "</p>";
                $('#source-' + event_name).html(msg);
            };
        };

        var obj = JSON.parse(event.data),
            events_removed = obj.removed,
            events_added = obj.added,
            device_selector = document.getElementById("device"),
            id = device_selector.value;

        // Unbind and delete a source event callback if it's in the removed list
        for(var i = 0; i < events_removed.length; i++){
            if(id !== "----"){
                var event_source = get_complete_event_name(events_removed[i]);
                unbind_event_source(event_source);
            }
            delete event_sources_callbacks[events_removed[i]];
        }

        // Construct and bind a source event callback if it's in the added list
        for(var i = 0; i < events_added.length; i++){
            var cb = print(events_added[i]);
            event_sources_callbacks[events_added[i]] = cb;
            if(id !== "----"){
                var event_source = get_complete_event_name(events_added[i]);
                bind_event_source(event_source);
            }
        }
    };

    function bind_event_source(event_source){
        /*
         * Connect the event_source to the callback registered in the
         * event_sources_callbacks object.
         */
        var father = $('.event-sources');
        var event_name = get_event_name(event_source);
        father.append('<div id="source-' + event_name + '"></div>');
        var cb = event_sources_callbacks[event_name];
        lupulo_controller.data_pipe.addEventListener(event_source, cb);
    };

    function unbind_event_source(event_source){
        /*
         * Disconnect the event_source from the callback registered in the
         * event_sources_callbacks object.
         */
        var event_name = get_event_name(event_source);
        $('#source-' + event_name).remove();
        var cb = event_sources_callbacks[event_name];
        lupulo_controller.data_pipe.removeEventListener(event_source, cb);
    };

    function update_data_panels(widget_name){
        /*
         * Closure to inject the widget_name argument
         */
        return function(event){
            /*
             * Callback that updates the data and accessors panels with
             * the data received from the backend.
             */
            var event_name = get_event_name(event.type);
            var panel = $('#' + widget_name + '-wrapper .data-panel');
            var accessors_panel = $('#' + widget_name + '-wrapper .accessors-panel');

            var obj = data_panel_objects[widget_name];
            obj[event_name] = JSON.parse(event.data);

            panel.html(pretty(obj, 0, true));

            obj = {};
            var widget_accessors = accessors[widget_name];
            for(var accessor_index in widget_accessors){
                var jdata = JSON.parse(event.data);
                var fdata = {};
                fdata[event.type] = jdata;
                var accessor = widget_accessors[accessor_index];
                obj[accessor_index] = accessor(fdata);
            }
            accessors_panel.html(pretty(obj, 0, true));
        };
    };

    function new_widgets(event){
        /*
         * Callback for the new_widget event source from the backend.
         * It creates all the sections for each layout definition and call the
         * lupulo controller to bind the widgets to its anchor.
         */
        var obj = JSON.parse(event.data),
            pathname = location.pathname.split('/'),
            widget_url = pathname[pathname.length-1],
            widgets_removed = [],
            widgets_added = [];

        // Delete the callbacks if the object is in the removed section
        if('removed' in obj){
            for(var i = 0; i < obj.removed.length; i++){
                var event_source = get_complete_event_name(obj.removed[i]);
                var cb = data_panel_callbacks[obj.removed[i]];
                lupulo_controller.data_pipe.removeEventListener(event_source, cb);
            }
        }

        // Construct all the html code, populate the data_panel_ objects and
        // connects the callbacks to its event sources if the id is a valid one
        var added_widgets = {};
        if('added' in obj){
            for(var name in obj.added){
                if(!(name in lupulo_controller.widgets) &&
                   ((pathname.length === 2) || (widget_url === name))){
                    added_widgets[name] = obj.added[name];
                    var anchor = obj.added[name].anchor.slice(1)
                    var layout = pretty(obj.added[name], 0, false);
                    var child = '<div class="clearfix wrapper" id="' + name + '-wrapper">' +
                                    '<div class="pull-left">' +
                                        '<pre class="section layout">' +
                                            '<div class="title">Layout</div>' +
                                            layout +
                                        '</pre>' +
                                        '<div class="section">' +
                                            '<div class="title">Raw data</div>' +
                                            '<pre class="data-panel">{}</pre>' +
                                        '</div>' +
                                        '<div class="section">' +
                                            '<div class="title">Accessors data</div>' +
                                            '<pre class="accessors-panel"></pre>' +
                                        '</div>' +
                                    '</div>' +
                                    '<div class="pull-left widget" id="' + anchor + '">' +
                                        '<div class="title">Widget</div>' +
                                    '</div>' +
                                '</div>';
                    $('.widgets').append(child);
                    var cb = update_data_panels(name);
                    data_panel_objects[name] = {};
                    data_panel_callbacks[name] = cb;
                    data_panel_events[name] = obj.added[name].event_names;
                    accessors[name] = get_accessors(obj.added[name].accessors);

                    var id = device_selector.value;
                    if(id !== '----'){
                        var events = data_panel_events[name];
                        for(var i = 0; i < events.length; i++){
                            var event_source = get_complete_event_name(events[i]);
                            lupulo_controller.data_pipe.addEventListener(event_source ,cb);
                        }
                    }
                }
            }
        }

        if('changed' in obj){
            for(var name in obj.changed){
                var layout = pretty(obj.changed[name], 0, false);
                var layout_dom = $('#' + name + '-wrapper .layout');
                layout_dom.html('<div class="title">Layout</div>' + layout);
            }
        }

        obj.added = added_widgets;
        new_event = jQuery.extend(true, {}, event);
        new_event.data = JSON.stringify(obj);
        // Call the lupulo_controller callback
        lupulo_controller.new_widgets(new_event);

        // Remove all the wrapper when the widget has been already deleted by
        // the lupulo controller
        if('removed' in obj){
            for(var i = 0; i < obj.removed.length; i++){
                $('#' + obj.removed[i] + '-wrapper').remove();
            }
        }

    };

    var old_id = '----',
        // Callback for the event sources section
        event_sources_callbacks = {},
        // Data for the data panels sections
        data_panel_callbacks = {},
        data_panel_events = {},
        data_panel_objects = {},
        accessors = {};

    // Overwrite the default callback for the device selector
    var device_selector = document.getElementById("device");
    device_selector.addEventListener("change", function(event){
        var id = device_selector.value;

        event.target.stable_value = event.target.value;
        // Update the event sources section accordingly
        for(var event_name in event_sources_callbacks){
            if(id === '----'){
                if(old_id !== "----"){
                    var event_source = 'id' + old_id + '-' + event_name;
                    unbind_event_source(event_source);
                }
            }else{
                if(old_id !== "----"){
                    var old_event_source = 'id' + old_id + '-' + event_name;
                    unbind_event_source(old_event_source);
                }
                var event_source = get_complete_event_name(event_name);
                bind_event_source(event_source);
            }
        }

        // Update the data panels accordingly
        for(var widget_name in data_panel_callbacks){
            // Clear the text of both panels
            $('#' + widget_name +'-wrapper .data-panel').text("{}");
            $('#' + widget_name +'-wrapper .accessors-panel').text("");

            var events = data_panel_events[widget_name];
            if(id === '----'){
                if(old_id !== "----"){
                    for(var i = 0; i < events.length; i++){
                        var event_source = 'id' + old_id + '-' + events[i];
                        var cb = data_panel_callbacks[widget_name];
                        lupulo_controller.data_pipe.removeEventListener(event_source, cb)
                    }
                }
            }else{
                for(var i = 0; i < events.length; i++){
                    var cb = data_panel_callbacks[widget_name];

                    if(old_id !== "----"){
                        var old_event_source = 'id' + old_id + '-' + events[i];
                        lupulo_controller.data_pipe.removeEventListener(old_event_source , cb);
                    }

                    var event_source = get_complete_event_name(events[i]);
                    lupulo_controller.data_pipe.addEventListener(event_source ,cb);
                }
            }
        }

        // Do the job of the lupulo_controller callback
        for(var name in lupulo_controller.widgets){
            widget = lupulo_controller.widgets[name];
            widget.clear_framebuffers();
            lupulo_controller.remove_widget(name);
            lupulo_controller.add_widget(widget);
        }

        // Update the old_id
        old_id = id;
    });

    // Overwrite some callbacks of the main controller
    lupulo_controller = new DefaultController();
    lupulo_controller.setup();
    lupulo_controller.data_pipe.addEventListener("new_widgets", new_widgets);
    lupulo_controller.data_pipe.addEventListener("new_devices", lupulo_controller.new_devices);
    lupulo_controller.data_pipe.addEventListener("new_event_sources", new_event_sources);
})();
