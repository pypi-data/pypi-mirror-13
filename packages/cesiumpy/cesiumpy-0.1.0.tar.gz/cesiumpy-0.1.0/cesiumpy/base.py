#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import collections
import json
import os
import six

import cesiumpy.common as com


class _CesiumObject(object):
    """
    Base class for Cesium instances, which can be converted to
    JavaScript instance
    """

    @property
    def _klass(self):
        return "Cesium.{0}".format(self.__class__.__name__)

    @property
    def _props(self):
        raise NotImplementedError('must be overriden in child classes')

    @property
    def _property_dict(self):
        props = collections.OrderedDict()
        for p in self._props:
            props[p] = getattr(self, p)
        return props

    @property
    def script(self):
        props = self._property_dict
        results = com.to_jsobject(props)
        return ''.join(results)


class _CesiumConstant(object):

    def __init__(self, constant):
        self._constant = constant

    def __repr__(self):
        return self._constant

    @property
    def script(self):
        return self._constant


class _CesiumBase(_CesiumObject):
    """
    Base class for Cesium Widget / Viewer
    """

    _props = ['clock', 'imageryProvider', 'terrainProvider',
              'skyBox', 'skyAtmosphere', 'sceneMode',
              'scene3DOnly', 'orderIndependentTranslucency',
              'mapProjection', 'globe', 'useDefaultRenderLoop',
              'targetFrameRate', 'showRenderLoopErrors',
              'contextOptions', 'creditContainer',
              'terrainExaggeration']
    _varname = 'widget'

    def __init__(self, divid=None, width='100%', height='100%',
                 clock=None, imageryProvider=None, terrainProvider=None,
                 skyBox=None, skyAtmosphere=None, sceneMode=None,
                 scene3DOnly=None, orderIndependentTranslucency=None,
                 mapProjection=None, globe=None, useDefaultRenderLoop=None,
                 targetFrameRate=None, showRenderLoopErrors=None,
                 contextOptions=None, creditContainer=None,
                 terrainExaggeration=None):

        if divid is None:
            divid = 'container-{0}'.format(id(self))
        self.divid = divid

        self.width = com.validate_str(width, key='width')
        self.height = com.validate_str(height, key='width')

        self.clock = com.notimplemented(clock)

        self.imageryProvider = imageryProvider
        self.terrainProvider = terrainProvider

        self.skyBox = com.notimplemented(skyBox)
        self.skyAtmosphere = com.notimplemented(skyAtmosphere)
        self.sceneMode = com.notimplemented(sceneMode)

        self.scene3DOnly = com.validate_bool_or_none(scene3DOnly, key='scene3DOnly')
        self.orderIndependentTranslucency = com.validate_bool_or_none(orderIndependentTranslucency, key='orderIndependentTranslucency')

        self.mapProjection = com.notimplemented(mapProjection)
        self.globe = com.notimplemented(globe)

        self.useDefaultRenderLoop = com.validate_bool_or_none(useDefaultRenderLoop, key='useDefaultRenderLoop')
        self.targetFrameRate = com.validate_numeric_or_none(targetFrameRate, key='targetFrameRate')
        self.showRenderLoopErrors = com.validate_bool_or_none(showRenderLoopErrors, key='showRenderLoopErrors')

        self.contextOptions = com.notimplemented(contextOptions)

        self.creditContainer = com.notimplemented(creditContainer)

        self.terrainExaggeration = com.validate_numeric_or_none(terrainExaggeration, key='terrainExaggeration')

        from cesiumpy.camera import Camera
        self._camera = Camera()

    @property
    def _load_scripts(self):
        js = """<script src="https://cesiumjs.org/Cesium/Build/Cesium/Cesium.js"></script>"""
        css = """<link rel="stylesheet" href="http://cesiumjs.org/Cesium/Build/CesiumUnminified/Widgets/CesiumWidget/CesiumWidget.css" type="text/css">"""
        return [js, css]

    @property
    def container(self):
        container = """<div id="{0}" style="width:{1}; height:{2};"><div>"""
        return container.format(self.divid, self.height, self.width)

    def _repr_html_(self):
        return self.to_html()

    def to_html(self):
        headers = self._load_scripts
        container = self.container
        script = self._wrap_js(self.script)

        results = self._build_html(headers, container, script)
        return results

    def _build_html(self, *args):
        results = []
        for a in args:
            if isinstance(a, list):
                results.extend(a)
            elif isinstance(a, six.string_types):
                results.append(a)
            else:
                raise ValueError(type(a))
        return os.linesep.join(results)

    @property
    def script(self):
        props = com.to_jsobject(self._property_dict)
        props = ''.join(props)
        if props != '':
            script = """var {varname} = new {klass}("{divid}", {props});"""
            script = script.format(varname=self._varname, klass=self._klass,
                                   divid=self.divid, props=''.join(props))
        else:
            script = """var {varname} = new {klass}("{divid}");"""
            script = script.format(varname=self._varname, klass=self._klass,
                                   divid=self.divid)
        return ([script] + self._entities_script +
                self._dataSources_script + [self._camera_script])

    @property
    def _entities_script(self):
        # temp, should return list
        return []

    @property
    def _dataSources_script(self):
        # temp, should return list
        return []
    @property
    def _camera_script(self):
        camera = self.camera.script
        if camera != '':
            script = """{varname}.camera.flyTo({camera});"""
            script = script.format(varname=self._varname,
                                   camera=camera)
            return script
        else:
            return ''

    @property
    def camera(self):
        return self._camera

    def _wrap_js(self, script):
        if not isinstance(script, list):
            script = [script]
        # filter None and empty str
        script = [s for s in script if s is not None and len(s) > 0]
        script = self._add_indent(script)
        return ["""<script type="text/javascript">"""] + script + ["""</script>"""]

    def _add_indent(self, script, indent=2):
        """ Indent list of script with specfied number of spaces """
        if not isinstance(script, list):
            script = [script]

        indent = ' ' * indent
        return [indent + s for s in script]
