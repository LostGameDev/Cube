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
CAMERA_Z = 0
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
		f"{name}_ScaleX": obj_data[0]["ScaleX"],
		f"{name}_ScaleY": obj_data[0]["ScaleY"],
		f"{name}_ScaleZ": obj_data[0]["ScaleZ"],
		f"{name}_RotationX": obj_data[0]["RotationX"],
		f"{name}_RotationY": obj_data[0]["RotationY"],
		f"{name}_RotationZ": obj_data[0]["RotationZ"],
		f"{name}_Red": obj_data[0]["Red"],
		f"{name}_Green": obj_data[0]["Green"],
		f"{name}_Blue": obj_data[0]["Blue"],
		f"{name}_Alpha": obj_data[0]["Alpha"]
	}

def create_cube(scale_x=1, scale_y=1, scale_z=1):
	scale_x *= 50
	scale_y *= 50
	scale_z *= 50
	vertices = [
		(-scale_x, scale_y, scale_z),  # 0
		(scale_x, scale_y, scale_z),   # 1
		(scale_x, -scale_y, scale_z),  # 2
		(-scale_x, -scale_y, scale_z), # 3
		(-scale_x, scale_y, -scale_z), # 4
		(scale_x, scale_y, -scale_z),  # 5
		(scale_x, -scale_y, -scale_z), # 6
		(-scale_x, -scale_y, -scale_z) # 7
	]
	normals = [
		(0, 0, 1),   # Front face
		(0, 0, -1),  # Back face
		(0, 1, 0),   # Top face
		(0, -1, 0),  # Bottom face
		(1, 0, 0),   # Right face
		(-1, 0, 0)   # Left face
	]
	 
	# Normalize normals
	normals = [np.array(n, dtype=np.float32) / np.linalg.norm(n) for n in normals]
	return vertices, normals

def draw_cube(cube_points, cube_normals, color, wireframe_mode, fullbright):
	edges = [
		(0, 1), (1, 2), (2, 3), (3, 0),
		(4, 5), (5, 6), (6, 7), (7, 4),
		(0, 4), (1, 5), (2, 6), (3, 7)
	]
	# Define quads in counter-clockwise order
	quads = [
		(3, 2, 1, 0), # Back face
		(4, 5, 6, 7), # Front face
		(0, 1, 5, 4), # Top face
		(2, 3, 7, 6), # Bottom face
		(1, 2, 6, 5), # Right face
		(4, 7, 3, 0)  # Left face
	]

	if wireframe_mode:
		glDisable(GL_LIGHTING)
		glEnable(GL_COLOR_MATERIAL)
		glBegin(GL_LINES)
		glColor4f(*color)  # Use RGBA color
		for start_index, end_index in edges:
			glVertex3fv(cube_points[start_index])
			glVertex3fv(cube_points[end_index])
		glEnd()
		glDisable(GL_COLOR_MATERIAL)
		glEnable(GL_LIGHTING)
	else:
		if fullbright:
			glDisable(GL_LIGHTING)
		glEnable(GL_COLOR_MATERIAL)
		glBegin(GL_QUADS)
		for i, quad in enumerate(quads):
			glNormal3fv(cube_normals[i])  # Set the normal for the face
			glColor4f(*color)  # Set color before drawing the vertices
			for vertex in quad:
				glVertex3fv(cube_points[vertex])
		glEnd()
		glDisable(GL_COLOR_MATERIAL)
		if fullbright:
			glEnable(GL_LIGHTING)

def setup_lighting():
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_COLOR_MATERIAL)
	
	# Set light properties
	light_position = (1, 1, 1, 0)  # Directional light
	light_diffuse = (0.8, 0.8, 0.8, 1)  # Dimmer diffuse light
	light_specular = (1, 1, 1, 1)  # White specular light

	glLightfv(GL_LIGHT0, GL_POSITION, light_position)
	glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
	glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

	# Set material properties
	glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.8, 0.8, 0.8, 1))  # Softer ambient and diffuse
	glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, 1))
	glMaterialf(GL_FRONT, GL_SHININESS, 30.0)  # Lower shininess

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

	# Enable back-face culling
	glEnable(GL_CULL_FACE)
	glCullFace(GL_BACK)

	camera = Camera([CAMERA_X, CAMERA_Y, CAMERA_Z], [CAMERA_ROT_X, CAMERA_ROT_Y])
	
	# Setup Lighting
	setup_lighting()

	objects_loaded = False
	loaded_objects_list = []
	cube_points_dict = {}

	pygame.mouse.set_visible(False)
	pygame.event.set_grab(True)

	sensitivity = 0.1
	move_speed = 5
	wireframe_mode = False
	fullbright = False
	paused = False

	while True:
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		if not objects_loaded:
			object_names = get_object_names()
			for name in object_names:
				cube_data = load_cube(name)
				cube_points, cube_normals = create_cube(cube_data[f"{name}_ScaleX"], cube_data[f"{name}_ScaleY"], cube_data[f"{name}_ScaleZ"])
				cube_points_dict[name] = (cube_points, cube_normals)
				loaded_objects_list.append(name)
			if len(loaded_objects_list) == len(object_names):
				objects_loaded = True

		if objects_loaded:
			glPushMatrix()
			camera.get_view_matrix()
			glScalef(1, -1, -1)  # Flip the Y-axis

			opaque_objects = []
			transparent_objects = []

			for name in loaded_objects_list:
				cube_data = load_cube(name)
				alpha = cube_data[f"{name}_Alpha"] / 255
				if alpha < 1.0:
					transparent_objects.append((name, alpha))
				else:
					opaque_objects.append(name)

			# Draw opaque objects first
			for name in opaque_objects:
				cube_data = load_cube(name)
				cube_points, cube_normals = cube_points_dict[name]
				translated_cube_points = [(p[0] + cube_data[f"{name}_X"], p[1] - cube_data[f"{name}_Y"], p[2] - cube_data[f"{name}_Z"]) for p in cube_points]
				color = (
					cube_data[f"{name}_Red"] / 255,
					cube_data[f"{name}_Green"] / 255,
					cube_data[f"{name}_Blue"] / 255,
					cube_data[f"{name}_Alpha"] / 255
				)
				# Apply cube rotation
				glPushMatrix()
				glTranslatef(cube_data[f"{name}_X"], -cube_data[f"{name}_Y"], -cube_data[f"{name}_Z"])
				glRotatef(cube_data[f"{name}_RotationX"], 1, 0, 0)
				glRotatef(cube_data[f"{name}_RotationY"], 0, 1, 0)
				glRotatef(cube_data[f"{name}_RotationZ"], 0, 0, 1)
				glTranslatef(-cube_data[f"{name}_X"], cube_data[f"{name}_Y"], cube_data[f"{name}_Z"])
				draw_cube(translated_cube_points, cube_normals, color, wireframe_mode, fullbright)
				glPopMatrix()

			# Draw transparent objects
			for name, alpha in sorted(transparent_objects, key=lambda x: -x[1]):  # Sort by alpha descending
				cube_data = load_cube(name)
				cube_points, cube_normals = cube_points_dict[name]
				translated_cube_points = [(p[0] + cube_data[f"{name}_X"], p[1] - cube_data[f"{name}_Y"], p[2] - cube_data[f"{name}_Z"]) for p in cube_points]
				color = (
					cube_data[f"{name}_Red"] / 255,
					cube_data[f"{name}_Green"] / 255,
					cube_data[f"{name}_Blue"] / 255,
					alpha
				)
				# Apply cube rotation
				glPushMatrix()
				glTranslatef(cube_data[f"{name}_X"], -cube_data[f"{name}_Y"], -cube_data[f"{name}_Z"])
				glRotatef(cube_data[f"{name}_RotationX"], 1, 0, 0)
				glRotatef(cube_data[f"{name}_RotationY"], 0, 1, 0)
				glRotatef(cube_data[f"{name}_RotationZ"], 0, 0, 1)
				glTranslatef(-cube_data[f"{name}_X"], cube_data[f"{name}_Y"], cube_data[f"{name}_Z"])
				draw_cube(translated_cube_points, cube_normals, color, wireframe_mode, fullbright)
				glPopMatrix()

			glPopMatrix()

		keys = pygame.key.get_pressed()
		if keys[K_w]:
			camera.position += move_speed * camera.forward
		if keys[K_s]:
			camera.position -= move_speed * camera.forward
		if keys[K_a]:
			camera.position -= move_speed * camera.right
		if keys[K_d]:
			camera.position += move_speed * camera.right
		if keys[K_SPACE]:
			camera.position += move_speed * camera.up
		if keys[K_LSHIFT]:
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
					wireframe_mode = False
					cube_points_dict.clear()
					loaded_objects_list.clear()
					objects_loaded = False
				if event.key == K_t:
					wireframe_mode = not wireframe_mode  # Toggle wireframe mode
				if event.key == K_b:
					fullbright = not fullbright
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
		pygame.time.wait(10)

if __name__ == "__main__":
	main()