#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import six

import cesiumpy
import cesiumpy.common as com



def validate_color_or_none(x, key):
    """ validate whether x is str, unicode or None"""
    if x is None:
        return x
    x = _maybe_color(x)
    if not isinstance(x, Color):
        msg = '{key} must be a Color instance: {x}'
        raise ValueError(msg.format(key=key, x=x))
    return x


def _maybe_color(x):
    """ Convert str to NamedColor constant """

    if isinstance(x, six.string_types):
        cname = x.upper()

        color = getattr(cesiumpy.color, cname, None)

        if color is not None and isinstance(color, NamedColor):
            return color

    return x



class Color(object):

    def __init__(self, red, green, blue, alpha=None):

        if alpha is not None:
            com.validate_numeric(alpha, 'alpha')

        self._red = com.validate_numeric(red, key='red')
        self._green = com.validate_numeric(green, key='green')
        self._blue = com.validate_numeric(blue, key='blue')
        self._alpha = alpha

    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def alpha(self):
        return self._alpha

    def set_alpha(self, alpha):
        if alpha is not None:
            com.validate_numeric(alpha, key='alpha')

        c = self.copy()
        c._alpha = alpha
        return c

    def __repr__(self):
        if self.alpha is None:
            rep = """Cesium.Color({red}, {green}, {blue})"""
            return rep.format(red=self.red, green=self.green, blue=self.blue)
        else:
            rep = """Cesium.Color({red}, {green}, {blue}, {alpha})"""
            return rep.format(red=self.red, green=self.green,
                              blue=self.blue, alpha=self.alpha)

    def copy(self):
        return CesiumColor(red=self.red, green=self.green,
                           blue=self.blue, alpha=self.alpha)


class NamedColor(Color):

    def __init__(self, name, alpha=None):
        self._name = com.validate_str(name, key='name')
        self._alpha = alpha

    @property
    def name(self):
        return self._name

    def __repr__(self):
        if self.alpha is None:
            rep = """Cesium.Color.{name}"""
            return rep.format(name=self.name)
        else:
            rep = """Cesium.Color.{name}.withAlpha({alpha})"""
            return rep.format(name=self.name, alpha=self.alpha)

    def copy(self):
        return NamedColor(name=self.name, alpha=self.alpha)



# --------------------------------------------------
# COLOR CONSTANTS
# --------------------------------------------------

# How to create

# copy colors from "https://cesiumjs.org/Cesium/Build/Documentation/Color.html"

# colors = [c for c in colors.split() if c.startswith('staticconstant')]
# colors = [c.split('.')[-1] for c in colors]
# colors = ["{0} = NamedColor('{0}')".format(c) for c in colors]


# ToDo: Prohibit overwrite
ALICEBLUE = NamedColor('ALICEBLUE')
ANTIQUEWHITE = NamedColor('ANTIQUEWHITE')
AQUA = NamedColor('AQUA')
AQUAMARINE = NamedColor('AQUAMARINE')
AZURE = NamedColor('AZURE')
BEIGE = NamedColor('BEIGE')
BISQUE = NamedColor('BISQUE')
BLACK = NamedColor('BLACK')
BLANCHEDALMOND = NamedColor('BLANCHEDALMOND')
BLUE = NamedColor('BLUE')
BLUEVIOLET = NamedColor('BLUEVIOLET')
BROWN = NamedColor('BROWN')
BURLYWOOD = NamedColor('BURLYWOOD')
CADETBLUE = NamedColor('CADETBLUE')
CHARTREUSE = NamedColor('CHARTREUSE')
CHOCOLATE = NamedColor('CHOCOLATE')
CORAL = NamedColor('CORAL')
CORNFLOWERBLUE = NamedColor('CORNFLOWERBLUE')
CORNSILK = NamedColor('CORNSILK')
CRIMSON = NamedColor('CRIMSON')
CYAN = NamedColor('CYAN')
DARKBLUE = NamedColor('DARKBLUE')
DARKCYAN = NamedColor('DARKCYAN')
DARKGOLDENROD = NamedColor('DARKGOLDENROD')
DARKGRAY = NamedColor('DARKGRAY')
DARKGREEN = NamedColor('DARKGREEN')
DARKGREY = NamedColor('DARKGREY')
DARKKHAKI = NamedColor('DARKKHAKI')
DARKMAGENTA = NamedColor('DARKMAGENTA')
DARKOLIVEGREEN = NamedColor('DARKOLIVEGREEN')
DARKORANGE = NamedColor('DARKORANGE')
DARKORCHID = NamedColor('DARKORCHID')
DARKRED = NamedColor('DARKRED')
DARKSALMON = NamedColor('DARKSALMON')
DARKSEAGREEN = NamedColor('DARKSEAGREEN')
DARKSLATEBLUE = NamedColor('DARKSLATEBLUE')
DARKSLATEGRAY = NamedColor('DARKSLATEGRAY')
DARKSLATEGREY = NamedColor('DARKSLATEGREY')
DARKTURQUOISE = NamedColor('DARKTURQUOISE')
DARKVIOLET = NamedColor('DARKVIOLET')
DEEPPINK = NamedColor('DEEPPINK')
DEEPSKYBLUE = NamedColor('DEEPSKYBLUE')
DIMGRAY = NamedColor('DIMGRAY')
DIMGREY = NamedColor('DIMGREY')
DODGERBLUE = NamedColor('DODGERBLUE')
FIREBRICK = NamedColor('FIREBRICK')
FLORALWHITE = NamedColor('FLORALWHITE')
FORESTGREEN = NamedColor('FORESTGREEN')
FUSCHIA = NamedColor('FUSCHIA')
GAINSBORO = NamedColor('GAINSBORO')
GHOSTWHITE = NamedColor('GHOSTWHITE')
GOLD = NamedColor('GOLD')
GOLDENROD = NamedColor('GOLDENROD')
GRAY = NamedColor('GRAY')
GREEN = NamedColor('GREEN')
GREENYELLOW = NamedColor('GREENYELLOW')
GREY = NamedColor('GREY')
HONEYDEW = NamedColor('HONEYDEW')
HOTPINK = NamedColor('HOTPINK')
INDIANRED = NamedColor('INDIANRED')
INDIGO = NamedColor('INDIGO')
IVORY = NamedColor('IVORY')
KHAKI = NamedColor('KHAKI')
LAVENDAR_BLUSH = NamedColor('LAVENDAR_BLUSH')
LAVENDER = NamedColor('LAVENDER')
LAWNGREEN = NamedColor('LAWNGREEN')
LEMONCHIFFON = NamedColor('LEMONCHIFFON')
LIGHTBLUE = NamedColor('LIGHTBLUE')
LIGHTCORAL = NamedColor('LIGHTCORAL')
LIGHTCYAN = NamedColor('LIGHTCYAN')
LIGHTGOLDENRODYELLOW = NamedColor('LIGHTGOLDENRODYELLOW')
LIGHTGRAY = NamedColor('LIGHTGRAY')
LIGHTGREEN = NamedColor('LIGHTGREEN')
LIGHTGREY = NamedColor('LIGHTGREY')
LIGHTPINK = NamedColor('LIGHTPINK')
LIGHTSEAGREEN = NamedColor('LIGHTSEAGREEN')
LIGHTSKYBLUE = NamedColor('LIGHTSKYBLUE')
LIGHTSLATEGRAY = NamedColor('LIGHTSLATEGRAY')
LIGHTSLATEGREY = NamedColor('LIGHTSLATEGREY')
LIGHTSTEELBLUE = NamedColor('LIGHTSTEELBLUE')
LIGHTYELLOW = NamedColor('LIGHTYELLOW')
LIME = NamedColor('LIME')
LIMEGREEN = NamedColor('LIMEGREEN')
LINEN = NamedColor('LINEN')
MAGENTA = NamedColor('MAGENTA')
MAROON = NamedColor('MAROON')
MEDIUMAQUAMARINE = NamedColor('MEDIUMAQUAMARINE')
MEDIUMBLUE = NamedColor('MEDIUMBLUE')
MEDIUMORCHID = NamedColor('MEDIUMORCHID')
MEDIUMPURPLE = NamedColor('MEDIUMPURPLE')
MEDIUMSEAGREEN = NamedColor('MEDIUMSEAGREEN')
MEDIUMSLATEBLUE = NamedColor('MEDIUMSLATEBLUE')
MEDIUMSPRINGGREEN = NamedColor('MEDIUMSPRINGGREEN')
MEDIUMTURQUOISE = NamedColor('MEDIUMTURQUOISE')
MEDIUMVIOLETRED = NamedColor('MEDIUMVIOLETRED')
MIDNIGHTBLUE = NamedColor('MIDNIGHTBLUE')
MINTCREAM = NamedColor('MINTCREAM')
MISTYROSE = NamedColor('MISTYROSE')
MOCCASIN = NamedColor('MOCCASIN')
NAVAJOWHITE = NamedColor('NAVAJOWHITE')
NAVY = NamedColor('NAVY')
OLDLACE = NamedColor('OLDLACE')
OLIVE = NamedColor('OLIVE')
OLIVEDRAB = NamedColor('OLIVEDRAB')
ORANGE = NamedColor('ORANGE')
ORANGERED = NamedColor('ORANGERED')
ORCHID = NamedColor('ORCHID')
PALEGOLDENROD = NamedColor('PALEGOLDENROD')
PALEGREEN = NamedColor('PALEGREEN')
PALETURQUOISE = NamedColor('PALETURQUOISE')
PALEVIOLETRED = NamedColor('PALEVIOLETRED')
PAPAYAWHIP = NamedColor('PAPAYAWHIP')
PEACHPUFF = NamedColor('PEACHPUFF')
PERU = NamedColor('PERU')
PINK = NamedColor('PINK')
PLUM = NamedColor('PLUM')
POWDERBLUE = NamedColor('POWDERBLUE')
PURPLE = NamedColor('PURPLE')
RED = NamedColor('RED')
ROSYBROWN = NamedColor('ROSYBROWN')
ROYALBLUE = NamedColor('ROYALBLUE')
SADDLEBROWN = NamedColor('SADDLEBROWN')
SALMON = NamedColor('SALMON')
SANDYBROWN = NamedColor('SANDYBROWN')
SEAGREEN = NamedColor('SEAGREEN')
SEASHELL = NamedColor('SEASHELL')
SIENNA = NamedColor('SIENNA')
SILVER = NamedColor('SILVER')
SKYBLUE = NamedColor('SKYBLUE')
SLATEBLUE = NamedColor('SLATEBLUE')
SLATEGRAY = NamedColor('SLATEGRAY')
SLATEGREY = NamedColor('SLATEGREY')
SNOW = NamedColor('SNOW')
SPRINGGREEN = NamedColor('SPRINGGREEN')
STEELBLUE = NamedColor('STEELBLUE')
TAN = NamedColor('TAN')
TEAL = NamedColor('TEAL')
THISTLE = NamedColor('THISTLE')
TOMATO = NamedColor('TOMATO')
TRANSPARENT = NamedColor('TRANSPARENT')
TURQUOISE = NamedColor('TURQUOISE')
VIOLET = NamedColor('VIOLET')
WHEAT = NamedColor('WHEAT')
WHITE = NamedColor('WHITE')
WHITESMOKE = NamedColor('WHITESMOKE')
YELLOW = NamedColor('YELLOW')
YELLOWGREEN = NamedColor('YELLOWGREEN')