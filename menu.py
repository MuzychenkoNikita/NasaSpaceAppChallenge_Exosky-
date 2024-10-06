import imgui
from pyrr import Vector3, vector, vector3, matrix44
from Exoplanet_Import import ExoplanetData

# Global variable to store the chosen exoplanet
chosen_planet = None
chosen_planet_coords = None

# Instantiate ExoplanetData to fetch all names
exoplanet_data = ExoplanetData()
all_names = [str(name) for name in exoplanet_data.get_all_names()]

def menu(camera):
    global chosen_planet, chosen_planet_coords    
    imgui.set_next_window_size(250, 250)
    imgui.begin(
        "Menu",
        flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE
    )
    
    imgui.text("Exoplanets")
    # Create a list of buttons for each exoplanet
    for name in all_names:
        if imgui.button(name):
            chosen_planet = name
            chosen_planet_coords = exoplanet_data.get_coordinates_by_name(name)
            if chosen_planet_coords and chosen_planet != camera.last_teleported_planet:
                print(f"Teleporting camera to: {chosen_planet_coords}")  # Debug: print chosen coordinates
                camera.camera_pos = Vector3([float(chosen_planet_coords['x']), float(chosen_planet_coords['y']), float(chosen_planet_coords['z'])])
                camera.last_teleported_planet = chosen_planet
                break

    imgui.end()

def photo_button():
    imgui.set_next_window_size(100, 100)
    imgui.set_next_window_position(1000, 0)
    imgui.begin(
        "Photo",
        flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE
    )
    if imgui.button("click me!", width=100, height=100) == True:
        imgui.end()
        return 'Screenshot'
    if imgui.button("click me to start making a constellation!", width=100, height=100) == True:
        imgui.end()
        return 'Constellation'

    imgui.end()

    