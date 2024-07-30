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

	def apply_perspective(p):
		"""Apply perspective to a 3D point."""
		factor = 1 / (1 + (p[2] + CAMERA_Z) * perspective)
		x = (p[0] + CAMERA_X) * factor
		y = (p[1] + CAMERA_Y) * factor
		return (x, y)
	
	a = apply_perspective(a)
	b = apply_perspective(b)
	
	ax, ay = a[0] + ORIGINX, a[1] + ORIGINY
	bx, by = b[0] + ORIGINX, b[1] + ORIGINY
	
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

def apply_camera_rotation(points, rotation_matrix_x, rotation_matrix_y):
	rotated_points = []
	for point in points:
		point = np.array(point)
		# Rotate around Y-axis first
		temp_point = np.dot(rotation_matrix_y, point)
		# Then rotate around X-axis
		final_point = np.dot(rotation_matrix_x, temp_point)
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

# Add rotation speed constants
ROTATION_SPEED = 1

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
	
	# Create rotation matrices for the camera
	rotation_matrix_x = get_rotation_matrix_x(radians(CAMERA_ROT_X))
	rotation_matrix_y = get_rotation_matrix_y(radians(CAMERA_ROT_Y))
	
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
		for i in get_object_names():
			if not objects_loaded:
				cubedict = load_cube(i)
				cube = create_cube(cubedict[f"{i}Scale"])
				# Store cube with initial position
				cube_points_dict[i] = cube
				draw_cube(background, (cubedict[f"{i}Red"], cubedict[f"{i}Green"], cubedict[f"{i}Blue"]), cube)
				loaded_objects_list.append(i)
				if loaded_objects_list == get_object_names():
					objects_loaded = True

			if objects_loaded:
				cubedict = load_cube(i)
				cube = cube_points_dict[i]
				# Apply object translation based on the loaded position
				translated_cube = [(p[0] + cubedict[f"{i}X"], p[1] - cubedict[f"{i}Y"], p[2] - cubedict[f"{i}Z"]) for p in cube]

				# Apply camera rotation to the cube
				rotated_cube = apply_camera_rotation(translated_cube, rotation_matrix_x, rotation_matrix_y)

				draw_cube(background, (cubedict[f"{i}Red"], cubedict[f"{i}Green"], cubedict[f"{i}Blue"]), rotated_cube)

		# Handle events
		keys = pygame.key.get_pressed()
		if keys[K_w] and enable_movement:
			CAMERA_X -= move_speed * cos(radians(CAMERA_ROT_Y) + np.pi / 2)
			CAMERA_Z -= move_speed * sin(radians(CAMERA_ROT_Y) + np.pi / 2)
		if keys[K_s] and enable_movement:
			CAMERA_X += move_speed * cos(radians(CAMERA_ROT_Y) + np.pi / 2)
			CAMERA_Z += move_speed * sin(radians(CAMERA_ROT_Y) + np.pi / 2)
		if keys[K_a] and enable_movement:
			CAMERA_X += move_speed * cos(radians(CAMERA_ROT_Y))
			CAMERA_Z += move_speed * sin(radians(CAMERA_ROT_Y))
		if keys[K_d] and enable_movement:
			CAMERA_X -= move_speed * cos(radians(CAMERA_ROT_Y))
			CAMERA_Z -= move_speed * sin(radians(CAMERA_ROT_Y))

		if keys[K_SPACE] and enable_movement:
			CAMERA_Y += move_speed
		if keys[K_LSHIFT] and enable_movement:
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

		# Update rotation matrices
		rotation_matrix_x = get_rotation_matrix_x(radians(CAMERA_ROT_X))
		rotation_matrix_y = get_rotation_matrix_y(radians(CAMERA_ROT_Y))

		# Draw everything to the off-screen surface
		screen.blit(background, (0, 0))
		pygame.display.flip()
		pygame.time.delay(25)

if __name__ == "__main__":
	main()