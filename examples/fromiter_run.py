import numpy as np
from mayavi import mlab
from plyfile import PlyData
from itertools import combinations

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(np.r_[a, b])

iterable = (x * x for x in range(5))
print(np.fromiter(iterable, float))

ply = PlyData.read("./tet.ply")
print(ply.elements)
print(ply['vertex'])
print(ply['face'])
print(ply['face']['vertex_indices'])
print(ply['face'].count)

data = []
for idx, dat in enumerate(ply['face']['vertex_indices']):
    data.append((dat[0], dat[1], dat[2]))
print(data)


def test_triangular_mesh():
    """An example of a cone, ie a non-regular mesh defined by its
        triangles.
    """
    n = 8
    t = np.linspace(-np.pi, np.pi, n)
    z = np.exp(1j * t)
    x = z.real.copy()
    y = z.imag.copy()
    z = np.zeros_like(x)

    triangles = [(0, i, i + 1) for i in range(1, n)]
    # Joining arrays for axs=0
    px = np.r_[1, x]
    py = np.r_[1, y]
    pz = np.r_[1, z]
    pt = np.r_[0, t]
    print(x)
    print(px)
    print(triangles)

    #
    # https://docs.enthought.com/mayavi/mayavi/auto/mlab_helper_functions.html#triangular-mesh
    #
    # triangular_mesh(x, y, z, triangles ...)
    # x, y, z are arrays giving the positions of the vertices of the surface.
    # triangles is a list of triplets (or an array) list the vertices in each triangle.
    # Vertices are indexes by their appearance number in the position arrays.
    return mlab.triangular_mesh(px, py, pz, triangles, scalars=pt)


test_triangular_mesh()
mlab.show()
