import imgui
import main

# Example function to add an ImGui button
def render_imgui_button():
    imgui.set_next_window_position(10, 10)  # Set button window position (top-left corner)
    imgui.set_next_window_size(150, 60)     # Set button window size
    imgui.begin("Control", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR)

    if imgui.button("Show/Hide Menu"):
        global show_menu
        show_menu = not show_menu
        # Update cursor state
        if show_menu:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        else:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    imgui.end()