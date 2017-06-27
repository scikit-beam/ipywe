require.undef("imgdisplay");

define("imgdisplay", ["jupyter-js-widgets"], function(widgets) {

    var ImgDisplayView = widgets.DOMWidgetView.extend({
    
        render: function() {
            var wid = this;

            var img_container = $('<div class="img-container">');
            this.$el.append(img_container);
            img_container.css({
                position: "relative",
                width: this.model.get("width"),
                height: this.model.get("height")
            });
            
            var img = $('<img class="curr-img">');
            var image_src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value")
            img.attr("src", image_src);
            img.width(this.model.get("width")); img.height(this.model.get("height"));
            img_container.append(img);
            //this.$el.append(img);

            var zoom_button = $('<button class="zoom-button">');
            zoom_button.button({
                label: "Zoom",
                disabled: false
            });
            zoom_button.css("margin", "10px");
            zoom_button.css("marginLeft", "0px");
            this.$el.append(zoom_button);
            zoom_button.click(function() {
                var zoom_val = wid.model.get("_zoom_click");
                if (zoom_val < Number.MAX_SAFE_INTEGER - 1) {
                    zoom_val++;
                }
                else {
                    zoom_val = 0;
                }
                wid.model.set("_zoom_click", zoom_val);
                wid.touch();
                select.remove();
                console.log("Select removed");
            });

            var reset_button = $('<button class="reset-button">')
            reset_button.button({
                label: "Reset",
                disabled: false
            });
            reset_button.css("margin", "10px");
            this.$el.append(reset_button);
            reset_button.click(function() {
                var reset_val = wid.model.get("_reset_click");
                if (reset_val < Number.MAX_SAFE_INTEGER - 1) {
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

            var select = $('<div class="selection-box">');

            img.on("dragstart", false);

            img.on("mousedown", function(event) {
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

                img.on("mousemove", function(event) {
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
                    img.off("mousemove");
                });
            });
            
            this.model.on("change:_b64value", this.on_img_change, this);
        },

        on_img_change: function() {
            var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value");
            this.$el.find(".curr-img").attr("src", src);
        }

    });

    return {
        ImgDisplayView : ImgDisplayView
    };

});
