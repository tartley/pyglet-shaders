#!/usr/bin/python

'''
You should see a big green diamond.
If you see a small red square, then the shaders aren't working.

This green diamond can only appear if your graphics card works with shaders.
'''

from sys import exit

from pyglet import app, gl
from pyglet.window import Window

import fixpath
from shader import FragmentShader, ShaderProgram, VertexShader


def read_source(fname):
    f = open(fname)
    try:
        src = f.read()
    finally:
        f.close()
    print '>>>%r<<<' % (src, )
    return src


def install_shaders():
    fsrc = read_source('allgreen.fsh')
    fshader = FragmentShader(fsrc)

    vsrc = read_source('zoom10rotate45.vsh')
    vshader = VertexShader(vsrc)

    shader = ShaderProgram(fshader, vshader)
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
    install_shaders()

    win = Window(fullscreen=True)
    try:
        win.on_draw = lambda: draw(win)
        app.run()
    finally:
        win.close()


if __name__ == '__main__':
    exit(main())
    
