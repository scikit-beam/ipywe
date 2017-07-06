require.undef("imgdatagraph");


define("imgdatagraph", ["jupyter-js-widgets"], function(widgets) {

    var ImgDataGraphView = widgets.DOMWidgetView.extend({

        render: function() {
            var img_container = $('<div class="img-container">');
            img_container.width(this.model.get("width")); img_container.height(this.model.get("height"));
            this.$el.append(img_container);

            
        },

    });

});
