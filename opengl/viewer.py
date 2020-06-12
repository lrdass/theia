import glfw
import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;
out vec3 v_color;
void main()
{
    gl_Position = vec4(a_position, 1.0);
    v_color = a_color;
}
"""

fragment_src = """
# version 330
in vec3 v_color;
out vec4 out_color;
void main()
{
    out_color = vec4(v_color, 1.0);
}
"""


def window_resize(window, width, height):
    gl.glViewport(0, 0, width, height)


# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 400, 200)

# set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

# make the context current
glfw.make_context_current(window)

vertices = [
    -0.5,
    -0.5,
    0.0,
    1.0,
    0.0,
    0.0,
    0.5,
    -0.5,
    0.0,
    0.0,
    1.0,
    0.0,
    -0.5,
    0.5,
    0.0,
    0.0,
    0.0,
    1.0,
    0.5,
    0.5,
    0.0,
    1.0,
    1.0,
    1.0,
    0.0,
    0.75,
    0.0,
    1.0,
    1.0,
    0.0,
]

indices = [0, 1, 2, 1, 2, 3, 2, 3, 4]

vertices = np.array(vertices, dtype=np.float32)
indices = np.array(indices, dtype=np.uint32)

shader = compileProgram(
    compileShader(vertex_src, gl.GL_VERTEX_SHADER),
    compileShader(fragment_src, gl.GL_FRAGMENT_SHADER),
)

# Vertex Buffer Object
VBO = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

# Element Buffer Object
EBO = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

gl.glEnableVertexAttribArray(0)
gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 24, gl.ctypes.c_void_p(0))

gl.glEnableVertexAttribArray(1)
gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 24, gl.ctypes.c_void_p(12))

gl.glUseProgram(shader)
gl.glClearColor(0, 0.1, 0.1, 1)

# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glDrawElements(gl.GL_TRIANGLES, len(indices), gl.GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()
