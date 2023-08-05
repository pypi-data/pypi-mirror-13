# -*- coding:utf-8 -*-

from twisted.web import resource


page = (
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n'
    '  <title>phen</title>\n  <meta name="description" content="">\n  <m'
    'eta name="viewport" content="width=device-width, initial-scale=1"'
    '>\n  <style>\n    body {\n      font-family: monospace;\n      backgr'
    'ound: #393A40;\n      color: #f84;\n      padding: 50px;\n      text'
    '-align: center;\n      font-family: monospace;\n      font-weight: '
    'bold;\n    }\n    #content {\n        margin-top: 20px;\n    }\n  </st'
    'yle>\n</head>\n<body>\n<svg\n   xmlns:dc="http://purl.org/dc/elements'
    '/1.1/"\n   xmlns:cc="http://creativecommons.org/ns#"\n   xmlns:rdf='
    '"http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n   xmlns:svg="http:'
    '//www.w3.org/2000/svg"\n   xmlns="http://www.w3.org/2000/svg"\n   v'
    'ersion="1.1"\n   id="svg3353"\n   viewBox="0 0 480.00001 192"\n   he'
    'ight="192"\n   width="480">\n  <g\n     transform="translate(0,-860.'
    '36216)"\n     id="layer1">\n    <rect\n       y="860.36218"\n       x'
    '="0"\n       height="192"\n       width="480"\n       id="rect3365"\n'
    '       style="color:#000000;display:inline;overflow:visible;visib'
    'ility:visible;fill:#000000;fill-opacity:1;fill-rule:nonzero;strok'
    'e:none;stroke-width:5.2441659;stroke-linecap:butt;stroke-linejoin'
    ':miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffse'
    't:0;stroke-opacity:1;marker:none;enable-background:accumulate" />'
    '\n    <g\n       id="text3361"\n       style="font-style:normal;font'
    '-variant:normal;font-weight:600;font-stretch:normal;font-size:180'
    "px;line-height:125%;font-family:'Latin Modern Sans Demi Cond';-in"
    "kscape-font-specification:'Latin Modern Sans Demi Cond, Semi-Bold"
    "';text-align:start;letter-spacing:0px;word-spacing:0px;writing-mo"
    'de:lr-tb;text-anchor:start;fill:#ffffff;fill-opacity:1;stroke:non'
    'e;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stro'
    'ke-opacity:1">\n      <path\n         id="path3387"\n         style='
    '""\n         d="m 151.22906,960.95218 c 0,-18.18 -5.04,-43.92 -29.'
    '16,-43.92 -9.36,0 -16.92,4.5 -22.319995,10.44 0,-5.04 0,-8.64 -7.'
    '92,-8.64 l -3.42,0 c -6.3,0 -8.1,1.62 -8.1,8.1 l 0,98.82002 c 0,6'
    '.3 1.62,8.1 8.1,8.1 l 3.96,0 c 6.3,0 7.919995,-1.8 7.919995,-7.92'
    ' l 0,-28.44002 c 6.48,7.02002 12.06,8.10002 17.28,8.10002 10.26,0'
    ' 20.52,-4.86 26.28,-13.68002 6.48,-10.26 7.38,-21.24 7.38,-30.96 '
    'z m -19.98,0.36 c 0,5.04 0,32.76 -18.72,32.76 -7.74,0 -11.88,-6.4'
    '8 -12.24,-7.02 l 0,-50.76 c 3.42,-3.96 8.46,-6.66 13.86,-6.66 17.'
    '1,0 17.1,26.28 17.1,31.68 z" />\n      <path\n         id="path3389'
    '"\n         style=""\n         d="m 234.105,995.87218 0,-53.64 c 0,'
    '-14.4 -4.5,-25.2 -23.04,-25.2 -14.4,0 -21.6,10.44 -24.66,17.1 l -'
    '0.18,0 0,-47.34 c 0,-5.58 -1.08,-7.92 -7.92,-7.92 l -3.42,0 c -6.'
    '3,0 -8.1,1.62 -8.1,8.1 l 0,108.72 c 0,6.30002 1.62,8.10002 8.1,8.'
    '10002 l 3.96,0 c 6.3,0 7.92,-1.8 7.92,-7.92002 l 0,-43.02 c 0,-16'
    '.38 9.18,-24.3 17.64,-24.3 7.56,0 9.72,4.32 9.72,14.4 l 0,52.92 c'
    ' 0,5.58002 1.08,7.92002 7.92,7.92002 l 4.14,0 c 6.3,0 7.92,-1.8 7'
    '.92,-7.92002 z" />\n      <path\n         id="path3391"\n         st'
    'yle=""\n         d="m 317.88094,954.29218 c 0,-24.66 -11.52,-38.16'
    ' -32.4,-38.16 -15.84,0 -36.9,9 -36.9,44.64 0,35.1 21.42,44.82002 '
    '39.06,44.82002 6.66,0 12.24,-1.44 17.82,-3.96 3.42,-1.62 11.34,-6'
    '.12002 11.34,-9.54002 0,-1.44 -0.36,-4.86 -0.54,-6.48 -0.54,-3.42'
    ' -0.54,-4.32 -2.34,-4.32 -0.9,0 -1.44,0.54 -2.34,1.62 -8.46,10.08'
    ' -19.44,11.16 -23.22,11.16 -21.24,0 -21.24,-26.64 -21.24,-32.04 l'
    ' 42.84,0 c 5.76,0 7.92,-1.26 7.92,-7.74 z m -15.48,-0.72 -35.1,0 '
    'c 0.72,-12.96 5.94,-25.92 18.36,-25.92 15.66,0 16.38,16.74 16.74,'
    '25.92 z" />\n      <path\n         id="path3393"\n         style=""\n'
    '         d="m 399.69094,995.87218 0,-53.64 c 0,-14.4 -4.5,-25.2 -'
    '23.04,-25.2 -13.32,0 -20.7,8.46 -25.2,18.36 l -0.18,0 0,-9.72 c 0'
    ',-5.58 -1.08,-7.92 -7.92,-7.92 l -2.88,0 c -6.3,0 -8.1,1.62 -8.1,'
    '8.1 l 0,69.84 c 0,6.30002 1.62,8.10002 8.1,8.10002 l 3.96,0 c 6.3'
    ',0 7.92,-1.8 7.92,-7.92002 l 0,-43.02 c 0,-16.38 9.18,-24.3 17.64'
    ',-24.3 7.56,0 9.72,4.32 9.72,14.4 l 0,52.92 c 0,5.58002 1.08,7.92'
    '002 7.92,7.92002 l 4.14,0 c 6.3,0 7.92,-1.8 7.92,-7.92002 z" />\n '
    '   </g>\n  </g>\n</svg>\n<div id="content">\nCONTENT\n</div>\n</body>\n<'
    '/html>'
)


class Page(resource.Resource):
    isLeaf = True
    content = "No plugin claimed the root path."

    def render_GET(self, request):
        return page.replace("CONTENT", self.content).encode("utf8")
