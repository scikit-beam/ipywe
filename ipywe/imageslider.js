require.undef("imgslider");


define("imgslider", ["jupyter-js-widgets"], function(widgets) {

    var ImgSliderView = widgets.DOMWidgetView.extend({
	
        //Overrides the default render method to allow for custom widget creation
	
        render: function() {

            //Sets all the values needed for creating the sliders. wid is created to allow model values to be obtained in functions within this render function.
            var wid = this;
            var img_max = this.model.get("series_max");
            var vrange_min = this.model.get("img_min");
            var vrange_max = this.model.get("img_max");
            var vrange_step = (vrange_max - vrange_min)/100;
            var vrange = [vrange_min, vrange_max];

            /*Creates the flexbox that will store the widget and the two flexitems that it will contain.
              img_vbox stores the image and the horizontal (Image Selector) slider.
              data_vbox stores the html text element (displays the XY coordinates of the mouse and that position's value) and the vertical (Z range) slider.*/

            var widget_area = $("<div>"); widget_area.addClass("flex-container");
            var img_vbox = $("<div>"); img_vbox.addClass("flex-item-img img-box");
            var data_vbox = $("<div>"); data_vbox.addClass("flex-item-data data-box");

            //Adds the img_vbox and data_vbox to the overall flexbox.

            widget_area.append(img_vbox);
            widget_area.append(data_vbox);

            //Adds the widget to the display area.
            this.$el.append(widget_area);

            //Creates the image stored in the initial value of _b64value and adds it to img_vbox.
            var img = $("<img>");
            var image_src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value")
            img.attr("src", image_src);
            img.addClass("curr-img");
            img.css("margin", "10px");
            img.width(this.model.get("width")); img.height(this.model.get("height"));
            img_vbox.append(img);

            //Creates a read-only input field with no border to dynamically display the value of the horizontal slider.
            var hslide_label = $('<input type="text" readonly style="border:0">'); 
            hslide_label.attr("id", "hslabel");
            //Creates the horizontal slider using JQuery UI
            var hslide_html = $('<div>'); hslide_html.addClass("hslider");
            hslide_html.slider({
                value: 0,
                min: 0,
                max: img_max,
                /*When the handle slides, this function is called to update hslide_label 
                  and change img_change_trig on the backend (triggers the update_image function on the backend)*/
                slide: function(event, ui) {
                    hslide_label.val( ui.value );
                    console.log("Executed!");
                    wid.model.set("img_change_trig", ui.value);
                    wid.touch();
                }
            });
            
            //Sets the label's initial value to the initial value of the slider
            hslide_label.val(hslide_html.slider("value"));
            //Adds hslide_html (the slider) and hslide_label (the label) to img_vbox
            img_vbox.append(hslide_html);
            img_vbox.append(hslide_label);

            console.log(img_vbox);
            console.log("done with img box");

            //Creates the fields (divs and spans) for the current mouse position and that position's value and adds them to data_vbox.
            var text_content = $("<div>"); text_content.addClass("widget-html-content");
            var xy = $("<div>"); xy.text("X,Y: ");
            var x_coord = $("<span>"); x_coord.addClass("img-offsetx");
            var y_coord = $("<span>"); y_coord.addClass("img-offsety");
            xy.append(x_coord); xy.append(", "); xy.append(y_coord);
            var value = $("<div>"); value.text("Value: ");
            var val = $("<span>"); val.addClass("img-value");
            value.append(val);
            text_content.append(xy); text_content.append(value);
            data_vbox.append(text_content);
            console.log(data_vbox);
            
            //Creates the label for the vertical slider with a static value of "Z range" (done in the same way as the other label)
            var vslide_label = $('<input type="text" readonly style="border:0">'); vslide_label.attr("id", "vs-label");
            vslide_label.val("\n\nZ range");
            vslide_label.css("paddingBottom", "10px");
            //Creates the vertical slider using JQuery UI
            var vslide_html = $("<div>"); vslide_html.addClass("vslider");
            vslide_html.slider({
                range: true,
                orientation: "vertical",
                min: vrange_min,
                max: vrange_max,
                values: vrange,
                step: vrange_step,
                /*When either handle slides, this function sets img_min and/or img_max on the backend to the handles' values.
                  This triggers the update_image function on the backend.*/
                slide: function(event, ui) {
                    wid.model.set("img_min", ui.values[0]);
                    wid.model.set("img_max", ui.values[1]);
                    wid.touch();
                }
            });

            
            //Adds vslide_label and vslide_html to data_vbox. At this point, the widget can be successfully displayed.
            vslide_html.height(this.model.get("height") * 0.75);
            data_vbox.append(vslide_label);
            data_vbox.append(vslide_html);
            console.log(data_vbox);
            console.log("done with data box");

            
            /*This function sets offsetX and offsetY on the backend to the event-specific offset values whenever
              the mouse moves over the image. It then calculates the data-based XY coordinates and displays them
              in the x_coord and y_coord span fields.*/
            img.mousemove(function(event){
                wid.model.set("offsetX", event.offsetX);
                wid.model.set("offsetY", event.offsetY);
                wid.touch();
                x_coord.text(Math.floor(event.offsetX*1./(wid.model.get("width"))*(wid.model.get("ncols"))));
                y_coord.text(Math.floor(event.offsetY*1./(wid.model.get("height"))*(wid.model.get("nrows"))));
            });

            //Triggers on_pixval_change and on_img_change when the backend values of pix_val and _b64value change.
            this.model.on("change:pix_val", this.on_pixval_change, this);
            this.model.on("change:_b64value", this.on_img_change, this);
        },

        /*If there is no custom error message, this function sets the value of the img-value span field to
          the value of pix_val from the backend. Otherwise, it sets the value of this field to the value of
          err (the error message).*/

        on_pixval_change: function() {
            console.log("Executing on_pixval_change");
            if (this.model.get("err") == "") {
                this.$el.find(".img-value").text(this.model.get("pix_val"));
            }
            else {
                this.$el.children(".img-value").text(this.model.get("err"));
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
