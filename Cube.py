import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import json
import os
from math import sin, cos, radians

#Window Width And Height
WindowWidth = 1024
WindowHeight = 640

# Paths
ObjectsJSONPath = os.path.abspath("./objects/objects.json")

# Camera Transform
CAMERA_X = 0
CAMERA_Y = 0
CAMERA_Z = 500
CAMERA_ROT_X = 0
CAMERA_ROT_Y = 0

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
        f"{name}_Blue": obj_data[0]["Blue"]
    }

def create_cube(scale=1):
    scale = scale * 50
    return [(-scale, scale, scale), (scale, scale, scale), (scale, -scale, scale), (-scale, -scale, scale),
            (-scale, scale, -scale), (scale, scale, -scale), (scale, -scale, -scale), (-scale, -scale, -scale)]

def draw_cube(cube_points):
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    glBegin(GL_LINES)
    for start_index, end_index in edges:
        glVertex3fv(cube_points[start_index])
        glVertex3fv(cube_points[end_index])
    glEnd()

def rotate_3dpoint(point, angle, axis):
    cos_angle, sin_angle = cos(angle), sin(angle)
    x, y, z = point
    return [
        (cos_angle + (1 - cos_angle) * axis[0]**2) * x + ((1 - cos_angle) * axis[0] * axis[1] - axis[2] * sin_angle) * y + ((1 - cos_angle) * axis[0] * axis[2] + axis[1] * sin_angle) * z,
        ((1 - cos_angle) * axis[0] * axis[1] + axis[2] * sin_angle) * x + (cos_angle + (1 - cos_angle) * axis[1]**2) * y + ((1 - cos_angle) * axis[1] * axis[2] - axis[0] * sin_angle) * z,
        ((1 - cos_angle) * axis[0] * axis[2] - axis[1] * sin_angle) * x + ((1 - cos_angle) * axis[1] * axis[2] + axis[0] * sin_angle) * y + (cos_angle + (1 - cos_angle) * axis[2]**2) * z
    ]

def rotate_object(cube_points, angle, axis):
    for i in range(len(cube_points)):
        cube_points[i] = rotate_3dpoint(cube_points[i], angle, axis)

def translate_object(cube_points, dx, dy, dz):
    for i in range(len(cube_points)):
        cube_points[i] = (cube_points[i][0] + dx, cube_points[i][1] + dy, cube_points[i][2] + dz)

def get_rotation_matrix_x(angle):
    return np.array([
        [1, 0, 0],
        [0, cos(angle), -sin(angle)],
        [0, sin(angle), cos(angle)]
    ])

def get_rotation_matrix_y(angle):
    return np.array([
        [cos(angle), 0, sin(angle)],
        [0, 1, 0],
        [-sin(angle), 0, cos(angle)]
    ])

def get_camera_direction():
    forward_vector = np.array([cos(radians(CAMERA_ROT_X + 90)), 0, sin(radians(CAMERA_ROT_X + 90))])
    right_vector = np.array([cos(radians(CAMERA_ROT_X)), 0, sin(radians(CAMERA_ROT_X))])
    up_vector = np.array([0, 1, 0])
    return forward_vector, right_vector, up_vector

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
            glTranslatef(-CAMERA_X, -CAMERA_Y, -CAMERA_Z)
            glRotatef(CAMERA_ROT_X, 1, 0, 0)
            glRotatef(CAMERA_ROT_Y, 0, 1, 0)
            glScalef(1, -1, -1)  # Flip the Y-axis

            for name in loaded_objects_list:
                cube_data = load_cube(name)
                cube_points = cube_points_dict[name]
                translated_cube_points = [(p[0] + cube_data[f"{name}_X"], p[1] - cube_data[f"{name}_Y"], p[2] - cube_data[f"{name}_Z"]) for p in cube_points]
                glColor3f(cube_data[f"{name}_Red"] / 255, cube_data[f"{name}_Green"] / 255, cube_data[f"{name}_Blue"] / 255)
                draw_cube(translated_cube_points)
            glPopMatrix()

        keys = pygame.key.get_pressed()
        forward_vector, right_vector, up_vector = get_camera_direction()
        if keys[K_w] and enable_movement:
            CAMERA_X -= move_speed * forward_vector[0]
            CAMERA_Z -= move_speed * forward_vector[2]
        if keys[K_s] and enable_movement:
            CAMERA_X += move_speed * forward_vector[0]
            CAMERA_Z += move_speed * forward_vector[2]
        if keys[K_a] and enable_movement:
            CAMERA_X -= move_speed * right_vector[0]
            CAMERA_Z -= move_speed * right_vector[2]
        if keys[K_d] and enable_movement:
            CAMERA_X += move_speed * right_vector[0]
            CAMERA_Z += move_speed * right_vector[2]
        if keys[K_SPACE] and enable_movement:
            CAMERA_Y += move_speed * up_vector[1]
        if keys[K_LSHIFT] and enable_movement:
            CAMERA_Y -= move_speed * up_vector[1]

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.mouse.set_visible(not pygame.mouse.get_visible())
                    pygame.mouse.set_pos([WindowWidth / 2, WindowHeight / 2])
                    pygame.event.set_grab(not pygame.event.get_grab())
                    paused = not paused
                if event.key == K_r:
                    CAMERA_X, CAMERA_Y, CAMERA_Z = 0, 0, 500
                    CAMERA_ROT_X, CAMERA_ROT_Y = 0, 0
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
        if paused != True:
            CAMERA_ROT_Y += mouse_x * sensitivity
            CAMERA_ROT_X += mouse_y * sensitivity
            CAMERA_ROT_X = max(-90, min(90, CAMERA_ROT_X))

        pygame.display.flip()
        pygame.time.delay(25)

if __name__ == "__main__":
    main()