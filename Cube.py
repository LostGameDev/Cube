import pygame
import pygame.draw
import pygame.time
import numpy as np
import json
from math import sin, cos, radians
from pygame.locals import *

# Constants
ORIGIN_X = 0
ORIGIN_Y = 0
CAMERA_X = 0
CAMERA_Y = 0
CAMERA_Z = 0
CAMERA_ROT_X = 0
CAMERA_ROT_Y = 0
PERSPECTIVE = 0.003
NEAR_PLANE = -322

def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)

def get_object_names():
    return list(load_json('./objects.json').keys())

def load_cube(name):
    data = load_json('./objects.json')
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

def apply_perspective(point):
    z = max(point[2], NEAR_PLANE)
    factor = 1 / (1 + z * PERSPECTIVE)
    return point[0] * factor, point[1] * factor

def clip_to_near_plane(point1, point2):
    z1, z2 = point1[2], point2[2]
    if z1 < NEAR_PLANE and z2 < NEAR_PLANE:
        return None, None
    if z1 >= NEAR_PLANE and z2 >= NEAR_PLANE:
        return point1, point2
    t = (NEAR_PLANE - z1) / (z2 - z1)
    if z1 < NEAR_PLANE:
        point1 = (point1[0] + t * (point2[0] - point1[0]),
                  point1[1] + t * (point2[1] - point1[1]),
                  NEAR_PLANE)
    else:
        point2 = (point1[0] + t * (point2[0] - point1[0]),
                  point1[1] + t * (point2[1] - point1[1]),
                  NEAR_PLANE)
    return point1, point2

def transform_point(point):
    translated_point = np.array(point) - np.array([CAMERA_X, CAMERA_Y, CAMERA_Z])
    rotated_point = np.dot(get_rotation_matrix_y(radians(CAMERA_ROT_Y)), translated_point)
    rotated_point = np.dot(get_rotation_matrix_x(radians(CAMERA_ROT_X)), rotated_point)
    return rotated_point

def draw_3dline(surface, color, start_point, end_point):
    start_point, end_point = transform_point(start_point), transform_point(end_point)
    start_point, end_point = clip_to_near_plane(start_point, end_point)
    if start_point is None or end_point is None:
        return
    start_perspective = apply_perspective(start_point)
    end_perspective = apply_perspective(end_point)
    pygame.draw.line(surface, color,
                     (start_perspective[0] + ORIGIN_X, start_perspective[1] + ORIGIN_Y),
                     (end_perspective[0] + ORIGIN_X, end_perspective[1] + ORIGIN_Y))

def create_cube(scale=50):
    return [(-scale, scale, scale), (scale, scale, scale), (scale, -scale, scale), (-scale, -scale, scale),
            (-scale, scale, -scale), (scale, scale, -scale), (scale, -scale, -scale), (-scale, -scale, -scale)]

def draw_cube(surface, color, cube_points):
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    for start_index, end_index in edges:
        draw_3dline(surface, color, cube_points[start_index], cube_points[end_index])

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
    forward_vector = np.array([cos(radians(CAMERA_ROT_Y + 90)), 0, sin(radians(CAMERA_ROT_Y + 90))])
    right_vector = np.array([cos(radians(CAMERA_ROT_Y)), 0, sin(radians(CAMERA_ROT_Y))])
    up_vector = np.array([0, -1, 0])
    return forward_vector, right_vector, up_vector

def main():
    global ORIGIN_X, ORIGIN_Y, CAMERA_X, CAMERA_Y, CAMERA_Z, CAMERA_ROT_X, CAMERA_ROT_Y
    pygame.init()
    screen = pygame.display.set_mode((1024, 640), pygame.RESIZABLE)
    ORIGIN_X, ORIGIN_Y = screen.get_width() / 2, screen.get_height() / 2

    enable_movement = False
    objects_loaded = False
    loaded_objects_list = []
    cube_points_dict = {}

    background = pygame.Surface(screen.get_size()).convert()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    sensitivity = 0.1
    move_speed = 5

    while True:
        background.fill(Color("black"))

        if not objects_loaded:
            object_names = get_object_names()
            for name in object_names:
                cube_data = load_cube(name)
                cube_points = create_cube(cube_data[f"{name}_Scale"])
                cube_points_dict[name] = cube_points
                draw_cube(background, (cube_data[f"{name}_Red"], cube_data[f"{name}_Green"], cube_data[f"{name}_Blue"]), cube_points)
                loaded_objects_list.append(name)
            if len(loaded_objects_list) == len(object_names):
                objects_loaded = True

        if objects_loaded:
            for name in loaded_objects_list:
                cube_data = load_cube(name)
                cube_points = cube_points_dict[name]
                translated_cube_points = [(p[0] + cube_data[f"{name}_X"], p[1] - cube_data[f"{name}_Y"], p[2] - cube_data[f"{name}_Z"]) for p in cube_points]
                draw_cube(background, (cube_data[f"{name}_Red"], cube_data[f"{name}_Green"], cube_data[f"{name}_Blue"]), translated_cube_points)

        keys = pygame.key.get_pressed()
        forward_vector, right_vector, up_vector = get_camera_direction()
        if keys[K_w] and enable_movement:
            CAMERA_X += move_speed * forward_vector[0]
            CAMERA_Z += move_speed * forward_vector[2]
        if keys[K_s] and enable_movement:
            CAMERA_X -= move_speed * forward_vector[0]
            CAMERA_Z -= move_speed * forward_vector[2]
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
                    pygame.event.set_grab(not pygame.event.get_grab())
                if event.key == K_r:
                    CAMERA_X, CAMERA_Y, CAMERA_Z = 0, 0, 0
                    CAMERA_ROT_X, CAMERA_ROT_Y = 0, 0
                    background.fill(Color("black"))
                    cube_points_dict.clear()
                    loaded_objects_list.clear()
                    objects_loaded = False
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == VIDEORESIZE:
                ORIGIN_X, ORIGIN_Y = event.w / 2, event.h / 2
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                background = pygame.Surface(screen.get_size()).convert()

        mouse_x, mouse_y = pygame.mouse.get_rel()
        CAMERA_ROT_Y -= mouse_x * sensitivity
        CAMERA_ROT_X += mouse_y * sensitivity
        CAMERA_ROT_X = max(-90, min(90, CAMERA_ROT_X))

        screen.blit(background, (0, 0))
        pygame.display.flip()
        pygame.time.delay(25)

if __name__ == "__main__":
    main()
