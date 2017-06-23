require.undef("imgdisplay");

define("imgdisplay", ["jupyter-js-widgets"], function(widgets) {

    var ImgDisplayView = widgets.DOMWidgetView.extend({
    
        render: function() {
            var wid = this;
            
            var img = $('<img class="curr-img">');
            var image_src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value")
            img.attr("src", image_src);
            img.width(this.model.get("width")); img.height(this.model.get("height"));
            this.$el.append(img);

            var select = $('<div class="selection-box">');

            img.on("mousedown", function(event) {
                var click_x = event.pageX;
                var click_y = event.pageY;
                
                select.css({
                    "top": click_y,
                    "left": click_x,
                    "width": 0,
                    "height": 0
                });
                
                img.append(select);

                img.on("mousemove", function(event) {
                    var move_x = event.pageX;
                    var move_y = event.pageY;
                    var width = Math.abs(move_x - click_x);
                    var height = Math.abs(move_y - click_y);
                    var new_x, new_y;

                    new_x = (move_x < click_x) ? (click_x - width) : click_x;
                    new_y = (move_y < click_y) ? (click_y - height) : click_y;

                    select.css({
                        "width": width,
                        "height": height,
                        "top": new_y,
                        "left": new_x
                    });

                    this.model.set("_offXtop", select.button("option", "left");
                    this.model.set("_offYtop", select.button("option", "top");
                    this.model.set("_offXbottom", select.button("option", "left") + select.button("option", "width"));
                    this.model.set("_offYbottom", select.button("option", "top") + select.button("option", "height"));
                    this.touch();

                }).on("mouseup", function(event) {
                    img.off("mousemove");
                });
            });
            
            var zoom_button = $('<button class="zoom-button">');
            zoom_button.button({
                label: "Zoom",
                disabled: false
            });
            zoom_button.click(function() {
                trigger_val = wid.model.get("_button_click");
                if (trigger_val < Number.MAX_SAFE_INTEGER - 1) {
                    trigger_val++;
                }
                else {
                    trigger_val = 0;
                }
                this.model.set("_button_click", trigger_val);
                this.touch();
            });
            this.model.on("change:_b64value", this.on_img_change, this);
        },

        on_img_change: function() {
            var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value");
            this.$el.find(".curr-img").attr("src", src);
        }

    });

    render {
        ImgDisplayView : ImgDisplayView
    };

});
