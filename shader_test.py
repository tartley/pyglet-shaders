#!/usr/bin/python

from ctypes import byref, c_int, c_long

from pyglet.gl import (
    glGetShaderiv,
    GL_COMPILE_STATUS, GL_DELETE_STATUS, GL_FALSE, GL_FRAGMENT_SHADER,
    GL_INFO_LOG_LENGTH, GL_INVALID_ENUM, 
    GL_INVALID_OPERATION, GL_INVALID_VALUE, GL_SHADER_SOURCE_LENGTH, 
    GL_SHADER_TYPE, GL_TRUE,
    GL_VERTEX_SHADER,
)

from unittest import TestCase, main

from mock import Mock, patch

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
        self.assertEqual(shader.type, GL_VERTEX_SHADER)
        self.assertTrue(shader.id is None)
        self.assertEquals(shader.sources, ['src'])


    def testInitFragmentShader(self):
        shader = FragmentShader(['src'])
        self.assertEqual(shader.type, GL_FRAGMENT_SHADER)
        self.assertTrue(shader.id is None)
        self.assertEquals(shader.sources, ['src'])


    @patch('shader.glGetShaderiv')
    def testGetShader(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(123)
        shader = VertexShader(['src'])
        self.assertEquals(shader._getShader(456), 123)
        self.assertEquals(mockGlGetShader.call_args[0][:2], (shader.id, 456))


    @patch('shader.glGetShaderiv')
    def testGetShaderRaisesOnError(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(GL_INVALID_ENUM)
        shader1 = VertexShader(['src'])
        self.assertRaises(ValueError, shader1._getShader, 456)

        mockGlGetShader.side_effect = mockGetShader(GL_INVALID_OPERATION)
        shader2 = VertexShader(['src'])
        self.assertRaises(ValueError, shader2._getShader, 456)

        mockGlGetShader.side_effect = mockGetShader(GL_INVALID_VALUE)
        shader3 = VertexShader(['src'])
        self.assertRaises(ValueError, shader3._getShader, 456)


    @patch('shader.glGetShaderiv')
    def testGetShaderType(self, mockGlGetShader):
        data = [
            (GL_VERTEX_SHADER, VertexShader),
            (GL_FRAGMENT_SHADER, FragmentShader),
        ]
        for glResult, expectedResult in data:
            mockGlGetShader.side_effect = mockGetShader(glResult)
            shader = VertexShader(['src'])

            actual = shader.getShaderType()

            self.assertEquals(actual, expectedResult)
            self.assertEquals(mockGlGetShader.call_args[0][:2],
                (shader.id, GL_SHADER_TYPE))


    @patch('shader.glGetShaderiv')
    def testGetDeleteStatus(self, mockGlGetShader):
        data = [
            (GL_TRUE, True),
            (GL_FALSE, False),
        ]
        for glResult, expectedResult in data:
            mockGlGetShader.side_effect = mockGetShader(glResult)
            shader = VertexShader(['src'])

            actual = shader.getDeleteStatus()

            self.assertEquals(actual, expectedResult)
            self.assertEquals(mockGlGetShader.call_args[0][:2],
                (shader.id, GL_DELETE_STATUS))


    @patch('shader.glGetShaderiv')
    def testGetCompileStatus(self, mockGlGetShader):
        data = [
            (GL_TRUE, True),
            (GL_FALSE, False),
        ]
        for glResult, expectedResult in data:
            mockGlGetShader.side_effect = mockGetShader(glResult)
            shader = VertexShader(['src'])

            actual = shader.getCompileStatus()

            self.assertEquals(actual, expectedResult)
            self.assertEquals(mockGlGetShader.call_args[0][:2],
                (shader.id, GL_COMPILE_STATUS))


    @patch('shader.glGetShaderiv')
    def testGetInfoLogLength(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(123)
        shader = VertexShader(['src'])

        actual = shader.getInfoLogLength()

        self.assertEquals(actual, 123)
        self.assertEquals(mockGlGetShader.call_args[0][:2],
            (shader.id, GL_INFO_LOG_LENGTH))


    @patch('shader.glGetShaderiv')
    def testGetShaderSourceLength(self, mockGlGetShader):
        mockGlGetShader.side_effect = mockGetShader(123)
        shader = VertexShader(['src'])

        actual = shader.getShaderSourceLength()

        self.assertEquals(actual, 123)
        self.assertEquals(mockGlGetShader.call_args[0][:2],
            (shader.id, GL_SHADER_SOURCE_LENGTH))


    @patch('shader.glGetShaderInfoLog')
    def testGetShaderInfoLog(self, mockGetLog):
        mockGetLog.side_effect = mockGetShaderInfoLog('abcd')
        shader = VertexShader(['src'])
        shader.getInfoLogLength = lambda: 4

        log = shader.getShaderInfoLog()

        self.assertEquals(log, 'abcd')


    @patch('shader.glGetShaderInfoLog')
    def testGetShaderInfoLogForZeroLogSize(self, mockGetLog):
        mockGetLog.side_effect = mockGetShaderInfoLog('')
        shader = VertexShader(['src'])
        shader.getInfoLogLength = lambda: 0

        log = shader.getShaderInfoLog()

        self.assertEquals(log, None)


    @patch('shader.glCreateShader')
    def testCreate(self, mock):
        mock.return_value = 123
        shader = VertexShader(['src'])
        shader._create()
        self.assertTrue(mock.called)
        self.assertEquals(mock.call_args[0], (shader.type,))
        self.assertEquals(shader.id, 123)


    @patch('shader.glShaderSource')
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


    @patch('shader.glShaderSource', DoNothing)
    def testShaderSourceCreates(self):
        shader = VertexShader(['src'])
        shader._create = Mock()
        shader._shaderSource()
        self.assertTrue(shader._create.called)
    

    @patch('shader.glCompileShader')
    def testCompile(self, mock):
        shader = VertexShader(['src'])
        shader._shaderSource = DoNothing
        shader.getCompileStatus = lambda: True

        shader.compile()

        self.assertEquals(mock.call_args[0], (shader.id,))


    @patch('shader.glCompileShader', DoNothing)
    def testCompileSetsShaderSource(self):
        shader = VertexShader(['src'])
        shader._shaderSource = Mock()
        shader.getCompileStatus = lambda: True

        shader.compile()

        self.assertTrue(shader._shaderSource.called)


    @patch('shader.glCompileShader', DoNothing)
    def testCompileRaisesOnFail(self):
        shader = VertexShader(['badsrc'])
        shader._shaderSource = DoNothing
        shader.getCompileStatus = lambda: False
        shader.getShaderInfoLog = lambda: 'hated badsrc'
        try:
            shader.compile()
            self.fail('should raise')
        except ShaderError, e:
            self.assertTrue(len(str(e)) > 10)
            self.assertTrue('badsrc' in str(e))


VERTEX_SOURCE = '''
void main():
{
    gl_Position = gl_Vertex;
}
'''

FRAGMENT_SOURCE = '''
void main():
{
    gl_FragColor = vec4(1.0, 0.0. 0.0, 1.0);
}
'''

BAD_SOURCE = '''
asdf
'''


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

        p = ShaderProgram(s1, s2, s3)
        self.assertTrue(p.id is None)
        self.assertEqual(p.shaders, [s1, s2, s3])


    @patch('shader.glCreateProgram')
    def testCreate(self, mock):
        mock.return_value = 123
        program = ShaderProgram()
        program._create()
        self.assertTrue(mock.called)
        self.assertEquals(program.id, 123)


    @patch('shader.glAttachShader')
    @patch('shader.glUseProgram', DoNothing)
    def testUseWillAttachShaders(self, mock):
        shader1 = Mock()
        shader2 = Mock()
        shader3 = Mock()
        program = ShaderProgram(shader1, shader2, shader3)

        program.use()

        expected = [
            ((program.id, shader1.id), {}),
            ((program.id, shader2.id), {}),
            ((program.id, shader3.id), {}),
        ]
        self.assertEquals(mock.call_args_list, expected)


    @patch('shader.glAttachShader', DoNothing)
    @patch('shader.glUseProgram', DoNothing)
    def testUseWillCompileShaders(self):
        shader1 = Mock()
        shader2 = Mock()
        shader3 = Mock()
        program = ShaderProgram(shader1, shader2, shader3)

        program.use()

        self.assertTrue(shader1.compile.called)
        self.assertTrue(shader2.compile.called)
        self.assertTrue(shader3.compile.called)


    def DONTtestCompile(self):
        #self.fail()
        pass


    @patch('shader.glUseProgram')
    def DONTtestUse(self, mock):
        shader1 = FragmentShader(FRAGMENT_SOURCE)
        shader2 = VertexShader(VERTEX_SOURCE)
        program = ShaderProgram(shader1, shader2)
        program.link = DoNothing
        
        program.use()

        self.assertEquals(mock.call_args, (program.id,))


    @patch('shader.glUseProgram', DoNothing)
    def DONTtestUseWillLinkIfReqd(self):
        shader = FragmentShader(FRAGMENT_SOURCE)
        program = ShaderProgram(shader)
        program.link = Mock()

        program.getLinkStatus = lambda: True
        program.use()
        self.assertFalse(program.link.called)

        program.getLinkStatus = lambda: False
        program.use()
        self.assertTrue(program.link.called)


    @patch('shader.glLinkProgram')
    def DONTtestLink(self, mock):
        shader = FragmentShader(FRAGMENT_SOURCE)
        program = ShaderProgram(shader)
        program.getCompileStatus = lambda: True

        program.link()

        self.assertEquals(mock.call_args, (program.id,))


    def DONTtestCompileError(self):
        shader = FragmentShader(BAD_SOURCE)
        sp = ShaderProgram(shader)
        self.assertRaises(Exception, sp.use)


if __name__ == '__main__':
    main()

