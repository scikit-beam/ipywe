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
            // var actor              = vtk.Rendering.Core.vtkActor.newInstance();
            // var mapper             = vtk.Rendering.Core.vtkMapper.newInstance();
            // var cone               = vtk.Filters.Sources.vtkConeSource.newInstance();

            $.get('/files/data/head-binary.vti', function(fileContentAsText){
                var vtiReader = vtk.IO.XML.vtkXMLImageDataReader.newInstance();
                vtiReader.parse(fileContentAsText);

                var source = vtiReader.getOutputData(0);
                console.log(source);
                var mapper = vtk.Rendering.Core.vtkVolumeMapper.newInstance();
                var actor = vtk.Rendering.Core.vtkVolume.newInstance();

                var dataArray = source.getPointData().getScalars() || source.getPointData().getArrays()[0];
                var dataRange = dataArray.getRange();
                var lookupTable = vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
                var piecewiseFunction = vtk.Common.DataModel.vtkPiecewiseFunction.newInstance();

                actor.setMapper(mapper);
                mapper.setInputData(source);
                renderer.addActor(actor);
                renderer.resetCamera();

                var sampleDistance = 0.7 * Math.sqrt(source.getSpacing().map(v => v * v).reduce((a, b) => a + b, 0));
                console.log('sampleDistance', sampleDistance);
                mapper.setSampleDistance(sampleDistance);
                actor.getProperty().setRGBTransferFunction(0, lookupTable);
                actor.getProperty().setScalarOpacity(0, piecewiseFunction);
                // actor.getProperty().setInterpolationTypeToFastLinear();
                actor.getProperty().setInterpolationTypeToLinear();
                // For better looking volume rendering
                // - distance in world coordinates a scalar opacity of 1.0
                actor.getProperty().setScalarOpacityUnitDistance(0, vtk.Common.DataModel.vtkBoundingBox.getDiagonalLength(source.getBounds()) / Math.max(...source.getDimensions()));
                // - control how we emphasize surface boundaries
                //  => max should be around the average gradient magnitude for the
                //     volume or maybe average plus one std dev of the gradient magnitude
                //     (adjusted for spacing, this is a world coordinate gradient, not a
                //     pixel gradient)
                //  => max hack: (dataRange[1] - dataRange[0]) * 0.05
                actor.getProperty().setGradientOpacityMinimumValue(0, 0);
                actor.getProperty().setGradientOpacityMaximumValue(0, (dataRange[1] - dataRange[0]) * 0.05);
                // - Use shading based on gradient
                actor.getProperty().setShade(true);
                actor.getProperty().setUseGradientOpacity(0, true);
                // - generic good default
                actor.getProperty().setGradientOpacityMinimumOpacity(0, 0.0);
                actor.getProperty().setGradientOpacityMaximumOpacity(0, 1.0);
                actor.getProperty().setAmbient(0.2);
                actor.getProperty().setDiffuse(0.7);
                actor.getProperty().setSpecular(0.3);
                actor.getProperty().setSpecularPower(8.0);


                // Sources/Rendering/OpenGL/RenderWindow

                var openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
                renderWindow.addView(openglRenderWindow);

                openglRenderWindow.setContainer(container);

                renderWindow.render();

//                var interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
//                interactor.setView(openglRenderWindow);
//                interactor.initialize();
//                interactor.bindEvents(container);
            });
        });
    }
});


module.exports = {
    VtkJsModel : VtkJsModel,
    VtkJsView : VtkJsView
};
