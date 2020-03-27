import numpy as np
import sys
from plyfile import PlyData
from plyfile import PlyElement, PlyListProperty

px = np.linspace(-1, 1, 100) * 100
py = np.linspace(-1, 1, 200) * 100
mesh = np.meshgrid(px, py)
surf = mesh[0]**2 / 500 + mesh[1]**2 / 1000
func = np.exp(-mesh[0]**2 / 500.0) * np.exp(-mesh[1]**2 / 750.0) * surf

x, y, z = mesh[0].flatten(), mesh[1].flatten(), surf.flatten()
data = func.flatten()

n0, n1 = func.shape
v_list, f_list = [], []
for i0 in range(n0):
    for j0 in range(n1):
        i1, j1 = i0 + 1, j0 + 1
        v_list.append((
            mesh[0][i0, j0],
            mesh[1][i0, j0],
            surf[i0, j0],
            func[i0, j0]
        ))
for i0 in range(n0 - 1):
    for j0 in range(n1 - 1):
        i1, j1 = i0 + 1, j0 + 1
        v_n00 = i0 * n1 + j0
        v_n01 = v_n00 + 1
        v_n10 = v_n00 + n1
        v_n11 = v_n10 + 1
        val = (func[i0, j0] + func[i0, j1] + func[i1, j0] + func[i1, j1]) / 4
        f_list.append((
            [v_n00, v_n01, v_n11, v_n10],
            val
        ))
vertex = np.array(
    v_list, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('data', 'f4')])
face = np.array(
    f_list, dtype=[('vertex_indices', 'i4', (4,)), ('face_color', 'f4')])
elv = PlyElement.describe(vertex, "vertex")
elf = PlyElement.describe(face, "face")


PlyData([elv, elf], text=True).write('./create_ply_simple1.ply')
