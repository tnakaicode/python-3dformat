import numpy as np
from plyfile import PlyData
from plyfile import PlyElement, PlyListProperty

plydata = PlyData.read('tet.ply')

# with open('tet.ply', 'rb') as f:
#    plydata = PlyData.read(f)

plydata.elements[0].name
plydata.elements[0].data[0]
plydata.elements[0].data[0]

vertex = np.array([(0, 0, 0),
                   (0, 1, 1),
                   (1, 0, 1),
                   (1, 1, 0),
                   (1, 2, 0)],
                  dtype=[('x', 'f4'), ('y', 'f4'),
                         ('z', 'f4')])
face = np.array([([0, 1, 2], 255, 255, 255, 0.0),
                 ([0, 2, 3], 255, 0, 0, 1.0),
                 ([0, 1, 3], 0, 255, 0, 2.0),
                 ([1, 2, 3], 0, 0, 255, 3.0),
                 ([1, 2, 4], 0, 0, 255, 4.0)],
                dtype=[('vertex_indices', 'i4', (3,)),
                       ('color1', 'u1'), ('color2', 'u1'),
                       ('color3', 'u1'), ('color4', 'f4')])

elv = PlyElement.describe(vertex, "vertex")
elf = PlyElement.describe(face, "face")

PlyData([elv, elf], text=True).write('some_ascii.ply')

# Force the byte order of the output to big-endian,
# independently of the machine's native byte order
PlyData([elv, elf], byte_order='>').write('some_binary.ply')

# Use a file object.  Binary mode is used here, which will cause
# Unix-style line endings to be written on all systems.
# with open('some_ascii.ply', mode='wb') as f:
#     PlyData([el], text=True).write(f)
