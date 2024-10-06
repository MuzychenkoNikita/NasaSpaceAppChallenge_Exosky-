import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
import numpy as np
import time
from camera import Camera
from Star_Import import Get_Stars  # Import star data from the Hipparcos catalog (filtered and processed)

# Initialize camera
cam = Camera()
WIDTH, HEIGHT = 1280, 720
lastX, lastY = WIDTH / 2, HEIGHT / 2
first_mouse = True
left, right, forward, backward = False, False, False, False

# Function to handle keyboard inputs
def key_input_clb(window, key, scancode, action, mode):
    global left, right, forward, backward
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    if key == glfw.KEY_W and action == glfw.PRESS:
        forward = True
    elif key == glfw.KEY_W and action == glfw.RELEASE:
        forward = False
    if key == glfw.KEY_S and action == glfw.PRESS:
        backward = True
    elif key == glfw.KEY_S and action == glfw.RELEASE:
        backward = False
    if key == glfw.KEY_A and action == glfw.PRESS:
        left = True
    elif key == glfw.KEY_A and action == glfw.RELEASE:
        left = False
    if key == glfw.KEY_D and action == glfw.PRESS:
        right = True
    elif key == glfw.KEY_D and action == glfw.RELEASE:
        right = False

# Process camera movement
def do_movement():
    if forward:
        cam.process_keyboard("FORWARD", 0.05)
    if backward:
        cam.process_keyboard("BACKWARD", 0.05)
    if left:
        cam.process_keyboard("LEFT", 0.05)
    if right:
        cam.process_keyboard("RIGHT", 0.05)

# Function for mouse look/camera rotation
def mouse_look_clb(window, xpos, ypos):
    global first_mouse, lastX, lastY
    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False
    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos
    cam.process_mouse_movement(xoffset, yoffset)

# Function to generate sphere vertices for stars
def generate_sphere(radius, sectorCount, stackCount):
    vertices = []
    indices = []
    for i in range(stackCount + 1):
        stack_angle = np.pi / 2 - i * np.pi / stackCount
        xy = radius * np.cos(stack_angle)
        z = radius * np.sin(stack_angle)
        for j in range(sectorCount + 1):
            sector_angle = j * 2 * np.pi / sectorCount
            x = xy * np.cos(sector_angle)
            y = xy * np.sin(sector_angle)
            vertices.extend([x, y, z])
    for i in range(stackCount):
        for j in range(sectorCount):
            first = i * (sectorCount + 1) + j
            second = first + sectorCount + 1
            indices.append(first)
            indices.append(second)
            indices.append(first + 1)
            indices.append(second)
            indices.append(second + 1)
            indices.append(first + 1)
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

# Vertex and fragment shader sources
vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_offset;
uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 move;
void main()
{
    vec3 final_pos = a_position + a_offset;
    gl_Position =  projection * view * move * model * vec4(final_pos, 1.0f);
}
"""

fragment_src = """
# version 330
out vec4 out_color;
void main()
{
    out_color = vec4(1.0, 1.0, 1.0, 1.0);  // White color for stars
}
"""

# Window resize callback
def window_resize_clb(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

# Initialize GLFW
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# Create window
window = glfw.create_window(WIDTH, HEIGHT, "Star Simulation", None, None)
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# Set window position
glfw.set_window_pos(window, 400, 200)

# Set callbacks for resizing, mouse input, and keyboard input
glfw.set_window_size_callback(window, window_resize_clb)
glfw.set_cursor_pos_callback(window, mouse_look_clb)
glfw.set_key_callback(window, key_input_clb)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

# Make the context current
glfw.make_context_current(window)

# Generate sphere data (for stars)
sphere_vertices, sphere_indices = generate_sphere(0.5, 20, 20)

# Compile shaders
shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# Setup VAO, VBO, and EBO
VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)
EBO = glGenBuffers(1)

glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, sphere_vertices.nbytes, sphere_vertices, GL_STATIC_DRAW)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, sphere_indices.nbytes, sphere_indices, GL_STATIC_DRAW)

# Vertex attribute pointers
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

# Fetch stars data (XYZ coordinates for visible stars)
stars_output = Get_Stars(amount=4000)  # Fetch 4000 visible stars

# Process star positions
instance_array = []
scale_factor = 0.01  # Scale stars' coordinates to fit within the scene
for star in stars_output:
    translation = pyrr.Vector3([star['x'] * scale_factor, star['y'] * scale_factor, star['z'] * scale_factor])
    instance_array.append(translation)
instance_array = np.array(instance_array, np.float32).flatten()

# Instance VBO
instanceVBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
glBufferData(GL_ARRAY_BUFFER, instance_array.nbytes, instance_array, GL_STATIC_DRAW)

# Enable instance attribute for offsets
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
glVertexAttribDivisor(1, 1)

# OpenGL settings
glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

# Projection and model matrices
projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH / HEIGHT, 0.01, 1000000)
model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -200.0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")
move_loc = glGetUniformLocation(shader, "move")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

# Main rendering loop
last_time = time.time()
frame_count = 0
while not glfw.window_should_close(window):
    glfw.poll_events()
    do_movement()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Update camera view matrix
    view = cam.get_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    # Draw stars as instanced spheres
    glDrawElementsInstanced(GL_TRIANGLES, len(sphere_indices), GL_UNSIGNED_INT, None, len(instance_array) // 3)

    glfw.swap_buffers(window)

    # FPS calculation
    current_time = time.time()
    frame_count += 1
    if current_time - last_time >= 1.0:
        fps = frame_count / (current_time - last_time)
        glfw.set_window_title(window, f"Star Simulation - FPS: {fps:.2f}")
        frame_count = 0
        last_time = current_time

glfw.terminate()
