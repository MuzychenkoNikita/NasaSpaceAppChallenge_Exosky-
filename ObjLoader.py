import numpy as np


class ObjLoader:
    buffer = []

    @staticmethod
    def search_data(data_values, coordinates, skip, data_type):
        for d in data_values:
            if d == skip:
                continue
            if data_type == 'float':
                coordinates.append(float(d))
            elif data_type == 'int':
                coordinates.append(int(d)-1)


    @staticmethod # sorted vertex buffer for use with glDrawArrays function
    def create_sorted_vertex_buffer(indices_data, vertices, textures, normals):
        for i, ind in enumerate(indices_data):
            if i % 3 == 0: # sort the vertex coordinates
                start = ind * 3
                end = start + 3
                ObjLoader.buffer.extend(vertices[start:end])
            elif i % 3 == 1: # sort the texture coordinates
                start = ind * 2
                end = start + 2
                ObjLoader.buffer.extend(textures[start:end])
            elif i % 3 == 2: # sort the normal vectors
                start = ind * 3
                end = start + 3
                ObjLoader.buffer.extend(normals[start:end])


    @staticmethod # TODO unsorted vertex buffer for use with glDrawElements function
    def create_unsorted_vertex_buffer(indices_data, vertices, textures, normals):
        num_verts = len(vertices) // 3

        for i1 in range(num_verts):
            start = i1 * 3
            end = start + 3
            ObjLoader.buffer.extend(vertices[start:end])

            for i2, data in enumerate(indices_data):
                if i2 % 3 == 0 and data == i1:
                    start = indices_data[i2 + 1] * 2
                    end = start + 2
                    ObjLoader.buffer.extend(textures[start:end])

                    start = indices_data[i2 + 2] * 3
                    end = start + 3
                    ObjLoader.buffer.extend(normals[start:end])

                    break


    @staticmethod
    def show_buffer_data(buffer):
        for i in range(len(buffer)//8):
            start = i * 8
            end = start + 8
            print(buffer[start:end])


    @staticmethod
    def load_model(file, sorted=True):
        vert_coords = []  # will contain all the vertex coordinates
        tex_coords = []  # will contain all the texture coordinates
        norm_coords = []  # will contain all the vertex normals

        all_indices = []  # will contain all the vertex, texture, and normal indices
        indices = []  # will contain the indices for indexed drawing

        with open(file, 'r') as f:
            line_number = 0  # Track the current line number for debugging
            line = f.readline()

            while line:
                line_number += 1
                values = line.strip().split()

                # Debugging output to check which lines are being processed
                print(f"Processing line {line_number}: {line.strip()}")
                print(f"Split values: {values}")

                # Skip empty lines and comments
                if len(values) == 0 or values[0].startswith('#'):
                    print(f"Skipping empty/comment line at {line_number}")
                    line = f.readline()
                    continue

                # Handle supported .obj keywords (v, vt, vn, f)
                if values[0] == 'v':
                    if len(values) >= 4:  # Ensure there are enough components for vertex data
                        ObjLoader.search_data(values, vert_coords, 'v', 'float')
                    else:
                        print(f"Malformed vertex line at {line_number}: {line.strip()}")
                elif values[0] == 'vt':
                    if len(values) >= 3:  # Ensure there are enough components for texture data
                        ObjLoader.search_data(values, tex_coords, 'vt', 'float')
                    else:
                        print(f"Malformed texture coordinate line at {line_number}: {line.strip()}")
                elif values[0] == 'vn':
                    if len(values) >= 4:  # Ensure there are enough components for normal data
                        ObjLoader.search_data(values, norm_coords, 'vn', 'float')
                    else:
                        print(f"Malformed normal vector line at {line_number}: {line.strip()}")
                elif values[0] == 'f':
                    for value in values[1:]:
                        val = value.split('/')
                        if len(val) >= 1 and len(val[0]) > 0:  # Ensure valid face data
                            ObjLoader.search_data(val, all_indices, 'f', 'int')
                            indices.append(int(val[0]) - 1)
                        else:
                            print(f"Malformed face element at {line_number}: {value}")
                else:
                    # Skip unsupported or irrelevant lines (like 'mtllib', 'o', etc.)
                    print(f"Skipping unsupported line {line_number}: {line.strip()}")

                # Read the next line
                line = f.readline()

        if sorted:
            # Use with glDrawArrays
            ObjLoader.create_sorted_vertex_buffer(all_indices, vert_coords, tex_coords, norm_coords)
        else:
            # Use with glDrawElements
            ObjLoader.create_unsorted_vertex_buffer(all_indices, vert_coords, tex_coords, norm_coords)

        buffer = ObjLoader.buffer.copy()  # Create a local copy of the buffer list
        ObjLoader.buffer = []  # After copy, reset the buffer

        return np.array(indices, dtype='uint32'), np.array(buffer, dtype='float32')

