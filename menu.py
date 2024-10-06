import imgui

def menu():
    
    imgui.set_next_window_size(250, 250)
    # imgui.set_next_window_position(0, 0)
    imgui.begin(
        "Menu",
        flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE
    )
    imgui.text("Exoplanets")
    imgui.button("click me!")

    imgui.end()