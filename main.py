import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
import numpy as np
import time
import imgui
from imgui.integrations.glfw import GlfwRenderer
import menu
from camera import Camera
from Stars_Import import Get_Stars
from PIL import Image
from Constellation_Draw import Constellation

# Initialize camera
cam = Camera()
WIDTH, HEIGHT = 1280, 720
lastX, lastY = WIDTH / 2, HEIGHT / 2
first_mouse = True
left, right, forward, backward = False, False, False, False

# Flag to track menu visibility
show_menu = False

# Variables to store mouse state
stored_lastX, stored_lastY = lastX, lastY

def ScreenShot(func):
    glReadBuffer(GL_FRONT)
    pixels = glReadPixels(0,0,WIDTH,HEIGHT,GL_RGB,GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (WIDTH, HEIGHT), pixels)
    image = image.transpose( Image.FLIP_TOP_BOTTOM)
    if func=='save':
        image.save('Exosky.jpg')
    if func=='constellation':
        Constellation(image)

# Function to handle keyboard inputs
def key_input_clb(window, key, scancode, action, mode):
    global left, right, forward, backward
    
    # Get ImGui IO context
    io = imgui.get_io()

    # Only process input if ImGui is not capturing the keyboard
    if not io.want_capture_keyboard:
        if key == glfw.KEY_W:
            forward = (action == glfw.PRESS)
        if key == glfw.KEY_S:
            backward = (action == glfw.PRESS)
        if key == glfw.KEY_A:
            left = (action == glfw.PRESS)
        if key == glfw.KEY_D:
            right = (action == glfw.PRESS)

# Process camera movement - poll directly from GLFW instead of relying on global flags
def do_movement():
    io = imgui.get_io()
    # Only allow movement if ImGui is not interacting with any input
    if not (io.want_capture_mouse or io.want_capture_keyboard):
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            cam.process_keyboard("FORWARD", 1.05)
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            cam.process_keyboard("BACKWARD", 1.05)
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            cam.process_keyboard("LEFT", 1.05)
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            cam.process_keyboard("RIGHT", 1.05)

# Mouse look callback (for rotation)
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
void main()
{
    vec3 final_pos = a_position + a_offset;
    gl_Position =  projection * view * model * vec4(final_pos, 1.0f);
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

# Make the context current
glfw.make_context_current(window)

# Set callbacks for resizing, mouse input, and keyboard input
glfw.set_window_size_callback(window, window_resize_clb)
glfw.set_cursor_pos_callback(window, mouse_look_clb)
glfw.set_key_callback(window, key_input_clb)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

# Initialize ImGui context
imgui.create_context()
imgui_renderer = GlfwRenderer(window)

# Generate sphere data (for stars)
sphere_vertices, sphere_indices = generate_sphere(0.1, 20, 20)

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

# Process star positions
number_of_stars = 4000

instance_array = []
scale_factor = 1  # Base scale for positioning

for star in Get_Stars(amount=number_of_stars):
    brightness = star['g_mag']
    size = star['rad']
    translation = pyrr.Vector3([star['x'] * scale_factor, star['y'] * scale_factor, star['z'] * scale_factor])
    instance_array.append((translation, size))  # Store translation and size as a tuple

print(f"Total number of stars fetched: {len(instance_array)}")

# Convert to a NumPy array for use in OpenGL
instance_array = np.array(instance_array, dtype=[('position', np.float32, 3), ('size', np.float32)])
instance_positions = instance_array['position'].flatten()  # Flatten positions for OpenGL
instance_sizes = instance_array['size']  # Sizes can be used later in shaders if needed

# Instance VBO
instanceVBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
glBufferData(GL_ARRAY_BUFFER, instance_positions.nbytes, instance_positions, GL_STATIC_DRAW)

# Enable instance attribute for offsets
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
glVertexAttribDivisor(1, 1)  # This line indicates that this attribute is instanced

# Optionally, if you need to pass sizes to the shader
sizeVBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, sizeVBO)
glBufferData(GL_ARRAY_BUFFER, instance_sizes.nbytes, instance_sizes, GL_STATIC_DRAW)

# Enable vertex attribute for sizes
glEnableVertexAttribArray(2)  # Assuming the size is at location 2 in the shader
glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
glVertexAttribDivisor(2, 1)  # This line indicates that this attribute is instanced

# OpenGL settings
glUseProgram(shader)
glClearColor(0, 0.0, 0.02, 1)
glEnable(GL_DEPTH_TEST)

# Projection and model matrices
projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH / HEIGHT, 0.01, 1000000)
model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -200.0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

# Main rendering loop
last_time = time.time()
frame_count = 0
take_screenshot = False
toggle_menu = False
take_screenshot = 0
ss_func=''

while not glfw.window_should_close(window):
    if take_screenshot == 2:
        ScreenShot(ss_func)
        take_screenshot = 0

    # Poll events from GLFW (keyboard, mouse)
    glfw.poll_events()

    # Directly check if Escape key is pressed to toggle the menu
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS or take_screenshot == 1:
        show_menu = not show_menu
        if take_screenshot == 1:
            take_screenshot = 2
        if glfw.get_key(window, glfw.KEY_ESCAPE):
            time.sleep(0.2)  # Add a slight delay to prevent rapid toggling

        # Update cursor state and store/restore mouse position
        if show_menu:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            print("Menu shown, cursor released")
            # Store the last mouse positions when entering the menu
            stored_lastX, stored_lastY = lastX, lastY
        else:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            print("Menu hidden, cursor locked")
            # Restore the stored mouse positions when exiting the menu
            lastX, lastY = stored_lastX, stored_lastY
            first_mouse = True  # Reset to ensure proper cursor repositioning

    # Process ImGui inputs
    imgui_renderer.process_inputs()  # Only call once per loop, after polling events

    # Handle camera movement only if menu is not shown
    if not show_menu:
        do_movement()

    # Handle mouse look only if menu is not shown
    if not show_menu:
        mouse_x, mouse_y = glfw.get_cursor_pos(window)
        mouse_look_clb(window, mouse_x, mouse_y)

    # Render ImGui interface if menu is shown
    imgui.new_frame()
    photo_trigger = ''
    if show_menu:
        menu.menu(cam)  # Your custom menu rendering
        photo_trigger = menu.photo_button()
        if photo_trigger == 'Constellation':
            take_screenshot = 1
            ss_func = 'constellation'
        if photo_trigger == 'Screenshot':
            take_screenshot = 1
            ss_func = 'save'

    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Update camera view matrix
    view = cam.get_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    # Draw instanced stars
    glDrawElementsInstanced(GL_TRIANGLES, len(sphere_indices), GL_UNSIGNED_INT, None, len(instance_array) // 3)

    # Render ImGui frame data
    imgui.render()
    imgui_renderer.render(imgui.get_draw_data())

    # Swap the buffers to display the current frame
    glfw.swap_buffers(window)

    # FPS calculation and window title update
    current_time = time.time()
    frame_count += 1
    if current_time - last_time >= 1.0:
        fps = frame_count / (current_time - last_time)
        glfw.set_window_title(window, f"Star Simulation - FPS: {fps:.2f}")
        frame_count = 0
        last_time = current_time

# Shutdown ImGui and terminate GLFW
imgui_renderer.shutdown()
glfw.terminate()