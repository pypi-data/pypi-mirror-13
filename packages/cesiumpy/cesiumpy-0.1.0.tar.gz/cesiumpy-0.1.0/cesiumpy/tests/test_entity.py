#!/usr/bin/env python
# coding: utf-8

import unittest
import nose

import cesiumpy


class TestEntity(unittest.TestCase):

    def test_validate_definitions(self):
        entities = [cesiumpy.Point, cesiumpy.Label, cesiumpy.Billboard,
                    cesiumpy.Ellipse, cesiumpy.Ellipsoid,
                    cesiumpy.Corridor, cesiumpy.Cylinder,
                    cesiumpy.Polyline, cesiumpy.PolylineVolume, cesiumpy.Wall,
                    cesiumpy.Rectangle, cesiumpy.Box, cesiumpy.Polygon]

        for entity in entities:
        # validate for development purpose, should be moved to tests
            for p in entity._props:
                self.assertFalse(p in entity._common_props)
            self.assertFalse('name' in entity._props)
            self.assertFalse('position' in entity._props)
            self.assertFalse('name' in entity._common_props)
            self.assertFalse('position' in entity._common_props)

    def test_point(self):
        e = cesiumpy.Point(position=(-110, 40, 0))
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), point : {color : Cesium.Color.WHITE, pixelSize : 10}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Point(position=(-110, 40, 0), pixelSize=100, color='blue')
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), point : {color : Cesium.Color.BLUE, pixelSize : 100}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_label(self):
        e = cesiumpy.Label(position=(-110, 40, 0), text='label_text')
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), label : {text : "label_text"}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Label(position=(-110, 40, 0), text='label_text', fillColor='blue', scale=0.1)
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), label : {text : "label_text", fillColor : Cesium.Color.BLUE, scale : 0.1}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_billboard(self):
        p = cesiumpy.Pin()
        e = cesiumpy.Billboard(position=(-110, 40, 0), image=p)
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), billboard : {image : new Cesium.PinBuilder().fromColor(Cesium.Color.ROYALBLUE, 48)}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        p = cesiumpy.Pin().fromText('?')
        e = cesiumpy.Billboard(position=(-110, 40, 0), image=p)
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), billboard : {image : new Cesium.PinBuilder().fromText("?", Cesium.Color.ROYALBLUE, 48)}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        p = cesiumpy.Pin().fromText('!', color='red')
        e = cesiumpy.Billboard(position=(-110, 40, 0), image=p, scale=3)
        exp = """{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), billboard : {image : new Cesium.PinBuilder().fromText("!", Cesium.Color.RED, 48), scale : 3}}"""
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_ellipse(self):
        e = cesiumpy.Ellipse(position=[-110, 40, 0], semiMinorAxis=25.0, semiMajorAxis=40.0)
        exp = "{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), ellipse : {semiMinorAxis : 25.0, semiMajorAxis : 40.0}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Ellipse(position=[-110, 40, 0], semiMinorAxis=25.0, semiMajorAxis=40.0, material=cesiumpy.color.RED)
        exp = "{position : Cesium.Cartesian3.fromDegrees(-110, 40, 0), ellipse : {semiMinorAxis : 25.0, semiMajorAxis : 40.0, material : Cesium.Color.RED}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Ellipse(position=[-110, 40, 0], semiMinorAxis=25.0, semiMajorAxis=40.0, material='red')
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_ellipsoid(self):
        e = cesiumpy.Ellipsoid(position=(-70, 40, 0), radii=(20, 30, 40), material=cesiumpy.color.GREEN)
        exp = "{position : Cesium.Cartesian3.fromDegrees(-70, 40, 0), ellipsoid : {radii : new Cesium.Cartesian3(20, 30, 40), material : Cesium.Color.GREEN}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Ellipsoid(position=(-70, 40, 0), radii=(20, 30, 40), material=cesiumpy.color.RED, name='XXX')
        exp = '{name : "XXX", position : Cesium.Cartesian3.fromDegrees(-70, 40, 0), ellipsoid : {radii : new Cesium.Cartesian3(20, 30, 40), material : Cesium.Color.RED}}'
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_cylinder(self):
        e = cesiumpy.Cylinder(position=(-70, 40, 0), length=10, topRadius=100, bottomRadius=200, material=cesiumpy.color.AQUA)
        exp = "{position : Cesium.Cartesian3.fromDegrees(-70, 40, 0), cylinder : {length : 10, topRadius : 100, bottomRadius : 200, material : Cesium.Color.AQUA}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Cylinder(position=(-70, 40, 0), length=10, topRadius=100, bottomRadius=200)
        exp = "{position : Cesium.Cartesian3.fromDegrees(-70, 40, 0), cylinder : {length : 10, topRadius : 100, bottomRadius : 200}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_polyline(self):
        e = cesiumpy.Polyline(positions=[-77, 35, -77.1, 35], width=5, material=cesiumpy.color.RED)
        exp = "{polyline : {positions : Cesium.Cartesian3.fromDegreesArray([-77, 35, -77.1, 35]), width : 5, material : Cesium.Color.RED}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_polylinevolume(self):
        e = cesiumpy.PolylineVolume(positions=[-120, 20, -90, 25, -60, 20],
                                    shape=[cesiumpy.Cartesian2(-50000, -50000), cesiumpy.Cartesian2(50000, -50000),
                                           cesiumpy.Cartesian2(50000, 50000), cesiumpy.Cartesian2(-50000, 50000)],
                                    material=cesiumpy.color.GREEN)
        exp = "{polylineVolume : {positions : Cesium.Cartesian3.fromDegreesArray([-120, 20, -90, 25, -60, 20]), shape : [new Cesium.Cartesian2(-50000, -50000), new Cesium.Cartesian2(50000, -50000), new Cesium.Cartesian2(50000, 50000), new Cesium.Cartesian2(-50000, 50000)], material : Cesium.Color.GREEN}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.PolylineVolume(positions=[-120, 20, -90, 25, -60, 20],
                                    shape=[1, 2, 3, 4], material=cesiumpy.color.GREEN)
        exp = "{polylineVolume : {positions : Cesium.Cartesian3.fromDegreesArray([-120, 20, -90, 25, -60, 20]), shape : [new Cesium.Cartesian2(1, 2), new Cesium.Cartesian2(3, 4)], material : Cesium.Color.GREEN}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.PolylineVolume(positions=[(-120, 20), (-90, 25), (-60, 20)],
                                    shape=((1, 2), (3, 4)), material=cesiumpy.color.GREEN)
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.PolylineVolume(positions=[(-120, 20), (-90, 25), (-60, 20)],
                                    shape=((1, 2), (3, 4)), material=cesiumpy.color.GREEN)
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        msg = "shape must be list-likes: 1"
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.PolylineVolume(positions=[-120, 20, -90, 25, -60, 20], shape=1, material=cesiumpy.color.GREEN)

        msg = "shape length must be an even number: \\[1, 2, 4\\]"
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.PolylineVolume(positions=[-120, 20, -90, 25, -60, 20], shape=[1, 2, 4], material=cesiumpy.color.GREEN)

        msg = "shape must be a listlike of Cartesian2: "
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.PolylineVolume(positions=[-120, 20, -90, 25, -60, 20],
                                    shape=[cesiumpy.Cartesian2(1, 2), cesiumpy.Cartesian3(1, 2, 3),
                                           cesiumpy.Cartesian2(3, 4)],
                                    material=cesiumpy.color.GREEN)


    def test_corridor(self):
        e = cesiumpy.Corridor(positions=[-120, 30, -90, 35, -60, 30],
                              width=2e5, material=cesiumpy.color.RED)
        exp = "{corridor : {positions : Cesium.Cartesian3.fromDegreesArray([-120, 30, -90, 35, -60, 30]), width : 200000.0, material : Cesium.Color.RED}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Corridor(positions=((-120, 30), (-90, 35), (-60, 30)),
                              width=2e5, material='red')
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        msg = "x length must be an even number: "
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.Corridor(positions=((-120, 30), (35, ), (-60, 30)),
                              width=2e5, material='red')

    def test_wall(self):
        e = cesiumpy.Wall(positions=[-60, 40, -65, 40, -65, 45, -60, 45],
                          maximumHeights=100, minimumHeights=0,
                          material=cesiumpy.color.RED)
        exp = "{wall : {positions : Cesium.Cartesian3.fromDegreesArray([-60, 40, -65, 40, -65, 45, -60, 45]), maximumHeights : [100, 100, 100, 100], minimumHeights : [0, 0, 0, 0], material : Cesium.Color.RED}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Wall(positions=[-60, 40, -65, 40, -65, 45, -60, 45],
                          maximumHeights=[100] * 4, minimumHeights=[0] * 4,
                          material=cesiumpy.color.RED)
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Wall(positions=[(-60, 40), (-65, 40), (-65, 45), (-60, 45)],
                          maximumHeights=100, minimumHeights=0,
                          material='red')
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Wall(positions=[(-60, 40), (-65, 40), (-65, 45), (-60, 45)],
                          maximumHeights=[100] * 4, minimumHeights=[0] * 4,
                          material='red')
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        msg = "maximumHeights must has the half length"
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.Wall(positions=[-60, 40, -65, 40, -65, 45, -60, 45],
                          maximumHeights=[100] * 2, minimumHeights=[0] * 4,
                          material=cesiumpy.color.RED)

        msg = "minimumHeights must has the half length"
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.Wall(positions=[-60, 40, -65, 40, -65, 45, -60, 45],
                          maximumHeights=[100] * 4, minimumHeights=[0] * 3,
                          material=cesiumpy.color.RED)

    def test_rectangle(self):
        e = cesiumpy.Rectangle(coordinates=(-80, 20, -60, 40), material=cesiumpy.color.GREEN)
        exp = "{rectangle : {coordinates : Cesium.Rectangle.fromDegrees(-80, 20, -60, 40), material : Cesium.Color.GREEN}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Rectangle(coordinates=(-80, 20, -60, 40),
                               material=cesiumpy.color.GREEN, outlineColor=cesiumpy.color.RED)
        exp = "{rectangle : {coordinates : Cesium.Rectangle.fromDegrees(-80, 20, -60, 40), material : Cesium.Color.GREEN, outlineColor : Cesium.Color.RED}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Rectangle(coordinates=[(-80, 20), (-60, 40)],
                               material='green', outlineColor='red')
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Rectangle(coordinates=(-80, 20, -60, 40), material='green', outlineColor='red')
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        msg = "coordinates length must be 4:"
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.Rectangle(coordinates=[1, 2, 3],
                               material='green', outlineColor='red')

        msg = "north must be numeric: X"
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.Rectangle(coordinates=(-80, 20, -60, 'X'),
                               material='green', outlineColor='red')

    def test_box(self):
        e = cesiumpy.Box(dimensions=(40e4, 30e4, 50e4),
                         material=cesiumpy.color.RED, position=[-120, 40, 0])
        exp = "{position : Cesium.Cartesian3.fromDegrees(-120, 40, 0), box : {dimensions : new Cesium.Cartesian3(400000.0, 300000.0, 500000.0), material : Cesium.Color.RED}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        msg = "dimensions length must be 3 to be converted to Cartesian3: "
        with nose.tools.assert_raises_regexp(ValueError, msg):
            cesiumpy.Box(dimensions=(40e4, 30e4),
                         material=cesiumpy.color.RED, position=[-120, 40, 0])

    def test_polygon(self):
        e = cesiumpy.Polygon([1, 1, 2, 2])
        exp = "{polygon : {hierarchy : Cesium.Cartesian3.fromDegreesArray([1, 1, 2, 2])}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

        e = cesiumpy.Polygon([1, 1, 2, 2], material=cesiumpy.color.AQUA)
        exp = "{polygon : {hierarchy : Cesium.Cartesian3.fromDegreesArray([1, 1, 2, 2]), material : Cesium.Color.AQUA}}"
        self.assertEqual(e.script, exp)

        e = e.copy()
        self.assertEqual(e.script, exp)

    def test_entities_repr(self):
        e = cesiumpy.Point(position=[-110, 40, 0])
        exp = "Point(-110, 40, 0)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Label(position=[-110, 40, 0], text='xxx')
        exp = "Label(-110, 40, 0)"
        self.assertEqual(repr(e), exp)

        p = cesiumpy.Pin()
        e = cesiumpy.Billboard(position=(-110, 40, 0), image=p)
        exp = "Billboard(-110, 40, 0)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Box(position=[-110, 40, 0], dimensions=(40e4, 30e4, 50e4))
        exp = "Box(-110, 40, 0)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Ellipse(position=[-110, 40, 0], semiMinorAxis=25e4,
                             semiMajorAxis=40e4)
        exp = "Ellipse(-110, 40, 0)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Cylinder(position=[-110, 40, 100], length=100e4,
                              topRadius=10e4, bottomRadius=10e4)
        exp = "Cylinder(-110, 40, 100)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Polygon(hierarchy=[-90, 40, -95, 40, -95, 45, -90, 40])
        exp = "Polygon([-90, 40, -95, 40, -95, 45, -90, 40])"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Rectangle(coordinates=(-85, 40, -80, 45))
        exp = "Rectangle(west=-85, south=40, east=-80, north=45)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Ellipsoid(position=(-70, 40, 0), radii=(20e4, 20e4, 30e4))
        exp = "Ellipsoid(-70, 40, 0)"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Wall(positions=[-60, 40, -65, 40, -65, 45, -60, 45],
                          maximumHeights=[10e4] * 4, minimumHeights=[0] * 4)
        exp = "Wall([-60, 40, -65, 40, -65, 45, -60, 45])"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Corridor(positions=[-120, 30, -90, 35, -60, 30], width=2e5)
        exp = "Corridor([-120, 30, -90, 35, -60, 30])"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.Polyline(positions=[-120, 25, -90, 30, -60, 25], width=0.5)
        exp = "Polyline([-120, 25, -90, 30, -60, 25])"
        self.assertEqual(repr(e), exp)

        e = cesiumpy.PolylineVolume(positions=[-120, 20, -90, 25, -60, 20],
                                    shape=[-5e4, -5e4, 5e4, -5e4, 5e4, 5e4, -5e4, 5e4])
        exp = "PolylineVolume([-120, 20, -90, 25, -60, 20])"
        self.assertEqual(repr(e), exp)



if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)
