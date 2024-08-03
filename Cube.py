import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import json
import os
from math import sin, cos, radians

# Window Width And Height
WindowWidth = 1024
WindowHeight = 640

# Paths
ObjectsJSONPath = os.path.abspath("./objects/objects.json")

# Camera Transform
CAMERA_X = 0
CAMERA_Y = 0
CAMERA_Z = 500
CAMERA_ROT_X = -90
CAMERA_ROT_Y = 0

class Camera:
    def __init__(self, position, rotation):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.update_vectors()

    def update_vectors(self):
        yaw, pitch = radians(self.rotation[0]), radians(self.rotation[1])
        self.forward = np.array([
            cos(pitch) * cos(yaw),
            sin(pitch),
            cos(pitch) * sin(yaw)
        ], dtype=np.float32)
        self.right = np.array([
            -sin(yaw),
            0,
            cos(yaw)
        ], dtype=np.float32)
        self.up = np.cross(self.right, self.forward)

    def get_view_matrix(self):
        return gluLookAt(
            self.position[0], self.position[1], self.position[2],
            self.position[0] + self.forward[0], self.position[1] + self.forward[1], self.position[2] + self.forward[2],
            self.up[0], self.up[1], self.up[2]
        )

def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)

def get_object_names():
    return list(load_json(ObjectsJSONPath).keys())

def load_cube(name):
    data = load_json(ObjectsJSONPath)
    obj_data = data[name]
    return {
        f"{name}_X": obj_data[0]["X"],
        f"{name}_Y": obj_data[0]["Y"],
        f"{name}_Z": obj_data[0]["Z"],
        f"{name}_Scale": obj_data[0]["Scale"],
        f"{name}_Red": obj_data[0]["Red"],
        f"{name}_Green": obj_data[0]["Green"],
        f"{name}_Blue": obj_data[0]["Blue"],
        f"{name}_Alpha": obj_data[0]["Alpha"]
    }

def create_cube(scale=1):
    scale = scale * 50
    return [(-scale, scale, scale), (scale, scale, scale), (scale, -scale, scale), (-scale, -scale, scale),
            (-scale, scale, -scale), (scale, scale, -scale), (scale, -scale, -scale), (-scale, -scale, -scale)]

def draw_cube(cube_points, color):
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    glBegin(GL_LINES)
    glColor4f(*color)  # Use RGBA color
    for start_index, end_index in edges:
        glVertex3fv(cube_points[start_index])
        glVertex3fv(cube_points[end_index])
    glEnd()

def main():
    global CAMERA_X, CAMERA_Y, CAMERA_Z, CAMERA_ROT_X, CAMERA_ROT_Y, WindowWidth, WindowHeight

    pygame.init()
    pygame.display.set_mode((WindowWidth, WindowHeight), DOUBLEBUF | OPENGL | RESIZABLE)

    # Initial OpenGL setup
    glViewport(0, 0, WindowWidth, WindowHeight)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (WindowWidth / WindowHeight), 0.1, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    camera = Camera([CAMERA_X, CAMERA_Y, CAMERA_Z], [CAMERA_ROT_X, CAMERA_ROT_Y])

    enable_movement = True
    objects_loaded = False
    loaded_objects_list = []
    cube_points_dict = {}

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    sensitivity = 0.1
    move_speed = 5

    paused = False

    while True:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not objects_loaded:
            object_names = get_object_names()
            for name in object_names:
                cube_data = load_cube(name)
                cube_points = create_cube(cube_data[f"{name}_Scale"])
                cube_points_dict[name] = cube_points
                loaded_objects_list.append(name)
            if len(loaded_objects_list) == len(object_names):
                objects_loaded = True

        if objects_loaded:
            glPushMatrix()
            camera.get_view_matrix()
            glScalef(1, -1, -1)  # Flip the Y-axis

            for name in loaded_objects_list:
                cube_data = load_cube(name)
                cube_points = cube_points_dict[name]
                translated_cube_points = [(p[0] + cube_data[f"{name}_X"], p[1] - cube_data[f"{name}_Y"], p[2] - cube_data[f"{name}_Z"]) for p in cube_points]
                color = (
                    cube_data[f"{name}_Red"] / 255,
                    cube_data[f"{name}_Green"] / 255,
                    cube_data[f"{name}_Blue"] / 255,
                    cube_data[f"{name}_Alpha"] / 255
                )
                draw_cube(translated_cube_points, color)
            glPopMatrix()

        keys = pygame.key.get_pressed()
        if keys[K_w] and enable_movement:
            camera.position += move_speed * camera.forward
        if keys[K_s] and enable_movement:
            camera.position -= move_speed * camera.forward
        if keys[K_a] and enable_movement:
            camera.position -= move_speed * camera.right
        if keys[K_d] and enable_movement:
            camera.position += move_speed * camera.right
        if keys[K_SPACE] and enable_movement:
            camera.position += move_speed * camera.up
        if keys[K_LSHIFT] and enable_movement:
            camera.position -= move_speed * camera.up

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.mouse.set_visible(not pygame.mouse.get_visible())
                    pygame.mouse.set_pos([WindowWidth / 2, WindowHeight / 2])
                    pygame.event.set_grab(not pygame.event.get_grab())
                    paused = not paused
                if event.key == K_r:
                    camera.position = np.array([CAMERA_X, CAMERA_Y, CAMERA_Z], dtype=np.float32)
                    camera.rotation = np.array([CAMERA_ROT_X, CAMERA_ROT_Y], dtype=np.float32)
                    enable_movement = True
                    cube_points_dict.clear()
                    loaded_objects_list.clear()
                    objects_loaded = False
                if event.key == K_u:
                    enable_movement = not enable_movement
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == VIDEORESIZE:
                WindowWidth = event.w
                WindowHeight = event.h
                glViewport(0, 0, WindowWidth, WindowHeight)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(45, (WindowWidth / WindowHeight), 0.1, 5000.0)
                glMatrixMode(GL_MODELVIEW)

        mouse_x, mouse_y = pygame.mouse.get_rel()
        if not paused:
            camera.rotation[0] += mouse_x * sensitivity
            camera.rotation[1] -= mouse_y * sensitivity
            camera.rotation[1] = max(-90, min(90, camera.rotation[1]))
            camera.update_vectors()

        pygame.display.flip()
        pygame.time.delay(25)

if __name__ == "__main__":
    main()