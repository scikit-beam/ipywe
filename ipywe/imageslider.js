require.undef("imgslider");


define("imgslider", ["jupyter-js-widgets"], function(widgets) {

    var ImgSliderView = widgets.DOMWidgetView.extend({
	
        //Overrides the default render method to allow for custom widget creation
	
        render: function() {

            //Sets all the values needed for creating the sliders. wid is created to allow model values to be obtained in functions within this render function.
            var wid = this;
            var img_max = this.model.get("_series_max");
            var vrange_min = this.model.get("_img_min");
            var vrange_max = this.model.get("_img_max");
            var vrange_step = (vrange_max - vrange_min)/100;
            var vrange = [vrange_min, vrange_max];

            /*Creates the flexbox that will store the widget and the two flexitems that it will contain. Also formats all of them.
              img_vbox stores the image and the horizontal (Image Selector) slider.
              data_vbox stores the html text element (displays the XY coordinates of the mouse and that position's value) and the vertical (Z range) slider.*/

            var widget_area = $('<div class="flex-container">');
            
            widget_area.css("display", "-webkit-flex"); widget_area.css("display", "flex");
            widget_area.css("justifyContent", "flex-start"); widget_area.width(1000); widget_area.height(this.model.get("height") * 1.3);
            
            var img_vbox = $('<div class="flex-item-img img-box">');

            img_vbox.width(this.model.get("width") * 1.1); img_vbox.height(this.model.get("height") * 1.25); img_vbox.css("padding", "5px");

            var data_vbox = $('<div class="flex-item-data data-box">');

            data_vbox.width(1000 - this.model.get("width") * 1.1 - 25); data_vbox.height(this.model.get("height") * 1.25); data_vbox.css("padding", "5px");

            //Adds the img_vbox and data_vbox to the overall flexbox.

            widget_area.append(img_vbox);
            widget_area.append(data_vbox);

            //Adds the widget to the display area.
            this.$el.append(widget_area);

            //Add a container for the image and the selection box
            var img_container = $('<div class="img-container">');
            img_vbox.append(img_container);
            img_container.css({
                position: "relative",
                width: this.model.get("width"),
                height: this.model.get("height"),
                padding: "10px"
            });

            //Creates the image stored in the initial value of _b64value and adds it to img_vbox.
            var img = $('<img class="curr-img">');
            var image_src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value")
            img.attr("src", image_src);
            
            img.width(this.model.get("width")); img.height(this.model.get("height"));
            img_container.append(img);

            //Creates a read-only input field with no border to dynamically display the value of the horizontal slider.
            var hslide_label = $('<input class="hslabel" type="text" readonly style="border:0">'); 
            //Creates the horizontal slider using JQuery UI
            var hslide_html = $('<div class="hslider">');
            hslide_html.slider({
                value: 0,
                min: 0,
                max: img_max,
                /*When the handle slides, this function is called to update hslide_label 
                  and change img_index on the backend (triggers the update_image function on the backend)*/
                slide: function(event, ui) {
                    hslide_label.val( ui.value );
                    console.log("Executed!");
                    wid.model.set("img_index", ui.value);
                    wid.touch();
                }
            });
            
            //Sets the label's initial value to the initial value of the slider and adds a left margin to the label
            hslide_label.val(hslide_html.slider("value"));
            hslide_label.css("marginLeft", "7px");
            hslide_label.width("15%");
            //Makes the slider's handle a blue circle and adds a 10 pixel margin to the slider
            var hslide_handle = hslide_html.find(".ui-slider-handle");
            hslide_handle.css("borderRadius", "50%");
            hslide_handle.css("background", "#0099e6");
            hslide_html.css("margin", "10px");
            hslide_html.css("marginBottom", "5px");
            hslide_html.css("marginTop", "20px");
            //Adds hslide_html (the slider) and hslide_label (the label) to img_vbox
            img_vbox.append(hslide_html);
            img_vbox.append(hslide_label);

            //Creates a zoom button, a zoom all button, and a reset button after the label
            var zoom_button = $('<button class="zoom-button">');
            zoom_button.button({
                label: "Zoom",
                disabled: false
            });
            zoom_button.css("margin", "10px");
            img_vbox.append(zoom_button);
            zoom_button.click(function() {
                var zoom_val = wid.model.get("_zoom_click");
                if (zoom_val < Number.MAX_SAFE_INTEGER) {
                    zoom_val++;
                }
                else {
                    zoom_val = 0;
                }
                wid.model.set("_zoom_click", zoom_val);
                wid.touch();
                select.remove();
                console.log("Zoomed");
            });

            var zoomall_button = $('<button class="zoom-button">');
            zoomall_button.button({
                label: "Zoom All",
                disabled: false
            });
            zoomall_button.css("margin", "10px");
            img_vbox.append(zoomall_button);
            zoomall_button.click(function() {
                var zoomall_val = wid.model.get("_zoomall_click");
                if (zoomall_val < Number.MAX_SAFE_INTEGER) {
                    zoomall_val++;
                }
                else {
                    zoomall_val = 0;
                }
                wid.model.set("_zoomall_click", zoomall_val);
                wid.touch();
                select.remove();
                console.log("All images zoomed");
            });

            var reset_button = $('<button class="reset-button">')
            reset_button.button({
                label: "Reset",
                disabled: false
            });
            reset_button.css("margin", "10px");
            img_vbox.append(reset_button);
            reset_button.click(function() {
                var reset_val = wid.model.get("_reset_click");
                if (reset_val < Number.MAX_SAFE_INTEGER) {
                    reset_val++;
                }
                else {
                    reset_val = 0;
                }
                wid.model.set("_reset_click", reset_val);
                wid.touch();
                select.remove();
                console.log("Image reset");
            });

            //Adds the selection box and changes its size as the mouse moves over the image
            var select = $('<div class="selection-box">');

            img.on("dragstart", false);

            img_container.on("mousedown", function(event) {
                console.log("Click 1");
                var click_x = event.offsetX;
                var click_y = event.offsetY;
                
                select.css({
                    "top": click_y,
                    "left": click_x,
                    "width": 0,
                    "height": 0,
                    "position": "absolute",
                    "pointerEvents": "none"
                });
                
                select.appendTo(img_container);

                img_container.on("mousemove", function(event) {
                    console.log("Mouse moving");
                    var move_x = event.offsetX;
                    var move_y = event.offsetY;
                    var width = Math.abs(move_x - click_x);
                    var height = Math.abs(move_y - click_y);
                    var new_x, new_y;

                    new_x = (move_x < click_x) ? (click_x - width) : click_x;
                    new_y = (move_y < click_y) ? (click_y - height) : click_y;

                    select.css({
                        "width": width - 1,
                        "height": height - 1,
                        "top": new_y,
                        "left": new_x,
                        "background": "transparent",
                        "border": "2px solid red"
                    });

                    wid.model.set("_offXtop", parseInt(select.css("left"), 10));
                    wid.model.set("_offYtop", parseInt(select.css("top"), 10));
                    wid.model.set("_offXbottom", parseInt(select.css("left"), 10) + select.width());
                    wid.model.set("_offYbottom", parseInt(select.css("top"), 10) + select.height());
                    wid.touch();

                }).on("mouseup", function(event) {
                    console.log("Click 2");
                    img_container.off("mousemove");
                });
            });

            console.log(img_vbox);
            console.log("done with img box");

            //Creates the fields (divs and spans) for the current mouse position and that position's value and adds them to data_vbox.
            var text_content = $('<div class="widget-html-content">');
            var xy = $("<div>"); xy.text("X,Y: ");
            var x_coord = $('<span class="img-offsetx">');
            var y_coord = $('<span class="img-offsety">');
            xy.append(x_coord); xy.append(", "); xy.append(y_coord);
            var value = $("<div>"); value.text("Value: ");
            var val = $('<span class="img-value">');
            value.append(val);
            text_content.append(xy); text_content.append(value);
            data_vbox.append(text_content);
            console.log(data_vbox);
            
            //Creates the label for the vertical slider with a static value of "Z range" (done in the same way as the other label)
            var vslide_label = $('<input class="vslabel" type="text" readonly style="border:0">');
            vslide_label.val("Z range");
            vslide_label.css("marginTop", "10px");
            vslide_label.css("marginBottom", "10px");
            //Creates the vertical slider using JQuery UI
            var vslide_html = $('<div class="vslider">');
            vslide_html.slider({
                range: true,
                orientation: "vertical",
                min: vrange_min,
                max: vrange_max,
                values: vrange,
                step: vrange_step,
                /*When either handle slides, this function sets _img_min and/or _img_max on the backend to the handles' values.
                  This triggers the update_image function on the backend.*/
                slide: function(event, ui) {
                    wid.model.set("_img_min", ui.values[0]);
                    wid.model.set("_img_max", ui.values[1]);
                    wid.touch();
                }
            });

            
            //Explicitly sets the slider's background color to white. Also, changes the handles to blue circles
            var vslide_bar = vslide_html.find(".ui-widget-header");
            vslide_bar.css("background", "#ffffff");
            vslide_bar.siblings().css("borderRadius", "50%");
            vslide_bar.siblings().css("background", "#0099e6");
            //Adds vslide_label and vslide_html to data_vbox. At this point, the widget can be successfully displayed.
            vslide_html.height(this.model.get("height") * 0.75);
            data_vbox.append(vslide_label);
            data_vbox.append(vslide_html);
            console.log(data_vbox);
            console.log("done with data box");

            
            /*This function sets _offsetX and _offsetY on the backend to the event-specific offset values whenever
              the mouse moves over the image. It then calculates the data-based XY coordinates and displays them
              in the x_coord and y_coord span fields.*/
            img.mousemove(function(event){
                wid.model.set("_offsetX", event.offsetX);
                wid.model.set("_offsetY", event.offsetY);
                wid.touch();
                x_coord.text(Math.floor(event.offsetX*1./(wid.model.get("width"))*(wid.model.get("_ncols"))));
                y_coord.text(Math.floor(event.offsetY*1./(wid.model.get("height"))*(wid.model.get("_nrows"))));
            });

            //Triggers on_pixval_change and on_img_change when the backend values of _pix_val and _b64value change.
            this.model.on("change:_pix_val", this.on_pixval_change, this);
            this.model.on("change:_b64value", this.on_img_change, this);
        },

        /*If there is no custom error message, this function sets the value of the img-value span field to
          the value of _pix_val from the backend. Otherwise, it sets the value of this field to the value of
          err (the error message).*/

        on_pixval_change: function() {
            console.log("Executing on_pixval_change");
            if (this.model.get("_err") == "") {
                this.$el.find(".img-value").text(this.model.get("_pix_val"));
            }
            else {
                this.$el.find(".img-value").text(this.model.get("_err"));
            }
        },

        /*When _b64value changes on the backend, this function creates a new source string for the image (based
          on the new value of _b64value). This new source then replaces the old source of the image.*/

        on_img_change: function() {
            console.log("Executing on_img_change");
            var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value");
            this.$el.find(".curr-img").attr("src", src);
        }
	
    });


    //Allows the widget to be rendered
    return {
        ImgSliderView : ImgSliderView
    };

});
