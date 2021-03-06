from PyQt5 import QtWidgets

import OpenGL.GL as gl
from OpenGL import GLU
from OpenGL.arrays import vbo       # vertex buffer objects
import numpy as np
import ctypes

from opengl_intro.load_shader import Shader
from opengl_intro.icosphere import Icosphere
import opengl_intro.transformations as trans


class OpenGLRenderArea(QtWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.points = []

        self.distance = 50
        self.radius = 3
        self.scaling = 300

        # Set up a zero array for the angles
        self.angles_3d = [0.0, 0.0, 0.0]
        self.resize(600, 600)

        # opengl settings
        self.light_pos = np.array([-100, 100, 100], np.float32)
        self._use_shading = False

    def initializeGL(self) -> None:
        gl.glEnable(gl.GL_DEPTH_TEST)                   # enable depth testing

        self.lightingShader = Shader("polytope_visualizer/light_shader.vs", "polytope_visualizer/light_shader.fs")
        self.noLightingShader = Shader("polytope_visualizer/no_light_shader.vs", "polytope_visualizer/no_light_shader.fs")
        self.icosphere = Icosphere(2, True)
        vertices = self.icosphere.vertices()

        # first, configure the sphere's VAO and VBO
        self.vertex_array = gl.glGenVertexArrays(1)
        self.vertex_buffer = gl.glGenBuffers(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices) * 4, vertices, gl.GL_STATIC_DRAW)

        gl.glBindVertexArray(self.vertex_array)

        # position attribute
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        # normal attribute
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FLOAT, 6 * 4, ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(1)

    def resizeGL(self, w: int, h: int) -> None:
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        aspect = w / h
        GLU.gluPerspective(45, aspect, 1, 200)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self) -> None:
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if self._use_shading:
            shader = self.lightingShader
            shader.use()
            shader.set_vec3("objectColor", 1.0, 1.0, 1.0)
            shader.set_vec3("lightColor", 1.0, 1.0, 1.0)
            shader.set_vec3v("lightPos", self.light_pos)
        else:
            shader = self.noLightingShader
            shader.use()
            shader.set_vec3("objectColor", 1.0, 1.0, 1.0)

        # view/projection transforms
        projection = trans.perspective(np.radians(45), self.width() / self.height(), 0.1, 100.0)
        view = trans.translate(np.identity(4), np.array((0, 0, -self.distance), np.float32))
        view = trans.rotate(view, np.radians(self.angles_3d[0]), np.array((1, 0, 0), np.float32))
        view = trans.rotate(view, np.radians(self.angles_3d[1]), np.array((0, 1, 0), np.float32))
        view = trans.rotate(view, np.radians(self.angles_3d[2]), np.array((0, 0, 1), np.float32))
        shader.set_mat4("projection", projection)
        shader.set_mat4("view", view)

        gl.glBindVertexArray(self.vertex_array)
        for point in self.points:
            model = np.identity(4)
            model = trans.translate(model, point/40)
            model = trans.scale(model, np.array([self.radius]*3, np.float32))
            shader.set_mat4("model", model)

            # render the cube
            gl.glBindVertexArray(self.vertex_array)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.icosphere.count)

    # Setters
    def set_points(self, points):
        self.points = points
        self.update()

    def set_angle(self, index, value):
        self.angles_3d[index] = value

    def set_scale(self, scale):
        self.scaling = scale

    def set_distance(self, dist):
        self.distance = dist

    def set_radius(self, radius):
        self.radius = radius

    def set_shading(self, shading: bool):
        self._use_shading = shading
