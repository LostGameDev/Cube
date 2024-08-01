from pygame.locals import *
import pygame.draw
import pygame.time
from math import sin, cos, radians
import json
import numpy as np

ORIGINX = 0
ORIGINY = 0

# Global camera position and rotation
CAMERA_X = 0
CAMERA_Y = 0
CAMERA_Z = 0
CAMERA_ROT_X = 0  # Rotation around X-axis
CAMERA_ROT_Y = 0  # Rotation around Y-axis

def get_object_names():
	objectnameDict = []
	with open('./objects.json') as f:
		data = json.load(f)
		for i in data:
			objectnameDict.append(i)
	return objectnameDict

def load_cube(name):
	objectDict = {}
	with open('./objects.json') as f:
		data = json.load(f)
		for i in data[name]:
			objectDict[f"{name}X"] = i["X"]
			objectDict[f"{name}Y"] = i["Y"]
			objectDict[f"{name}Z"] = i["Z"]
			objectDict[f"{name}Scale"] = i["Scale"]
			objectDict[f"{name}Red"] = i["Red"]
			objectDict[f"{name}Green"] = i["Green"]
			objectDict[f"{name}Blue"] = i["Blue"]
	return objectDict

def draw_3dline(surface, color, a, b):
    """Convert 3D coordinates to 2D and draw line with perspective."""
    perspective = 0.003  # Adjust this value to change perspective depth
    near_plane = -322  # Distance of the near clipping plane

    def apply_perspective(p):
        """Apply perspective to a 3D point."""
        z = p[2] + CAMERA_Z
        if z < near_plane:
            z = near_plane  # Clip to the near plane to prevent division by zero or negative values
        factor = 1 / (1 + z * perspective)
        x = (p[0] + CAMERA_X) * factor
        y = (p[1] + CAMERA_Y) * factor
        return (x, y)

    def clip_to_near_plane(p1, p2):
        """Clip line segment to the near plane."""
        p1_z = p1[2] + CAMERA_Z
        p2_z = p2[2] + CAMERA_Z
        if p1_z < near_plane and p2_z < near_plane:
            return None, None
        if p1_z >= near_plane and p2_z >= near_plane:
            return p1, p2
        t = (near_plane - p1_z) / (p2_z - p1_z)
        if p1_z < near_plane:
            p1 = (
                p1[0] + t * (p2[0] - p1[0]),
                p1[1] + t * (p2[1] - p1[1]),
                near_plane - CAMERA_Z
            )
        else:
            p2 = (
                p1[0] + t * (p2[0] - p1[0]),
                p1[1] + t * (p2[1] - p1[1]),
                near_plane - CAMERA_Z
            )
        return p1, p2

    a, b = clip_to_near_plane(a, b)
    if a is None or b is None:
        return  # Both points are behind the near plane

    a_perspective = apply_perspective(a)
    b_perspective = apply_perspective(b)

    ax, ay = a_perspective[0] + ORIGINX, a_perspective[1] + ORIGINY
    bx, by = b_perspective[0] + ORIGINX, b_perspective[1] + ORIGINY

    pygame.draw.line(surface, color, (ax, ay), (bx, by))


def create_cube(Scale=50):
	cube = [(-Scale,Scale,Scale),  (Scale,Scale,Scale),  (Scale,-Scale,Scale),  (-Scale,-Scale,Scale),
			(-Scale,Scale,-Scale), (Scale,Scale,-Scale), (Scale,-Scale,-Scale), (-Scale,-Scale,-Scale)]
	return cube

def draw_cube(surface, color, cube):
	"""Draw 3D cube."""
	a, b, c, d, e, f, g, h = cube
	draw_3dline(surface, color, a, b)
	draw_3dline(surface, color, b, c)
	draw_3dline(surface, color, c, d)
	draw_3dline(surface, color, d, a)

	draw_3dline(surface, color, e, f)
	draw_3dline(surface, color, f, g)
	draw_3dline(surface, color, g, h)
	draw_3dline(surface, color, h, e)

	draw_3dline(surface, color, a, e)
	draw_3dline(surface, color, b, f)
	draw_3dline(surface, color, c, g)
	draw_3dline(surface, color, d, h)

def rotate_3dpoint(p, angle, axis):
	"""Rotate a 3D point around a given axis."""
	ret = [0, 0, 0]
	cosang = cos(angle)
	sinang = sin(angle)
	ret[0] = (cosang + (1 - cosang) * axis[0] * axis[0]) * p[0]
	ret[0] += ((1 - cosang) * axis[0] * axis[1] - axis[2] * sinang) * p[1]
	ret[0] += ((1 - cosang) * axis[0] * axis[2] + axis[1] * sinang) * p[2]
	ret[1] = ((1 - cosang) * axis[0] * axis[1] + axis[2] * sinang) * p[0]
	ret[1] += (cosang + (1 - cosang) * axis[1] * axis[1]) * p[1]
	ret[1] += ((1 - cosang) * axis[1] * axis[2] - axis[0] * sinang) * p[2]
	ret[2] = ((1 - cosang) * axis[0] * axis[2] - axis[1] * sinang) * p[0]
	ret[2] += ((1 - cosang) * axis[1] * axis[2] + axis[0] * sinang) * p[1]
	ret[2] += (cosang + (1 - cosang) * axis[2] * axis[2]) * p[2]
	return ret

def rotate_object(obj, angle, axis):
	"""Rotate an object around a given axis."""
	for i in range(len(obj)):
		obj[i] = rotate_3dpoint(obj[i], angle, axis)

def translate_object(obj, dx, dy, dz):
	"""Move an object by a specific amount along X, Y, and Z axes."""
	for i in range(len(obj)):
		point = list(obj[i])
		point[0] += dx
		point[1] += dy
		point[2] += dz
		obj[i] = tuple(point)

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

def apply_camera_rotation(points):
	"""Apply camera rotation to all points."""
	angle_x = radians(CAMERA_ROT_X)
	angle_y = radians(CAMERA_ROT_Y)

	# Rotation matrices for X and Y axis
	rotation_x = get_rotation_matrix_x(angle_x)
	rotation_y = get_rotation_matrix_y(angle_y)

	rotated_points = []
	for point in points:
		point = np.array(point)
		# Rotate around Y-axis first
		temp_point = np.dot(rotation_y, point)
		# Then rotate around X-axis
		final_point = np.dot(rotation_x, temp_point)
		rotated_points.append(tuple(final_point))
	return rotated_points

def rotate_camera(cube_points_dict):
	"""Apply camera rotation to all objects."""
	angle_x = radians(CAMERA_ROT_X)
	angle_y = radians(CAMERA_ROT_Y)

	# Rotation matrices for X and Y axis
	rotation_x = get_rotation_matrix_x(angle_x)
	rotation_y = get_rotation_matrix_y(angle_y)

	for name in cube_points_dict:
		for i in range(len(cube_points_dict[name])):
			point = np.array(cube_points_dict[name][i])

			# Apply rotation around Y axis
			y_rotated = np.dot(rotation_y, point)

			# Apply rotation around X axis
			x_rotated = np.dot(rotation_x, y_rotated)

			cube_points_dict[name][i] = tuple(x_rotated)

def get_camera_direction():
	forward_vector = np.array([cos(radians(CAMERA_ROT_Y)), 0, sin(radians(CAMERA_ROT_Y))])
	CameraDirection = {"Forward": 0, "Back": 0, "Left": 0, "Right": 0, "Up": 0, "Down": 0, "PIDivBy2": 0, "NotPIDivBy2": 0}

	if abs(forward_vector[0]) > abs(forward_vector[2]):
		if forward_vector[0] > 0:
			# Forward
			CameraDirection["Forward"] = -1
			CameraDirection["Back"] = 1
			CameraDirection["Left"] = 1
			CameraDirection["Right"] = -1
			CameraDirection["Up"] = 0
			CameraDirection["Down"] = 0
			CameraDirection["PIDivBy2"] = np.pi / 2
			CameraDirection["NotPIDivBy2"] = 0
		else:
			# Back
			CameraDirection["Forward"] = 1
			CameraDirection["Back"] = -1
			CameraDirection["Left"] = -1
			CameraDirection["Right"] = 1
			CameraDirection["Up"] = 0
			CameraDirection["Down"] = 0
			CameraDirection["PIDivBy2"] = np.pi / 2
			CameraDirection["NotPIDivBy2"] = 0
	else:
		if forward_vector[2] > 0:
			# Left
			CameraDirection["Forward"] = -1
			CameraDirection["Back"] = 1
			CameraDirection["Left"] = -1
			CameraDirection["Right"] = 1
			CameraDirection["Up"] = 0
			CameraDirection["Down"] = 0
			CameraDirection["PIDivBy2"] = 0
			CameraDirection["NotPIDivBy2"] = np.pi / 2
		else:
			# Right
			CameraDirection["Forward"] = 1
			CameraDirection["Back"] = -1
			CameraDirection["Left"] = 1
			CameraDirection["Right"] = -1	
			CameraDirection["Up"] = 0
			CameraDirection["Down"] = 0
			CameraDirection["PIDivBy2"] = 0
			CameraDirection["NotPIDivBy2"] = np.pi / 2

	if abs(CAMERA_ROT_X) > 45:
		if CAMERA_ROT_X > 0:
			# Down
			CameraDirection["Forward"] = -1
			CameraDirection["Back"] = 1
			CameraDirection["Left"] = -1
			CameraDirection["Right"] = 1
			CameraDirection["Up"] = -1
			CameraDirection["Down"] = -1
			CameraDirection["PIDivBy2"] = 0
			CameraDirection["NotPIDivBy2"] = np.pi / 2
		else:
			# Up
			CameraDirection["Forward"] = 1
			CameraDirection["Back"] = -1
			CameraDirection["Left"] = 1
			CameraDirection["Right"] = -1
			CameraDirection["Up"] = 1
			CameraDirection["Down"] = 1
			CameraDirection["PIDivBy2"] = 0
			CameraDirection["NotPIDivBy2"] = np.pi / 2
	return CameraDirection

def main():
	global ORIGINX, ORIGINY, CAMERA_X, CAMERA_Y, CAMERA_Z, CAMERA_ROT_X, CAMERA_ROT_Y

	pygame.init()
	screen = pygame.display.set_mode((1024, 640), pygame.RESIZABLE)
	ORIGINX = screen.get_width() / 2
	ORIGINY = screen.get_height() / 2

	enable_movement = False

	objects_loaded = False
	loaded_objects_list = []
	cube_points_dict = {}

	background = pygame.Surface(screen.get_size())
	background = background.convert()
	
	# Hide the mouse cursor and set the relative mode
	capture_mouse = True
	pygame.mouse.set_visible(not capture_mouse)
	pygame.event.set_grab(capture_mouse)

	# Sensitivity for camera rotation
	sensitivity = 0.1
	move_speed = 5  # Speed of camera movement

	while True:
		background.fill(Color("black"))  # Clear background at the top of the loop

		# Load and draw objects
		if not objects_loaded:
			for i in get_object_names():
				cubedict = load_cube(i)
				cube = create_cube(cubedict[f"{i}Scale"])
				cube_points_dict[i] = cube
				draw_cube(background, (cubedict[f"{i}Red"], cubedict[f"{i}Green"], cubedict[f"{i}Blue"]), cube)
				loaded_objects_list.append(i)
				if len(loaded_objects_list) == len(get_object_names()):
					objects_loaded = True

		if objects_loaded:
			for i in loaded_objects_list:
				cubedict = load_cube(i)
				cube = cube_points_dict[i]
				translated_cube = [(p[0] + cubedict[f"{i}X"], p[1] - cubedict[f"{i}Y"], p[2] - cubedict[f"{i}Z"]) for p in cube]
				rotated_cube = apply_camera_rotation(translated_cube)
				draw_cube(background, (cubedict[f"{i}Red"], cubedict[f"{i}Green"], cubedict[f"{i}Blue"]), rotated_cube)

		
		# Get camera direction
		CameraDirection = get_camera_direction()

		# Handle events
		keys = pygame.key.get_pressed()
		if keys[K_w] and enable_movement:
			CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Forward"])
			CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Forward"])
		if keys[K_s] and enable_movement:
			CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Back"])
			CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Back"])
		if keys[K_a] and enable_movement:
			CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["NotPIDivBy2"]) * CameraDirection["Left"])
			CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["NotPIDivBy2"]) * CameraDirection["Left"])
		if keys[K_d] and enable_movement:
			CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["NotPIDivBy2"]) * CameraDirection["Right"])
			CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["NotPIDivBy2"]) * CameraDirection["Right"])

		if keys[K_SPACE] and enable_movement:
			if CameraDirection["Up"] == 1:
				CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Forward"])
				CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Forward"])
			elif CameraDirection["Up"] == -1:
				CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Back"])
				CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Back"])
			else:
				CAMERA_Y += move_speed
		if keys[K_LSHIFT] and enable_movement:
			if CameraDirection["Down"] == 1:
				CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Back"])
				CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Back"])
			elif CameraDirection["Up"] == -1:
				CAMERA_X += (move_speed * cos(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Forward"])
				CAMERA_Z += (move_speed * sin(radians(CAMERA_ROT_Y) + radians(CAMERA_ROT_X) + CameraDirection["PIDivBy2"]) * CameraDirection["Forward"])
			else:
				CAMERA_Y -= move_speed
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				# Hide the mouse cursor and set the relative mode
				capture_mouse = not capture_mouse
				pygame.mouse.set_visible(not capture_mouse)
				pygame.event.set_grab(capture_mouse)
			if event.type == pygame.VIDEORESIZE:
				ORIGINX = screen.get_width() / 2
				ORIGINY = screen.get_height() / 2
				screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
				background = pygame.Surface(screen.get_size())
				background = background.convert()
			if event.type == KEYDOWN and event.key == K_r:
				CAMERA_X = 0
				CAMERA_Y = 0
				CAMERA_Z = 0
				CAMERA_ROT_X = 0
				CAMERA_ROT_Y = 0
				background.fill(Color("black"))
				cube_points_dict.clear()
				loaded_objects_list.clear()
				objects_loaded = False
			if event.type == QUIT:
				pygame.quit()
				return

		if objects_loaded == True:
			for i in loaded_objects_list:
				#translate_object(cube_points_dict[i], 10, 10 ,10)
				#rotate_object(cube_points_dict[i], 0.1, (0,1,0))
				#rotate_object(cube_points_dict[i], 0.01, (0,0,1))
				#rotate_object(cube_points_dict[i], 0.01, (1,0,0))
				pass

		# Get mouse movement
		mouse_x, mouse_y = pygame.mouse.get_rel()

		# Update camera rotation based on mouse movement
		CAMERA_ROT_Y -= mouse_x * sensitivity
		CAMERA_ROT_X += mouse_y * sensitivity

		# Constrain vertical rotation to avoid flipping the camera
		CAMERA_ROT_X = max(-90, min(90, CAMERA_ROT_X))

		# Draw everything to the off-screen surface
		screen.blit(background, (0, 0))
		pygame.display.flip()
		pygame.time.delay(25)

if __name__ == "__main__":
	main()