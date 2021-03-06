from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtOpenGL

import OpenGL.GL as gl
import numpy as np

import sys
import ctypes
import time
import math

from load_shader import load_shaders


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.resize(300, 300)
        self.setWindowTitle("Hello OpenGL App")

        self.glWidget = GLWidget(self)
        self.initGUI()

        timer = QtCore.QTimer(self)
        timer.setInterval(20)
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(gui_layout)
        self.setCentralWidget(central_widget)
        gui_layout.addWidget(self.glWidget)


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.parent = parent

        self.greenValue = 0

    def initializeGL(self) -> None:
        self.program = load_shaders("shader.vert", "shader.frag")

        # positions followed by rgb values
        vertices = np.array([
            0.5, 0.5, 0.0,      1.0, 0.0, 0.0,
            0.5, -0.5, 0.0,     1.0, 1.0, 0.0,
            -0.5, -0.5, 0.0,    0.0, 0.0, 1.0,
            -0.5, 0.5, 0.0,     1.0, 0.0, 1.0
        ], np.float32)
        indices = np.array([
            0, 1, 3,
            1, 2, 3,
        ], np.uint32)

        self.vertex_array = gl.glGenVertexArrays(1)
        self.vertex_buffer = gl.glGenBuffers(1)
        self.element_buffer = gl.glGenBuffers(1)

        # 1. bind Vertex Array Object
        gl.glBindVertexArray(self.vertex_array)
        # 2. copy our vertices array in a buffer for OpenGL to use
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices) * 4, vertices, gl.GL_STATIC_DRAW)
        # 3. copy our index array in a element buffer for OpenGL to use
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, indices, gl.GL_STATIC_DRAW)
        # 4. then set our vertex attributes pointers
        # position attribute
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        # color attribute
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

    def paintGL(self):
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(self.program)

        gl.glBindVertexArray(self.vertex_array)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, ctypes.c_void_p(0))
        gl.glBindVertexArray(0)

    def resizeGL(self, w: int, h: int) -> None:
        gl.glViewport(0, 0, w, h)
        # gl.glMatrixMode(gl.GL_PROJECTION)
        # gl.glLoadIdentity()

        # aspect = w / h
        # GLU.gluPerspective(45, aspect, 1, 100)
        # gl.glMatrixMode(gl.GL_MODELVIEW)

    # def updateGL(self) -> None:
    #     time_value = time.time()
    #     self.greenValue = (math.sin(time_value) / 2) + 0.5
    #     vertex_color_location = gl.glGetUniformLocation(self.program, "ourColor")
    #     gl.glUseProgram()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
