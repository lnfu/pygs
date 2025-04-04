import numpy as np
import glfw
from pyglm import glm
from OpenGL.GL import *
import plyfile
from shader import Shader

WIDTH = 800
HEIGHT = 800
SH_C0 = 0.28209479177387814

vertex_data = np.array([-0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5], dtype=np.float32)


def main():
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")
    window = glfw.create_window(
        WIDTH, HEIGHT, title="Gaussian Splatting", monitor=None, share=None
    )
    if not window:
        glfw.terminate()
        raise RuntimeError("GLFW window creation failed")

    glfw.make_context_current(window)  # 把 OpenGL context 設成目前的 window

    ply_data = plyfile.PlyData.read("splats/christmas_tree.ply")

    num_instances = len(ply_data["vertex"])
    instance_data = (
        np.stack(
            [
                np.array(ply_data["vertex"]["x"]),
                np.array(ply_data["vertex"]["y"]),
                np.array(ply_data["vertex"]["z"]),
                np.array(ply_data["vertex"]["scale_0"]),
                np.array(ply_data["vertex"]["scale_1"]),
                np.array(ply_data["vertex"]["scale_2"]),
                np.array(ply_data["vertex"]["rot_0"]),
                np.array(ply_data["vertex"]["rot_1"]),
                np.array(ply_data["vertex"]["rot_2"]),
                np.array(ply_data["vertex"]["rot_3"]),
                np.array(ply_data["vertex"]["f_dc_0"]) * SH_C0 + 0.5,
                np.array(ply_data["vertex"]["f_dc_1"]) * SH_C0 + 0.5,
                np.array(ply_data["vertex"]["f_dc_2"]) * SH_C0 + 0.5,
                1 / (1 + np.exp(-np.array(ply_data["vertex"]["opacity"]))),
            ],
            axis=1,
        )
        .reshape(-1)
        .astype(np.float32)
    )

    print("OpenGL version:", glGetString(GL_VERSION))
    print("Num instances:", num_instances)

    glViewport(0, 0, WIDTH, HEIGHT)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # TODO???
    # glDisable(GL_DEPTH_TEST) # TODO

    # Shader
    default_shader = Shader(
        "shaders/default_vertex.glsl", "shaders/default_fragment.glsl"
    )
    default_shader.activate()

    view = np.array(
        glm.lookAt(glm.vec3(-50, 0, 0), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0)),
        dtype=np.float32,
    )
    projection = np.array(
        glm.perspective(glm.radians(90), WIDTH / HEIGHT, 0.1, 50), dtype=np.float32
    )

    u_view = glGetUniformLocation(default_shader.program, "uView")
    u_projection = glGetUniformLocation(default_shader.program, "uProjection")

    # column-major
    glUniformMatrix4fv(u_view, 1, GL_FALSE, view)
    glUniformMatrix4fv(u_projection, 1, GL_FALSE, projection)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)
    a_pos = glGetAttribLocation(default_shader.program, "aPos")
    glVertexAttribPointer(
        a_pos,
        2,
        GL_FLOAT,
        GL_FALSE,
        2 * np.dtype(np.float32).itemsize,
        ctypes.c_void_p(0),
    )
    glEnableVertexAttribArray(a_pos)

    instance_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance_buffer)
    glBufferData(
        GL_ARRAY_BUFFER,
        instance_data.nbytes,
        instance_data,
        GL_STATIC_DRAW,
    )
    a_instance_pos = glGetAttribLocation(default_shader.program, "aInstancePos")
    a_instance_scale = glGetAttribLocation(default_shader.program, "aInstanceScale")
    a_instance_rot = glGetAttribLocation(default_shader.program, "aInstanceRot")
    a_instance_color = glGetAttribLocation(default_shader.program, "aInstanceColor")
    stride = (3 + 3 + 4 + 4) * np.dtype(np.float32).itemsize
    offset = 0
    glVertexAttribPointer(
        a_instance_pos,
        3,
        GL_FLOAT,
        GL_FALSE,
        stride,
        ctypes.c_void_p(offset),
    )
    glVertexAttribDivisor(a_instance_pos, 1)
    offset += 3 * np.dtype(np.float32).itemsize

    glVertexAttribPointer(
        a_instance_scale,
        3,
        GL_FLOAT,
        GL_FALSE,
        stride,
        ctypes.c_void_p(offset),
    )
    glVertexAttribDivisor(a_instance_scale, 1)
    offset += 3 * np.dtype(np.float32).itemsize

    glVertexAttribPointer(
        a_instance_rot,
        4,
        GL_FLOAT,
        GL_FALSE,
        stride,
        ctypes.c_void_p(offset),
    )
    glVertexAttribDivisor(a_instance_rot, 1)
    offset += 4 * np.dtype(np.float32).itemsize

    glVertexAttribPointer(
        a_instance_color,
        4,
        GL_FLOAT,
        GL_FALSE,
        stride,
        ctypes.c_void_p(offset),
    )
    glVertexAttribDivisor(a_instance_color, 1)
    offset += 4 * np.dtype(np.float32).itemsize

    glEnableVertexAttribArray(a_instance_pos)
    glEnableVertexAttribArray(a_instance_scale)
    glEnableVertexAttribArray(a_instance_rot)
    glEnableVertexAttribArray(a_instance_color)

    while not glfw.window_should_close(window):
        glClearColor(0.07, 0.28, 0.17, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        default_shader.activate()

        glBindVertexArray(vao)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, 4, num_instances)

        glfw.swap_buffers(window)

        glfw.poll_events()

    glDeleteBuffers(2, [vertex_buffer, instance_buffer])
    glDeleteVertexArrays(1, [vao])

    default_shader.delete()
    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
