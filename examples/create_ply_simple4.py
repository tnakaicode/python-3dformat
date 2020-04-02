import numpy as np
import sys
from plyfile import PlyData
from plyfile import PlyElement, PlyListProperty


class PlySquare(object):

    def __init__(self):
        super().__init__()
        pt = np.linspace(0, 1, 100) * 2 * np.pi
        pz = np.linspace(0, 1, 200)

        mesh = np.meshgrid(pt, pz)
        x = 11 * np.cos(mesh[0])
        y = 10 * np.sin(mesh[0])
        z = 15 * mesh[1]
        func = np.exp(-mesh[0]**2 / 500.0) * np.exp(-mesh[1]**2 / 750.0)
        self.exprt_surf(x, y, z, func)

    def exprt_surf(self, x, y, z, dat):
        n0, n1 = z.shape
        v_list, f_list = [], []
        for i0 in range(n0):
            for j0 in range(n1):
                i1, j1 = i0 + 1, j0 + 1
                v_list.append((x[i0, j0], y[i0, j0], z[i0, j0], dat[i0, j0]))
        vertex = np.array(
            v_list, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('data', 'f4')])

        for i0 in range(n0 - 1):
            for j0 in range(n1 - 1):
                i1, j1 = i0 + 1, j0 + 1
                v_n00 = i0 * n1 + j0
                v_n01 = v_n00 + 1
                v_n10 = v_n00 + n1
                v_n11 = v_n10 + 1
                f_list.append((
                    [v_n00, v_n01, v_n10],
                ))
                f_list.append((
                    [v_n01, v_n10, v_n11],
                ))

        face = np.array(f_list, dtype=[('vertex_indices', 'i4', (3,))])

        elv = PlyElement.describe(vertex, "vertex")
        elf = PlyElement.describe(face, "face")
        PlyData([elv, elf], text=True).write('./create_ply_simple4.ply')


if __name__ == '__main__':
    obj = PlySquare()
