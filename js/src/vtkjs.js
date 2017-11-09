// var devel=1;
var devel=0;
var widgets = require('jupyter-js-widgets');
var _ = require('underscore');

// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//
//  when different from the base class.

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
var VtkJsModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
	_model_name : 'VtkJsModel',
	_view_name : 'VtkJsView',
	_model_module : 'ipywe',
	_view_module : 'ipywe',
	_model_module_version : '0.1.0',
	_view_module_version : '0.1.0',
	value : 'Hello World'
    })
});


// Custom View. Renders the widget model.
var VtkJsView = widgets.DOMWidgetView.extend({
    render: function() {
        var widget_area = $('<div>');
        this.$el.append(widget_area);
        var container = widget_area.get(0);

        $.getScript('https://unpkg.com/vtk.js').done(function(){
            var renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
            var renderer = vtk.Rendering.Core.vtkRenderer.newInstance({ background: [0.2, 0.3, 0.4] });
            renderWindow.addRenderer(renderer);

            // var fullScreenRenderer = vtk.Rendering.Core.vtkRenderWindow.newInstance();
            var actor              = vtk.Rendering.Core.vtkActor.newInstance();
            var mapper             = vtk.Rendering.Core.vtkMapper.newInstance();
            var cone               = vtk.Filters.Sources.vtkConeSource.newInstance();
            actor.setMapper(mapper);
            mapper.setInputConnection(cone.getOutputPort());
            renderer.addActor(actor);
            renderer.resetCamera();

            // Sources/Rendering/OpenGL/RenderWindow

            var openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
            renderWindow.addView(openglRenderWindow);

            openglRenderWindow.setContainer(container);

            renderWindow.render();

            var interactor =     vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
            interactor.setView(openglRenderWindow);
            interactor.initialize();
            interactor.bindEvents(container);
        });
    }
});


module.exports = {
    VtkJsModel : VtkJsModel,
    VtkJsView : VtkJsView
};
