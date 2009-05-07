#!/usr/bin/python

from __future__ import absolute_import

from ctypes import byref, c_int, c_long

from pyglet import gl

from unittest import TestCase, main

from mock import Mock, patch

from sys import path

import fixpath

from shader import ShaderError, FragmentShader, ShaderProgram, VertexShader


DoNothing = lambda *_: None


def mockGetShader(returnVal):
    def _mockGetShader(_, __, p_status):
        p_status._obj.value = returnVal
    return _mockGetShader


def mockGetShaderInfoLog(returnVal):
    def _mockGetShaderInfoLog(_, __, ___, p_buffer):
        p_buffer.value = returnVal
    return _mockGetShaderInfoLog


class ShaderTest(TestCase):

    def testInitVertexShader(self):
        shader = VertexShader(['src'])
        self.assertEqual(shader.type, gl.GL_VERTEX_SHADER)
        self.assertTrue(shader.id is None)
        self.assertEquals(shader.sources, ['src'])


    def testInitFragmentShader(self):
        shader = FragmentShader(['src'])
        self.assertEqual(shader.type, gl.GL_FRAGMENT_SHADER)
        self.assertTrue(shader.id is None)
        self.assertEquals(shader.sources, ['src'])


    @patch('shader.gl.glGetShaderiv')
    def testGet(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(123)
        shader = VertexShader(['src'])
        self.assertEquals(shader._get(456), 123)
        self.assertEquals(mockGlGetShader.call_args[0][:2], (shader.id, 456))


    @patch('shader.gl.glGetShaderiv')
    def testGetShaderRaisesOnError(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(gl.GL_INVALID_ENUM)
        shader1 = VertexShader(['src'])
        self.assertRaises(ValueError, shader1._get, 456)

        mockGlGetShader.side_effect = mockGetShader(gl.GL_INVALID_OPERATION)
        shader2 = VertexShader(['src'])
        self.assertRaises(ValueError, shader2._get, 456)

        mockGlGetShader.side_effect = mockGetShader(gl.GL_INVALID_VALUE)
        shader3 = VertexShader(['src'])
        self.assertRaises(ValueError, shader3._get, 456)


    @patch('shader.gl.glGetShaderiv')
    def testGetCompileStatus(self, mockGlGetShader):
        data = [
            (gl.GL_TRUE, True),
            (gl.GL_FALSE, False),
        ]
        for glResult, expectedResult in data:
            mockGlGetShader.side_effect = mockGetShader(glResult)
            shader = VertexShader(['src'])

            actual = shader.getCompileStatus()

            self.assertEquals(actual, expectedResult)
            self.assertEquals(mockGlGetShader.call_args[0][:2],
                (shader.id, gl.GL_COMPILE_STATUS))


    @patch('shader.gl.glGetShaderiv')
    def testGetInfoLogLength(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(123)
        shader = VertexShader(['src'])

        actual = shader.getInfoLogLength()

        self.assertEquals(actual, 123)
        self.assertEquals(mockGlGetShader.call_args[0][:2],
            (shader.id, gl.GL_INFO_LOG_LENGTH))


    @patch('shader.gl.glGetShaderInfoLog')
    def testGetShaderInfoLog(self, mockGetLog):
        mockGetLog.side_effect = mockGetShaderInfoLog('abcd')
        shader = VertexShader(['src'])
        shader.getInfoLogLength = lambda: 4

        log = shader.getShaderInfoLog()

        self.assertEquals(log, 'abcd')


    @patch('shader.gl.glGetShaderInfoLog')
    def testGetShaderInfoLogForZeroLogSize(self, mockGetLog):
        mockGetLog.side_effect = mockGetShaderInfoLog('')
        shader = VertexShader(['src'])
        shader.getInfoLogLength = lambda: 0

        log = shader.getShaderInfoLog()

        self.assertEquals(log, None)


    @patch('shader.gl.glCreateShader')
    def testCreate(self, mock):
        mock.return_value = 123
        shader = VertexShader(['src'])
        shader._create()
        self.assertTrue(mock.called)
        self.assertEquals(mock.call_args[0], (shader.type,))
        self.assertEquals(shader.id, 123)


    @patch('shader.gl.glShaderSource')
    def testShaderSource(self, mock):
        sources = ['one', 'two', 'three']
        shader = VertexShader(sources)

        shader._shaderSource()

        args = mock.call_args[0]
        self.assertEquals(args[:2], (shader.id, 3))
        dirarg = args[2]._objects['0']
        actualSources = [dirarg[key] for key in sorted(dirarg.keys())]
        self.assertEquals(actualSources, sources)
        self.assertTrue(args[3] is None)


    @patch('shader.gl.glShaderSource', DoNothing)
    def testShaderSourceCreates(self):
        shader = VertexShader(['src'])
        shader._create = Mock()
        shader._shaderSource()
        self.assertTrue(shader._create.called)
    

    @patch('shader.gl.glCompileShader')
    def testCompile(self, mock):
        shader = VertexShader(['src'])
        shader._shaderSource = DoNothing
        shader.getCompileStatus = lambda: True

        shader.compile()

        self.assertEquals(mock.call_args[0], (shader.id,))


    @patch('shader.gl.glCompileShader', DoNothing)
    def testCompileSetsShaderSource(self):
        shader = VertexShader(['src'])
        shader._shaderSource = Mock()
        shader.getCompileStatus = lambda: True

        shader.compile()

        self.assertTrue(shader._shaderSource.called)


    @patch('shader.gl.glCompileShader', DoNothing)
    def testCompileRaisesOnFail(self):
        shader = VertexShader(['badsrc'])
        shader._shaderSource = DoNothing
        shader.getCompileStatus = lambda: False
        shader.getShaderInfoLog = lambda: 'errormessage'
        try:
            shader.compile()
            self.fail('should raise')
        except ShaderError, e:
            self.assertTrue(len(str(e)) > 10)
            self.assertTrue('errormessage' in str(e))



class ShaderProgramTest(TestCase):

    def testInit(self):
        s1 = FragmentShader(['src'])
        s2 = FragmentShader(['src'])
        s3 = FragmentShader(['src'])

        p = ShaderProgram()
        self.assertTrue(p.id is None)
        self.assertEqual(p.shaders, [])

        p = ShaderProgram(s1)
        self.assertTrue(p.id is None)
        self.assertEqual(p.shaders, [s1])

        p = ShaderProgram(s1, s2)
        self.assertTrue(p.id is None)
        self.assertEqual(p.shaders, [s1, s2])


    @patch('shader.gl.glCreateProgram')
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram', DoNothing)
    def testUseCreatesProgram(self, mock):
        mock.return_value = 123
        program = ShaderProgram()
        
        program.use()

        self.assertTrue(mock.called)
        self.assertEquals(program.id, 123)


    @patch('shader.gl.glAttachShader')
    @patch('shader.gl.glCreateProgram', DoNothing)
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram', DoNothing)
    def testUseCompilesAndAttachesShadersCompile(self, mock):
        shader1 = Mock()
        shader2 = Mock()
        program = ShaderProgram(shader1, shader2)
        program.id = 123
        
        program.use()

        self.assertEquals(shader1.compile.call_args, (tuple(), {}))
        self.assertEquals(shader2.compile.call_args, (tuple(), {}))
        self.assertEquals(mock.call_args_list, [
            ((program.id, shader1.id), {}),
            ((program.id, shader2.id), {}),
        ])


    @patch('shader.gl.glCreateProgram', DoNothing)
    @patch('shader.gl.glLinkProgram')
    @patch('shader.gl.glUseProgram', DoNothing)
    def testUseLinksTheShaderProgram(self, mock):
        program = ShaderProgram()

        program.use()

        self.assertEquals(mock.call_args, ((program.id,), {}))


    def testUseRaisesOnLinkFailure(self):
        self.fail()


    @patch('shader.gl.glCreateProgram', DoNothing)
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram')
    def testUseUsesTheShaderProgram(self, mock):
        program = ShaderProgram()
        program._link = DoNothing
        
        program.use()

        self.assertEquals(mock.call_args, ((program.id,), {}))


    def testDispose(self):
        self.fail()


if __name__ == '__main__':
    main()

