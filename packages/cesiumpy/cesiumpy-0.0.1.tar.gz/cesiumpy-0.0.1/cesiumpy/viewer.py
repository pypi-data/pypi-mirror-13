#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import collections
import json

from cesiumpy.base import _CesiumBase
import cesiumpy.common as com


class Viewer(_CesiumBase):
    """
    Viewer

    Parameters
    ----------

    divid: str
        id string used in div tag
    width: str
        width of div tag, should be provided as css format like "100%" or "100px"
    height: str
        height of div tag, should be provided as css format like "100%" or "100px"
    animation: bool, default True
        If set to false, the Animation widget will not be created.
    baseLayerPicker: bool, default True
        If set to false, the BaseLayerPicker widget will not be created.
    fullscreenButton: bool, default True
        If set to false, the FullscreenButton widget will not be created.
    geocoder: bool, default True
        If set to false, the Geocoder widget will not be created.
    homeButton: bool, default True
        If set to false, the HomeButton widget will not be created.
    infoBox: bool, default True
        If set to false, the InfoBox widget will not be created.
    sceneModePicker: bool, default True
        If set to false, the SceneModePicker widget will not be created.
    selectionIndicator: bool, default True
        If set to false, the SelectionIndicator widget will not be created.
    timeline: bool, default True
        If set to false, the Timeline widget will not be created.
    navigationHelpButton: bool, default True
        If set to the false, the navigation help button will not be created.
    navigationInstructionsInitiallyVisible: bool, defaut True
        True if the navigation instructions should initially be visible, or false if the should not be shown until the user explicitly clicks the button.
    scene3DOnly: bool, default False
        When true, each geometry instance will only be rendered in 3D to save GPU memory.
    clock: Clock, default new Clock()
        The clock to use to control current time.
    selectedImageryProviderViewModel: ProviderViewModel
        The view model for the current base imagery layer, if not supplied the first available base layer is used. This value is only valid if options.baseLayerPicker is set to true.
    imageryProviderViewModels: list of ProviderViewModel, default createDefaultImageryProviderViewModels()
        The list of ProviderViewModels to be selectable from the BaseLayerPicker. This value is only valid if options.baseLayerPicker is set to true.
    selectedTerrainProviderViewModel: ProviderViewModel
        The view model for the current base terrain layer, if not supplied the first available base layer is used. This value is only valid if options.baseLayerPicker is set to true.
    terrainProviderViewModels: list of ProviderViewModel, default createDefaultTerrainProviderViewModels()
        The list of ProviderViewModels to be selectable from the BaseLayerPicker. This value is only valid if options.baseLayerPicker is set to true.
    imageryProvider: ImageryProvider, default new BingMapsImageryProvider()
        The imagery provider to use. This value is only valid if options.baseLayerPicker is set to false.
    terrainProvider: TerrainProvider, default new EllipsoidTerrainProvider()
        The terrain provider to use
    skyBox: SkyBox
        The skybox used to render the stars. When undefined, the default stars are used.
    skyAtmosphere: SkyAtmosphere
        Blue sky, and the glow around the Earth's limb. Set to false to turn it off.
    fullscreenElement: Element or str, default document.body
        The element or id to be placed into fullscreen mode when the full screen button is pressed.
    useDefaultRenderLoop: bool, default True
        True if this widget should control the render loop, false otherwise.
    targetFrameRate: float
        The target frame rate when using the default render loop.
    showRenderLoopErrors: bool, default True
        If true, this widget will automatically display an HTML panel to the user containing the error, if a render loop error occurs.
    automaticallyTrackDataSourceClocks: bool, default True
        If true, this widget will automatically track the clock settings of newly added DataSources, updating if the DataSource's clock changes. Set this to false if you want to configure the clock independently.
    contextOptions: Object
        Context and WebGL creation properties corresponding to options passed to Scene.
    sceneMode: SceneMode, default SceneMode.SCENE3D
        The initial scene mode.
    mapProjection: MapProjection, default new GeographicProjection()
        The map projection to use in 2D and Columbus View modes.
    globe: Globe, default new Globe(mapProjection.ellipsoid)
        The globe to use in the scene. If set to false, no globe will be added.
    orderIndependentTranslucency: bool, default True
        If true and the configuration supports it, use order independent translucency.
    creditContainer: Element or str
        The DOM element or ID that will contain the CreditDisplay. If not specified, the credits are added to the bottom of the widget itself.
    dataSources: DataSourceCollection, default new DataSourceCollection()
        The collection of data sources visualized by the widget. If this parameter is provided, the instance is assumed to be owned by the caller and will not be destroyed when the viewer is destroyed.
    terrainExaggeration: float, default 1.
        A scalar used to exaggerate the terrain. Note that terrain exaggeration will not modify any other primitive as they are positioned relative to the ellipsoid.
    """

    _props = ['animation', 'baseLayerPicker', 'fullscreenButton',
              'geocoder', 'homeButton', 'infoBox', 'sceneModePicker',
              'selectionIndicator', 'timeline', 'navigationHelpButton',
              'navigationInstructionsInitiallyVisible', 'scene3DOnly', 'clock',
              'selectedImageryProviderViewModel', 'imageryProviderViewModels',
              'selectedTerrainProviderViewModel', 'terrainProviderViewModels',
              'imageryProvider', 'terrainProvider', 'skyBox', 'skyAtmosphere',
              'fullscreenElement', 'useDefaultRenderLoop', 'targetFrameRate',
              'showRenderLoopErrors', 'automaticallyTrackDataSourceClocks',
              'contextOptions', 'sceneMode', 'mapProjection', 'globe',
              'orderIndependentTranslucency', 'creditContainer', 'dataSources',
              'terrainExaggeration']

    def __init__(self, divid=None, width='100%', height='100%',
                 animation=None, baseLayerPicker=None, fullscreenButton=None,
                 geocoder=None, homeButton=None, infoBox=None,
                 sceneModePicker=None, selectionIndicator=None, timeline=None,
                 navigationHelpButton=None, navigationInstructionsInitiallyVisible=None,
                 scene3DOnly=None, clock=None,
                 selectedImageryProviderViewModel=None, imageryProviderViewModels=None,
                 selectedTerrainProviderViewModel=None, terrainProviderViewModels=None,
                 imageryProvider=None, terrainProvider=None, skyBox=None, skyAtmosphere=None,
                 fullscreenElement=None, useDefaultRenderLoop=None, targetFrameRate=None,
                 showRenderLoopErrors=None, automaticallyTrackDataSourceClocks=None,
                 contextOptions=None, sceneMode=None, mapProjection=None, globe=None,
                 orderIndependentTranslucency=None, creditContainer=None, dataSources=None,
                 terrainExaggeration=None):

        super(Viewer, self).__init__(divid=divid, width=width, height=height,
                                     scene3DOnly=scene3DOnly, clock=clock,
                                     imageryProvider=imageryProvider,
                                     terrainProvider=terrainProvider,
                                     skyBox=skyBox, skyAtmosphere=skyAtmosphere,
                                     sceneMode=sceneMode,
                                     orderIndependentTranslucency=orderIndependentTranslucency,
                                     mapProjection=mapProjection, globe=globe,
                                     useDefaultRenderLoop=useDefaultRenderLoop,
                                     targetFrameRate=targetFrameRate,
                                     showRenderLoopErrors=showRenderLoopErrors,
                                     contextOptions=contextOptions,
                                     creditContainer=creditContainer,
                                     terrainExaggeration=terrainExaggeration)

        self.animation = com.validate_bool_or_none(animation, key='animation')
        self.baseLayerPicker = com.validate_bool_or_none(baseLayerPicker, key='baseLayerPicker')
        self.fullscreenButton = com.validate_bool_or_none(fullscreenButton, key='fullscreenButton')
        self.geocoder = com.validate_bool_or_none(geocoder, key='geocoder')
        self.homeButton = com.validate_bool_or_none(homeButton, key='homeButton')
        self.infoBox = com.validate_bool_or_none(infoBox, key='infoBox')
        self.sceneModePicker = com.validate_bool_or_none(sceneModePicker, key='sceneModePicker')
        self.selectionIndicator = com.validate_bool_or_none(selectionIndicator, key='selectionIndicator')
        self.timeline = com.validate_bool_or_none(timeline, key='timeline')
        self.navigationHelpButton = com.validate_bool_or_none(navigationHelpButton, key='navigationHelpButton')
        self.navigationInstructionsInitiallyVisible = com.validate_bool_or_none(navigationInstructionsInitiallyVisible, key='navigationInstructionsInitiallyVisible')

        if selectedImageryProviderViewModel is not None:
            raise NotImplementedError
        self.selectedImageryProviderViewModel = selectedImageryProviderViewModel
        if imageryProviderViewModels is not None:
            raise NotImplementedError
        self.imageryProviderViewModels = imageryProviderViewModels
        if selectedTerrainProviderViewModel is not None:
            raise NotImplementedError
        self.selectedTerrainProviderViewModel = selectedTerrainProviderViewModel
        if terrainProviderViewModels is not None:
            raise NotImplementedError
        self.terrainProviderViewModels = terrainProviderViewModels

        if fullscreenElement is not None:
            raise NotImplementedError
        self.fullscreenElement = fullscreenElement
        self.automaticallyTrackDataSourceClocks = com.validate_bool_or_none(automaticallyTrackDataSourceClocks, key='automaticallyTrackDataSourceClocks')

        if dataSources is not None:
            raise NotImplementedError
        self.dataSources = dataSources

        # ToDo: API to disable all flags to False
        # store cesium objects as entities
        self._entities = EntityList()

    @property
    def script(self):
        script = super(Viewer, self).script
        return [script] + self.entities.script

    @property
    def entities(self):
        return self._entities


class EntityList(object):

    def __init__(self):
        self._entities = []

    def add(self, entity):
        from cesiumpy.entity import _CesiumEntity
        if not isinstance(entity, _CesiumEntity):
            msg = 'entity must be a CesiumEntity instance: {0}'
            raise ValueError(msg.format(type(entity)))

        self._entities.append(entity)

    def clear(self):
        self._entities = []

    def __len__(self):
        return len(self._entities)

    def __getitem__(self, item):
        return self._entities[item]

    @property
    def script(self):
        """
        return list of scripts built from entities
        each script may be a list of comamnds also
        """
        results = []
        for entity in self._entities:
            script = """widget.entities.add({entity});""".format(entity=entity)
            results.append(script)
        return results

