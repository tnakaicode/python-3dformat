import numpy as np
from mayavi import mlab
from plyfile import PlyData
from plyfile import PlyElement, PlyProperty, PlyListProperty

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

ply = PlyData()
print(ply)
