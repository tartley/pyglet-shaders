#!/usr/bin/python

'''
This source draws a small red square from (0,0) to (10, 10)
If the vertex and fragment shaders are working properly,
it should be transformed into a large (100pixel) green diamond.
'''

from sys import exit

from pyglet import app, gl
from pyglet.window import Window

import fixpath
from shader import FragmentShader, ShaderError, ShaderProgram, VertexShader


def read_source(fname):
    f = open(fname)
    try:
        src = f.read()
    finally:
        f.close()
    return src


def install_shaders():
    fsrc = read_source('allgreen.fsh')
    fshader = FragmentShader(fsrc)

    vsrc = read_source('zoom10rotate45.vsh')
    vshader = VertexShader(vsrc)

    shader = ShaderProgram(vshader, fshader)
    shader.use()


def draw(win):
    win.clear()
    gl.glColor3ub(255, 0, 0)

    gl.glBegin(gl.GL_TRIANGLES)

    gl.glVertex2f(0, 0)
    gl.glVertex2f(10, 0)
    gl.glVertex2f(0, 10)

    gl.glVertex2f(0, 10)
    gl.glVertex2f(10, 0)
    gl.glVertex2f(10, 10)

    gl.glEnd()


def main():
    try:
        install_shaders()
    except ShaderError, e:
        print '%s: %s' %(type(e).__name__, str(e))
        return 2
        
    win = Window(fullscreen=True)
    try:
        win.on_draw = lambda: draw(win)
        app.run()
    finally:
        win.close()


if __name__ == '__main__':
    exit(main())
