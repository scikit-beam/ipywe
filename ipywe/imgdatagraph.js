require.undef("imgdatagraph");


define("imgdatagraph", ["jupyter-js-widgets"], function(widgets) {

    var ImgDataGraphView = widgets.DOMWidgetView.extend({

        render: function() {
            var wid = this;

            var img_container = $('<div class="img-container">');
            this.$el.append(img_container);
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
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = "#ff0000";
                    ctx.stroke();
                }).on("mouseup", function(event) {
                    console.log("mouseup");
                    canvas.off("mousemove");
                });
            });

            var graph_button = $('<button class="graph-button">');
            graph_button.button({
                label: "Graph",
                disabled: false
            });
            this.$el.append(graph_button);
            graph_button.css("margin", "10px");
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
            this.model.on("change:_b64value", this.on_img_change, this);
        },

        on_img_change: function() {
            var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value");
            this.$el.find(".curr-img").attr("src", src);
        }

    });

    return {
        ImgDataGraphView : ImgDataGraphView
    };

});
