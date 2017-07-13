require.undef("imgdatagraph");


define("imgdatagraph", ["jupyter-js-widgets"], function(widgets) {

    var ImgDataGraphView = widgets.DOMWidgetView.extend({

        render: function() {
            var wid = this;

            var widget_area = $('<div class="flex-container">');
            
            widget_area.css("display", "-webkit-flex"); widget_area.css("display", "flex");
            widget_area.css("justifyContent", "flex-start"); widget_area.width(1000); widget_area.height(this.model.get("height") * 1.3);
            
            var img_vbox = $('<div class="flex-item-img img-box">');

            img_vbox.width(this.model.get("width") * 1.1); img_vbox.height(this.model.get("height") * 1.25); img_vbox.css("padding", "5px");

            var graph_vbox = $('<div class="flex-item-graph graph-box">');

            graph_vbox.width(1000 - this.model.get("width") * 1.1 - 25); graph_vbox.height(this.model.get("height") * 1.25); graph_vbox.css("padding", "5px");

            widget_area.append(img_vbox);
            widget_area.append(graph_vbox);

            this.$el.append(widget_area);

            var img_container = $('<div class="img-container">');
            img_vbox.append(img_container);
            img_container.width(this.model.get("width")); img_container.height(this.model.get("height"));

            var img = $('<img class="curr-img">');
            var image_src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value")
            img.attr("src", image_src);
            img_container.append(img);
            img.css("position", "absolute");
            img.width(this.model.get("width")); img.height(this.model.get("height"));

            var canvas = $('<canvas class="img-canvas">');
            canvas.prop({
                width: this.model.get("width"),
                height: this.model.get("height")
            });
            //canvas.width(this.model.get("width")); canvas.height(this.model.get("height"));
            canvas.css("position", "absolute");
            img_container.append(canvas);
            var can = canvas[0];
            var ctx = can.getContext('2d');
            console.log(ctx);

            var linewidth_label = $('<input class="lwidth-label" type="text" readonly style="border:0">');        
 
            var max_linewidth;
            if (this.model.get("width") < this.model.get("height")) {
                max_linewidth = this.model.get("width") / 4;
            }
            else {
                max_linewidth = this.model.get("height") / 4;
            }
            var width_slider = $('<div class="width-slider">');
            width_slider.slider({
                value: 1,
                min: 1,
                max: max_linewidth,
                slide: function(event, ui) {
                    linewidth_label.val("Line Width: " + ui.value + " px");
                    wid.model.set("_linepix_width", ui.value);
                    wid.touch();
                }
            });

            linewidth_label.val("Line Width: " + width_slider.slider("value") + " px");
            linewidth_label.width("40%");
            var width_slider_handle = width_slider.find(".ui-slider-handle");
            width_slider_handle.css("borderRadius", "50%");
            width_slider_handle.css("background", "#0099e6");
            width_slider.width(this.model.get("width"));
            width_slider.css({
                "marginLeft": "7px",
                "marginBottom": "5px",
                "marginTop": "20px"
            });
            
            img_vbox.append(width_slider);
            img_vbox.append(linewidth_label);

            var graph_button = $('<button class="graph-button">');
            graph_button.button({
                label: "Graph",
                disabled: false
            });
            graph_button.css("marginLeft", "10px");
            img_vbox.append(graph_button);
            graph_button.click(function() {
                var graph_val = wid.model.get("_graph_click");
                if (graph_val < Number.MAX_SAFE_INTEGER) {
                    graph_val++;
                }
                else {
                    graph_val = 0;
                }
                wid.model.set("_graph_click", graph_val);
                wid.touch();
                ctx.clearRect(0, 0, wid.model.get("width"), wid.model.get("height"));
            });

            img.on("dragstart", false);
            
            //For some reason, none of the canvas drawing code appears to work.
            canvas.on("mousedown", function(event) {
                console.log("mousedown");
                ctx.clearRect(0, 0, wid.model.get("width"), wid.model.get("height"));
                var offx = event.offsetX;
                var offy = event.offsetY;
                wid.model.set("_offsetX1", offx);
                wid.model.set("_offsetY1", offy);
                wid.touch();
                canvas.on("mousemove", function(event) {
                    console.log("mousemove");
                    ctx.clearRect(0, 0, wid.model.get("width"), wid.model.get("height"));
                    var currx = event.offsetX;
                    var curry = event.offsetY;
                    wid.model.set("_offsetX2", currx);
                    wid.model.set("_offsetY2", curry);
                    wid.touch();
                    ctx.beginPath();
                    ctx.moveTo(offx, offy);
                    ctx.lineTo(currx, curry);
                    ctx.lineWidth = wid.model.get("_linepix_width") + 1;
                    ctx.strokeStyle = "#ff0000";
                    ctx.stroke();
                }).on("mouseup", function(event) {
                    console.log("mouseup");
                    canvas.off("mousemove");
                });
            });

            var graph_img = $('<img class="graph-img">');
            var graph_src = "data:image/" + this.model.get("_format") + ";base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
            graph_img.attr("src", graph_src);
            graph_vbox.append(graph_img);
            graph_img.css("position", "absolute");
            //graph_img.height(this.model.get("height"));
            if (graph_vbox.width() <= graph_img.width()) {
                graph_img.width(graph_vbox.width() - 50);
            }

            this.model.on("change:_b64value", this.on_img_change, this);
            this.model.on("change:_graphb64", this.on_graph_change, this);
            this.model.on("change:_linepix_width", this.on_linewidth_change, this);
        },

        on_img_change: function() {
            var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value");
            this.$el.find(".curr-img").attr("src", src);
        },

        on_graph_change: function() {
            var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_graphb64");
            this.$el.find(".graph-img").attr("src", src);
        },

        on_linewidth_change: function() {
            var canvas = this.$el.find(".img-canvas")[0];
            var ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, this.model.get("width"), this.model.get("height"));
            ctx.beginPath();
            ctx.moveTo(this.model.get("_offsetX1"), this.model.get("_offsetY1"));
            ctx.lineTo(this.model.get("_offsetX2"), this.model.get("_offsetY2"));
            ctx.lineWidth = this.model.get("_linepix_width") + 1;
            ctx.strokeStyle = "#ff0000";
            ctx.stroke();
        }

    });

    return {
        ImgDataGraphView : ImgDataGraphView
    };

});
