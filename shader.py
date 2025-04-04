import OpenGL.GL.shaders as shaders
from OpenGL.GL import *


def load_shader_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


class Shader:
    program: shaders.ShaderProgram

    def __init__(self, vertex_shader_file_path: str, fragment_shader_file_path: str):
        vertex_shader = shaders.compileShader(
            load_shader_file(vertex_shader_file_path), GL_VERTEX_SHADER
        )
        fragment_shader = shaders.compileShader(
            load_shader_file(fragment_shader_file_path), GL_FRAGMENT_SHADER
        )
        self.program = shaders.compileProgram(vertex_shader, fragment_shader)
        glLinkProgram(self.program)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def activate(self):
        glUseProgram(self.program)

    def delete(self):
        glDeleteProgram(self.program)
