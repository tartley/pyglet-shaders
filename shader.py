from ctypes import (
    byref, c_char, c_char_p, c_int, cast, create_string_buffer, pointer,
    POINTER
)
from pyglet import gl


class ShaderError(Exception):
    pass


shaderErrors = {
    gl.GL_INVALID_VALUE: 'GL_INVALID_VALUE (1st arg)',
    gl.GL_INVALID_OPERATION: 'GL_INVALID_OPERATION '
        '(bad shader id or immediate mode drawing in progress)',
    gl.GL_INVALID_ENUM: 'GL_INVALID_ENUM (2nd arg)',
}


class _Shader(object):

    type = None

    def __init__(self, sources):
        self.sources = sources
        self.id = None
        
        
    def _getShader(self, paramNum):
        outvalue = c_int(0)
        gl.glGetShaderiv(self.id, paramNum, byref(outvalue))
        value = outvalue.value
        if value in shaderErrors.keys():
            msg = '%s from glGetShader(%s, %s, *value)'
            raise ValueError(msg % (shaderErrors[value], self.id, paramNum))
        return value


    def getShaderType(self):
        shader_type = self._getShader(gl.GL_SHADER_TYPE)
        if shader_type == gl.GL_VERTEX_SHADER:
            return VertexShader
        elif shader_type == gl.GL_FRAGMENT_SHADER:
            return FragmentShader


    def getDeleteStatus(self):
        return self._getShader(gl.GL_DELETE_STATUS)


    def getCompileStatus(self):
        return self._getShader(gl.GL_COMPILE_STATUS)


    def getInfoLogLength(self):
        return self._getShader(gl.GL_INFO_LOG_LENGTH)
        

    def getShaderSourceLength(self):
        return self._getShader(gl.GL_SHADER_SOURCE_LENGTH)


    def getShaderInfoLog(self):
        len = self.getInfoLogLength()
        if len == 0:
            return None
        buffer = create_string_buffer(len)
        gl.glGetShaderInfoLog(self.id, len, None, buffer)
        return buffer.value


    def _create(self):
        self.id = gl.glCreateShader(self.type)


    def _shaderSource(self):
        self._create()
        count = len(self.sources)
        all_source = (c_char_p * count)(*self.sources)
        source_array = cast(pointer(all_source), POINTER(POINTER(c_char)))
        gl.glShaderSource(self.id, count, source_array, None)
 

    def compile(self):
        self._shaderSource()
        gl.glCompileShader(self.id)
        if self.getCompileStatus() == False:
            message = self.getShaderInfoLog()
            raise ShaderError(message)



class VertexShader(_Shader):
    type = gl.GL_VERTEX_SHADER


class FragmentShader(_Shader):
    type = gl.GL_FRAGMENT_SHADER



class ShaderProgram(object):

    def __init__(self, *shaders):
        self.shaders = list(shaders)
        self.id = None


    def getLinkStatus(self):
        pass


    def _create(self):
        self.id = gl.glCreateProgram()


    def _compile(self):
        return
        self._create()
        for shader in self.shaders:
            shader.compile()
            gl.glAttachShader(self.id, shader.id)


    def _link(self):
        return
        gl.glLinkProgram(self.id)


    def use(self):
        return
        self._link()
        gl.glUseProgram(self.id)

