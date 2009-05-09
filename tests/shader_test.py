#!/usr/bin/python

from __future__ import absolute_import

from ctypes import byref, c_int, c_long

from pyglet import gl

from unittest import TestCase, main

from mock import Mock, patch

from sys import path

import fixpath

from shader import CompileError, FragmentShader, LinkError, ShaderProgram, VertexShader


DoNothing = lambda *_: None


def mockGet(returnVal):
    def _mockGet(_, __, p_status):
        p_status._obj.value = returnVal
    return _mockGet


def mockGetInfoLog(returnVal):
    def _mockGetInfoLog(_, __, ___, p_buffer):
        p_buffer.value = returnVal
    return _mockGetInfoLog


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


    @patch('shader.gl')
    def testGet(self, mockGl):
        mockGl.glGetShaderiv.side_effect = mockGet(123)
        shader = VertexShader(['src'])
        shader.id = object()
        
        actual = shader._get(456)

        self.assertEquals(mockGl.glGetShaderiv.call_args[0][:2],
            (shader.id, 456))
        self.assertEquals(actual, 123)


    @patch('shader.gl')
    def testGetRaisesOnError(self, mockGl):
        mockGl.glGetShaderiv.side_effect = mockGet(gl.GL_INVALID_ENUM)
        shader1 = VertexShader(['src'])
        self.assertRaises(ValueError, shader1._get, 456)

        mockGl.glGetShaderiv.side_effect = mockGet(gl.GL_INVALID_OPERATION)
        shader2 = VertexShader(['src'])
        self.assertRaises(ValueError, shader2._get, 456)

        mockGl.glGetShaderiv.side_effect = mockGet(gl.GL_INVALID_VALUE)
        shader3 = VertexShader(['src'])
        self.assertRaises(ValueError, shader3._get, 456)


    def testGetCompileStatus(self):
        data = [
            (gl.GL_TRUE, True),
            (gl.GL_FALSE, False),
        ]
        for getReturn, expected in data:
            shader = FragmentShader(['src'])
            shader._get = Mock(return_value=getReturn)

            actual = shader.getCompileStatus()

            self.assertEquals(shader._get.call_args,
                ((gl.GL_COMPILE_STATUS,), {}))
            self.assertEquals(actual, expected)
            self.assertEquals(type(actual), type(expected))


    def testGetInfoLogLength(self):
        shader = VertexShader(['src'])
        shader._get = Mock(return_value=123)

        actual = shader.getInfoLogLength()

        self.assertEquals(shader._get.call_args, ((gl.GL_INFO_LOG_LENGTH,), {}))
        self.assertEquals(actual, 123)


    @patch('shader.gl')
    def testGetInfoLog(self, mockGl):
        expected = 'logmessage'
        mockGl.glGetShaderInfoLog.side_effect = mockGetInfoLog(expected)
        shader = VertexShader(['src'])
        shader.getInfoLogLength = lambda: len(expected)

        log = shader.getInfoLog()

        self.assertEquals(log, expected)


    def testGetInfoLogForZeroLogSize(self):
        shader = VertexShader(['src'])
        shader.getInfoLogLength = lambda: 0

        log = shader.getInfoLog()

        self.assertEquals(log, None)


    @patch('shader.gl')
    def testCompileCreatesShaders(self, mockGl):
        mockGl.glCreateShader.return_value = 123
        shader = VertexShader(['src'])
        shader.getCompileStatus = lambda: True
        shader.getInfoLog = DoNothing
        
        shader.compile()

        self.assertTrue(mockGl.glCreateShader.called)
        self.assertEquals(mockGl.glCreateShader.call_args[0], (shader.type,))
        self.assertEquals(shader.id, 123)


    @patch('shader.gl')
    def testCompileSetsShaderSource(self, mockGl):
        sources = ['one', 'two', 'three']
        shader = VertexShader(sources)
        shader.getCompileStatus = lambda: True
        shader.getInfoLog = DoNothing

        shader.compile()

        args = mockGl.glShaderSource.call_args[0]
        self.assertEquals(args[:2], (shader.id, 3))
        dirarg = args[2]._objects['0']
        actualSources = [dirarg[key] for key in sorted(dirarg.keys())]
        self.assertEquals(actualSources, sources)
        self.assertTrue(args[3] is None)
    

    @patch('shader.gl')
    def testCompileCompilesShader(self, mockGl):
        shader = VertexShader(['src'])
        shader.getCompileStatus = lambda: True
        shader.getInfoLog = lambda: 'compilemessage'
        message = shader.compile()

        self.assertEquals(mockGl.glCompileShader.call_args[0], (shader.id,))
        self.assertTrue('compilemessage' in message)


    @patch('shader.gl', Mock())
    def testCompileRaisesOnFail(self):
        shader = VertexShader(['badsrc'])
        shader.getCompileStatus = lambda: False
        shader.getInfoLog = lambda: 'errormessage'
        try:
            shader.compile()
            self.fail('should raise')
        except CompileError, e:
            self.assertTrue('errormessage' in str(e))
        except:
            self.fail('should raise a CompileError')



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


    @patch('shader.gl.glGetProgramiv')
    def testGet(self, mockGlGetProgram):
        mockGlGetProgram.side_effect = mockGet(123)
        program = ShaderProgram()
        program.id = object()

        actual = program._get(456)

        self.assertEquals(mockGlGetProgram.call_args[0][:2], (program.id, 456))
        self.assertEquals(actual, 123)


    @patch('shader.gl.glGetProgramiv')
    def testGetRaisesOnError(self, mockGlGetProgram):
        mockGlGetProgram.side_effect = mockGet(gl.GL_INVALID_ENUM)
        program1 = ShaderProgram()
        self.assertRaises(ValueError, program1._get, 456)

        mockGlGetProgram.side_effect = mockGet(gl.GL_INVALID_OPERATION)
        program2 = ShaderProgram()
        self.assertRaises(ValueError, program2._get, 456)

        mockGlGetProgram.side_effect = mockGet(gl.GL_INVALID_VALUE)
        program3 = ShaderProgram()
        self.assertRaises(ValueError, program3._get, 456)


    def testGetLinkStatus(self):
        data = [
            (gl.GL_TRUE, True),
            (gl.GL_FALSE, False),
        ]
        for getReturn, expected in data:
            program = ShaderProgram()
            program._get = Mock(return_value=getReturn)

            actual = program.getLinkStatus()

            self.assertEquals(program._get.call_args,
                ((gl.GL_LINK_STATUS,), {}))
            self.assertEquals(actual, expected)
            self.assertEquals(type(actual), type(expected))  
            

    def testGetProgramInfoLogLength(self):
        program = ShaderProgram()
        program._get = Mock(return_value=123)

        actual = program.getInfoLogLength()

        self.assertEquals(program._get.call_args,
            ((gl.GL_INFO_LOG_LENGTH,), {}))
        self.assertEquals(actual, 123)


    @patch('shader.gl.glGetProgramInfoLog')
    def testGetProgramInfoLog(self, mockGetLog):
        expected = 'logmessage'
        mockGetLog.side_effect = mockGetInfoLog(expected)
        program = ShaderProgram()
        program.getInfoLogLength = lambda: len(expected)

        log = program.getProgramInfoLog()

        self.assertEquals(log, expected)


    def testGetProgramInfoLogForZeroLogSize(self):
        program = ShaderProgram()
        program.getInfoLogLength = lambda: 0

        log = program.getProgramInfoLog()

        self.assertEquals(log, None)
        
            
    @patch('shader.gl.glCreateProgram')
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram', DoNothing)
    def testUseCreatesProgram(self, mock):
        mock.return_value = 123
        program = ShaderProgram()
        program.getLinkStatus = lambda: True
        
        program.use()

        self.assertTrue(mock.called)
        self.assertEquals(program.id, 123)


    @patch('shader.gl.glAttachShader')
    @patch('shader.gl.glCreateProgram', DoNothing)
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram', DoNothing)
    def testUseCompilesAndAttachesShaders(self, mock):
        shader1 = Mock()
        shader2 = Mock()
        program = ShaderProgram(shader1, shader2)
        program.id = 123
        program.getLinkStatus = lambda: True
        
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
        program.getLinkStatus = lambda: True

        program.use()

        self.assertEquals(mock.call_args, ((program.id,), {}))
        self.fail('and returns infolog text')


    @patch('shader.gl.glCreateProgram', DoNothing)
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram', DoNothing)
    def testUseRaisesOnLinkFailure(self):
        program = ShaderProgram()
        program.getLinkStatus = lambda: False
        program.getProgramInfoLog = lambda: 'errormessage'
        try:
            program.use()
            self.fail('should raise')
        except LinkError, e:
            self.assertTrue('errormessage' in str(e))
        except:
            self.fail('should raise a LinkError')


    @patch('shader.gl.glCreateProgram', DoNothing)
    @patch('shader.gl.glLinkProgram', DoNothing)
    @patch('shader.gl.glUseProgram')
    def testUseUsesTheShaderProgram(self, mock):
        program = ShaderProgram()
        program.getLinkStatus = lambda: True
        
        program.use()

        self.assertEquals(mock.call_args, ((program.id,), {}))


    def testDispose(self):
        self.fail()


if __name__ == '__main__':
    main()

