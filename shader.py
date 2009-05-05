from ctypes import (
    byref, c_char, c_char_p, c_int, cast, create_string_buffer, pointer,
    POINTER
)
from pyglet.gl import (
	glAttachShader, glCompileShader, glCreateProgram, glCreateShader,
    glGetShaderInfoLog, glGetShaderiv, glLinkProgram, glShaderSource,
    glUseProgram,
    GL_COMPILE_STATUS, GL_DELETE_STATUS, GL_FRAGMENT_SHADER,
    GL_INFO_LOG_LENGTH, GL_INVALID_ENUM,
    GL_INVALID_OPERATION, GL_INVALID_VALUE, GL_SHADER_SOURCE_LENGTH,
    GL_SHADER_TYPE, GL_VERTEX_SHADER
)


class ShaderError(Exception):
    pass


shaderErrors = {
    GL_INVALID_VALUE: 'GL_INVALID_VALUE (1st arg)',
    GL_INVALID_OPERATION: 'GL_INVALID_OPERATION '
        '(bad shader id or immediate mode drawing in progress)',
    GL_INVALID_ENUM: 'GL_INVALID_ENUM (2nd arg)',
}


class _Shader(object):

    type = None

    def __init__(self, sources):
        self.sources = sources
        self.id = None
        
        
    def _getShader(self, paramNum):
        outvalue = c_int(0)
        glGetShaderiv(self.id, paramNum, byref(outvalue))
        value = outvalue.value
        if value in [GL_INVALID_ENUM, GL_INVALID_OPERATION, GL_INVALID_VALUE]:
            msg = '%s from glGetShader(%s, %s, *value)'
            raise ValueError(msg % (shaderErrors[value], self.id, paramNum))
        return value


    def getShaderType(self):
        shader_type = self._getShader(GL_SHADER_TYPE)
        if shader_type == GL_VERTEX_SHADER:
            return VertexShader
        elif shader_type == GL_FRAGMENT_SHADER:
            return FragmentShader


    def getDeleteStatus(self):
        return self._getShader(GL_DELETE_STATUS)


    def getCompileStatus(self):
        return self._getShader(GL_COMPILE_STATUS)


    def getInfoLogLength(self):
        return self._getShader(GL_INFO_LOG_LENGTH)
        

    def getShaderSourceLength(self):
        return self._getShader(GL_SHADER_SOURCE_LENGTH)


    def getShaderInfoLog(self):
        len = self.getInfoLogLength()
        if len == 0:
            return None
        buffer = create_string_buffer(len)
        glGetShaderInfoLog(self.id, len, None, buffer)
        return buffer.value


    def _create(self):
        self.id = glCreateShader(self.type)


    def _shaderSource(self):
        self._create()
        count = len(self.sources)
        all_source = (c_char_p * count)(*self.sources)
        source_array = cast(pointer(all_source), POINTER(POINTER(c_char)))
        glShaderSource(self.id, count, source_array, None)
 

    def compile(self):
        self._shaderSource()
        glCompileShader(self.id)
        if self.getCompileStatus() == False:
            message = self.getShaderInfoLog()
            raise ShaderError(message)



class VertexShader(_Shader):
    type = GL_VERTEX_SHADER


class FragmentShader(_Shader):
    type = GL_FRAGMENT_SHADER



class ShaderProgram(object):

    def __init__(self, *shaders):
        self.shaders = list(shaders)
        self.id = None


    def getLinkStatus(self):
        pass


    def _create(self):
        self.id = glCreateProgram()


    def _compile(self):
        return
        self._create()
        for shader in self.shaders:
            shader.compile()
            glAttachShader(self.id, shader.id)


    def _link(self):
        return
        glLinkProgram(self.id)


    def use(self):
        return
        self._link()
        glUseProgram(self.id)

