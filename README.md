[![Build Status](https://travis-ci.org/dranjan/python-plyfile.svg?branch=master)](https://travis-ci.org/dranjan/python-plyfile)

Welcome to the `plyfile` Python module, which provides a simple facility
for reading and writing ASCII and binary PLY files.

The PLY format is documented
[elsewhere](https://web.archive.org/web/20161221115231/http://www.cs.virginia.edu/~gfx/Courses/2001/Advanced.spring.01/plylib/Ply.txt).

# Installation

## Dependencies

- python2 >= 2.7 or python3
- numpy >= 1.8

**Note:** `numpy` 1.9 before version 1.9.2 has a bug that breaks byte
swapping by manipulating the `byte_order` field of a `PlyData` instance.
As a workaround, you can manually byte-swap your arrays using `el.data =
el.data.byteswap().newbyteorder()` in addition to changing the
`byte_order` attribute.

### Optional dependencies

- setuptools (for installation via setup.py)
- tox (for test suite)
- py.test and py (for test suite)

## Installing plyfile

Quick way:

    pip install plyfile

Or clone the repository and run from the project root:

    python setup.py install

Or just copy `plyfile.py` into your GPL-compatible project.

## Running test suite

Preferred (more comprehensive; requires tox and setuptools):

    tox -v

Alternate (requires py.test and py):

    py.test test -v

# Usage

Both deserialization and serialization of PLY file data is done through
`PlyData` and `PlyElement` instances.

    >>> from plyfile import PlyData, PlyElement

For the code examples that follow, assume the file `tet.ply` contains
the following text:

    ply
    format ascii 1.0
    comment single tetrahedron with colored faces
    element vertex 4
    comment tetrahedron vertices
    property float x
    property float y
    property float z
    element face 4
    property list uchar int vertex_indices
    property uchar red
    property uchar green
    property uchar blue
    end_header
    0 0 0
    0 1 1
    1 0 1
    1 1 0
    3 0 1 2 255 255 255
    3 0 2 3 255 0 0
    3 0 1 3 0 255 0
    3 1 2 3 0 0 255

(This file is available under the `examples` directory.)

## Reading a PLY file

    >>> plydata = PlyData.read('tet.ply')

or

    >>> with open('tet.ply', 'rb') as f:
    ...     plydata = PlyData.read(f)

The static method `PlyData.read` returns a `PlyData` instance, which is
`plyfile`'s representation of the data in a PLY file.  A `PlyData`
instance has an attribute `elements`, which is a list of `PlyElement`
instances, each of which has a `data` attribute which is a `numpy`
structured array containing the numerical data.  PLY file elements map
onto `numpy` structured arrays in a pretty obvious way.  For a list
property in an element, the corresponding `numpy` field type
is `object`, with the members being `numpy` arrays (see the
`vertex_indices` example below).

Concretely:

    >>> plydata.elements[0].name
    'vertex'
    >>> plydata.elements[0].data[0]
    (0.0, 0.0, 0.0)
    >>> plydata.elements[0].data['x']
    array([ 0.,  0.,  1.,  1.], dtype=float32)
    >>> plydata['face'].data['vertex_indices'][0]
    array([0, 1, 2], dtype=int32)

For convenience, elements and properties can be looked up by name:

    >>> plydata['vertex']['x']
    array([ 0.,  0.,  1.,  1.], dtype=float32)

and elements can be indexed directly without explicitly going through
the `data` attribute:

    >>> plydata['vertex'][0]
    (0.0, 0.0, 0.0)

The above expression is equivalent to `plydata['vertex'].data[0]`.

`PlyElement` instances also contain metadata:

    >>> plydata.elements[0].properties
    (PlyProperty('x', 'float'), PlyProperty('y', 'float'),
     PlyProperty('z', 'float'))
    >>> plydata.elements[0].count
    4

`PlyProperty` and `PlyListProperty` instances are used internally as a
convenient intermediate representation of PLY element properties that
can easily be serialized to a PLY header (using `str`) or converted to
`numpy`-compatible type descriptions (via the `dtype` method).  It's not
extremely common to manipulate them directly, but if needed, the
property metadata of an element can be accessed as a tuple via the
`properties` attribute (as illustrated above) or looked up by name:

    >>> plydata.elements[0].ply_property('x')
    PlyProperty('x', 'float')

Many (but not necessarily all) types of malformed input files will raise
`PlyParseError` when `PlyData.read` is called.  The string value of the
`PlyParseError` instance (as well as attributes `element`, `row`, and
`prop`) provides additional context for the error if applicable.

## Creating a PLY file

The first step is to get your data into `numpy` structured arrays.  Note
that there are some restrictions: generally speaking, if you know the
types of properties a PLY file element can contain, you can easily
deduce the restrictions.  For example, PLY files don't contain 64-bit
integer or complex data, so these aren't allowed.

For convenience, non-scalar fields **are** allowed; they will be
serialized as list properties.  For example, when constructing a "face"
element, if all the faces are triangles (a common occurrence), it's okay
to have a  "vertex_indices" field of type `'i4'` and shape `(3,)`
instead of type `object` and shape `()`.  However, if the serialized PLY
file is read back in using `plyfile`, the "vertex_indices" property will
be represented as an `object`-typed field, each of whose values is an
array of type `'i4'` and length 3.  The reason is simply that the PLY
format provides no way to find out that each "vertex_indices" field has
length 3 without actually reading all the data, so `plyfile` has to
assume that this is a variable-length property.  However, see below (and
`examples/plot.py`) for an easy way to recover a two-dimensional array
from a list property.

For example, if we wanted to create the "vertex" and "face" PLY elements
of the `tet.ply` data directly as `numpy` arrays for the purpose of
serialization, we could do (as in `test/test.py`):

    >>> vertex = numpy.array([(0, 0, 0),
    ...                       (0, 1, 1),
    ...                       (1, 0, 1),
    ...                       (1, 1, 0)],
    ...                      dtype=[('x', 'f4'), ('y', 'f4'),
    ...                             ('z', 'f4')])
    >>> face = numpy.array([([0, 1, 2], 255, 255, 255),
    ...                     ([0, 2, 3], 255,   0,   0),
    ...                     ([0, 1, 3],   0, 255,   0),
    ...                     ([1, 2, 3],   0,   0, 255)],
    ...                    dtype=[('vertex_indices', 'i4', (3,)),
    ...                           ('red', 'u1'), ('green', 'u1'),
    ...                           ('blue', 'u1')])

Once you have suitably structured array, the static method
`PlyElement.describe` can then be used to create the necessary
`PlyElement` instances:

    >>> el = PlyElement.describe(some_array, 'some_name')

or

    >>> el = PlyElement.describe(some_array, 'some_name',
    ...                          comments=['comment1',
    ...                                    'comment2'])

Note that there's no need to create `PlyProperty` instances explicitly.
This is all done behind the scenes by examining `some_array.dtype.descr`.
One slight hiccup here is that variable-length fields in a `numpy` array
(i.e., our representation of PLY list properties)
must have a type of `object`, so the types of the list length and values
in the serialized PLY file can't be obtained from the array's `dtype`
attribute alone.  For simplicity and predictability, the length
defaults to 8-bit unsigned integer, and the value defaults to 32-bit
signed integer, which covers the majority of use cases.  Exceptions must
be stated explicitly:

    >>> el = PlyElement.describe(some_array, 'some_name',
    ...                          val_dtypes={'some_property': 'f8'},
    ...                          len_dtypes={'some_property': 'u4'})

Now you can instantiate `PlyData` and serialize:

    >>> PlyData([el]).write('some_binary.ply')
    >>> PlyData([el], text=True).write('some_ascii.ply')

    # Force the byte order of the output to big-endian, independently of
    # the machine's native byte order
    >>> PlyData([el],
    ...         byte_order='>').write('some_big_endian_binary.ply')

    # Use a file object.  Binary mode is used here, which will cause
    # Unix-style line endings to be written on all systems.
    >>> with open('some_ascii.ply', mode='wb') as f:
    ...     PlyData([el], text=True).write(f)

## Miscellaneous

### Comments

Header comments are supported:

    >>> ply = PlyData([el], comments=['header comment'])
    >>> ply.comments
    ['header comment']

As of version 0.3, "obj_info" comments are supported as well:

    >>> ply = PlyData([el], obj_info=['obj_info1', 'obj_info2'])
    >>> ply.obj_info
    ['obj_info1', 'obj_info2']

When written, they will be placed after regular comments after the
"format" line.

Comments can have leading whitespace, but trailing whitespace may be
stripped and should not be relied upon.  Comments may not contain
embedded newlines.

### Getting a two-dimensional array from a list property

The PLY format provides no way to assert that all the data for a given
list property is of the same length, yet this is a relatively common
occurrence.  For example, all the "vertex_indices" data on a "face"
element will have length three for a triangular mesh.  In such cases,
it's usually much more convenient to have the data in a two-dimensional
array, as opposed to a one-dimensional array of type `object`.  Here's a
pretty easy way to obtain a two dimensional array, assuming we know the
row length in advance:

    >>> plydata = PlyData.read('tet.ply')
    >>> tri_data = plydata['face'].data['vertex_indices']
    >>> triangles = numpy.vstack(tri_data)

### Instance mutability

A plausible code pattern is to read a PLY file into a `PlyData`
instance, perform some operations on it, possibly modifying data and
metadata in place, and write the result to a new file.  This pattern is
partially supported.  As of version 0.4, the following in-place
mutations are supported:

- Modifying numerical array data only.
- Assigning directly to a `PlyData` instance's `elements`.
- Switching format by changing the `text` and `byte_order` attributes of
  a `PlyData` instance.   This will switch between `ascii`,
  `binary_little_endian`, and `binary_big_endian` PLY formats.
- Modifying a `PlyData` instance's `comments` and `obj_info`, and
  modifying a `PlyElement` instance's `comments`.
- Assigning to an element's `data`.  Note that the property metadata in
  `properties` is not touched by this, so for every property in the
  `properties` list of the `PlyElement` instance, the `data` array must
  have a field with the same name (but possibly different type, and
  possibly in different order).  The array can have additional fields as
  well, but they won't be output when writing the element to a PLY file.
  The properties in the output file will appear as they are in the
  `properties` list.  If an array field has a different type than the
  corresponding `PlyProperty` instance, then it will be cast when
  writing.
- Assigning directly to an element's `properties`.  Note that the
  `data` array is not touched, and the previous note regarding the
  relationship between `properties` and `data` still applies: the field
  names of `data` must be a subset of the property names in
  `properties`, but they can be in a different order and specify
  different types.
- Changing a `PlyProperty` or `PlyListProperty` instance's `val_dtype`
  or a `PlyListProperty` instance's `len_dtype`, which will perform
  casting when writing.

Modifying the `name` of a `PlyElement`, `PlyProperty`, or
`PlyListProperty` instance is not supported and will raise an error.  To
rename a property of a `PlyElement` instance, you can remove the
property from `properties`, rename the field in `data`, and re-add the
property to `properties` with the new name by creating a new
`PlyProperty` or `PlyListProperty` instance:

    >>> from plyfile import PlyProperty, PlyListProperty
    >>> face = plydata['face']
    >>> face.properties = ()
    >>> face.data.dtype.names = ['idx', 'r', 'g', 'b']
    >>> face.properties = (PlyListProperty('idx', 'uchar', 'int'),
    ...                    PlyProperty('r', 'uchar'),
    ...                    PlyProperty('g', 'uchar'),
    ...                    PlyProperty('b', 'uchar'))

Note that it is always safe to create a new `PlyElement` or `PlyData`
instance instead of modifying one in place, and this is the recommended
style:

    >>> # Recommended:
    >>> plydata = PlyData([plydata['face'], plydata['vertex']],
                          text=False, byte_order='<')

    >>> # Also supported:
    >>> plydata.elements = [plydata['face'], plydata['vertex']]
    >>> plydata.text = False
    >>> plydata.byte_order = '<'
    >>> plydata.comments = []
    >>> plydata.obj_info = []

Objects created by this library don't claim ownership of the other
objects they refer to, which has implications for both styles (creating
new instances and modifying in place).  For example, a single
`PlyElement` instance can be contained by multiple `PlyData` instances,
but modifying that instance will then affect all of those containing
`PlyData` instances.

# Design philosophy and rationale

At the time that I wrote this, I didn't know of any simple and
self-contained Python PLY file module using `numpy` as its data
representation medium.  Considering the increasing prevalence of Python
as a tool for scientific programming with NumPy as the _lingua franca_
for numerical data, such a module seemed desirable; hence, `plyfile` was
born.

## Familiarity

I opted to use existing Python and NumPy constructs whenever they
matched the data.  Thus, the `elements` attribute of a `PlyData`
instance is simply a `list` of `PlyElement` instances, and the `data`
attribute of a `PlyElement` instance is a `numpy` array, and a list
property field of a PLY element datum is referred to in the `data`
attribute by a type of `object` with the value being another `numpy`
array, etc.  In the last case, this is certainly not the most-efficient
in-memory representation of the data, since it contains a lot of
indirection.  However, it is arguably the most obvious and natural
unless NumPy adds explicit support for "ragged" arrays in its type
system.  The design goal was to represent data in a form familiar to
users of `numpy`.

## Simplicity

When the two were at odds, I decided to favor simplicity over power or
user-friendliness.  Thus, list property types in `PlyElement.describe`
always default to the same, rather than, say, being obtained by looking
at an array element.  (Which element?  What if the array has length
zero?  Whatever default we could choose in that case could lead to
subtle edge-case bugs if the user isn't vigilant.)  Also, all input and
output is done in "one shot": all the arrays must be created up front
rather than being processed in a streaming fashion.  (That said, I have
nothing against streamability, and I considered it at one point.  I
decided against it for now in order to have a consistent and
maintainable interface at least for the first usable version.)

## Interpretation issues

There doesn't seem to be a single complete and consistent description of
the PLY format.  Even the "authoritative"
[Ply.txt](https://web.archive.org/web/20161221115231/http://www.cs.virginia.edu/~gfx/Courses/2001/Advanced.spring.01/plylib/Ply.txt)
by Greg Turk has some issues.

### Comment placement

Where can comments appear in the header?  It appears that in all the
"official" examples, all comments immediately follow the "format" line,
but the language of the document neither places any such restrictions
nor explicitly allows comments to be placed anywhere else.  Thus, it
isn't clear whether comments can appear anywhere in the header or must
immediately follow the "format" line.  At least one popular reader of
PLY files chokes on comments before the "format" line.  `plyfile`
accepts comments anywhere in the header in input but only places them in
a few limited places in output, namely immediately after "format" and
"element" lines.

### Element and property names

Another ambiguity is names: what strings are allowed as PLY element and
property names?  `plyfile` accepts as input any name that doesn't
contain spaces, but this is surely too generous.  This may not be such
a big deal, though: although names are theoretically arbitrary, in
practice, the majority of PLY element and property names probably come
from a small finite set ("face", "x", "nx", "green", etc.).

### Property syntax

A more serious problem is that the PLY format specification appears to
be inconsistent regarding the syntax of property definitions.  In
some examples, it uses the syntax

    property {type} {name}

and in others,

    property {name} {type}

`plyfile` only supports the former, which appears to be standard _de
facto_.

### Header line endings

The specification explicitly states that lines in the header must
end with carriage returns, but this rule doesn't seem to be followed by
anyone, including the C-language PLY implementation by Greg Turk, the
author of the format.  Here, we stick to common practice and output
Unix-style line endings (with no carriage returns) but accept any line
ending style in input files.

# More examples

Examples beyond the scope of this document and the tests are in the
`examples` directory.

# Credits

Author: Darsh Ranjan

# License

This software is released under the terms of the GNU General Public
License, version 3.  See the file `COPYING` for details.

numpy-stl
==============================================================================

Simple library to make working with STL files (and 3D objects in general) fast
and easy.

Due to all operations heavily relying on `numpy` this is one of the fastest
STL editing libraries for Python available.

Links
-----

 - The source: https://github.com/WoLpH/numpy-stl
 - Project page: https://pypi.python.org/pypi/numpy-stl
 - Reporting bugs: https://github.com/WoLpH/numpy-stl/issues
 - Documentation: http://numpy-stl.readthedocs.org/en/latest/
 - My blog: https://wol.ph/

Requirements for installing:
------------------------------------------------------------------------------

 - `numpy`_ any recent version
 - `python-utils`_ version 1.6 or greater

Installation:
------------------------------------------------------------------------------

`pip install numpy-stl`

Initial usage:
------------------------------------------------------------------------------

 - `stl2bin your_ascii_stl_file.stl new_binary_stl_file.stl`
 - `stl2ascii your_binary_stl_file.stl new_ascii_stl_file.stl`
 - `stl your_ascii_stl_file.stl new_binary_stl_file.stl`

Quickstart
------------------------------------------------------------------------------

.. code-block:: python

    import numpy
    from stl import mesh

    # Using an existing stl file:
    your_mesh = mesh.Mesh.from_file('some_file.stl')

    # Or creating a new mesh (make sure not to overwrite the `mesh` import by
    # naming it `mesh`):
    VERTICE_COUNT = 100
    data = numpy.zeros(VERTICE_COUNT, dtype=mesh.Mesh.dtype)
    your_mesh = mesh.Mesh(data, remove_empty_areas=False)

    # The mesh normals (calculated automatically)
    your_mesh.normals
    # The mesh vectors
    your_mesh.v0, your_mesh.v1, your_mesh.v2
    # Accessing individual points (concatenation of v0, v1 and v2 in triplets)
    assert (your_mesh.points[0][0:3] == your_mesh.v0[0]).all()
    assert (your_mesh.points[0][3:6] == your_mesh.v1[0]).all()
    assert (your_mesh.points[0][6:9] == your_mesh.v2[0]).all()
    assert (your_mesh.points[1][0:3] == your_mesh.v0[1]).all()

    your_mesh.save('new_stl_file.stl')

Plotting using `matplotlib`_ is equally easy:

.. code-block:: python

    from stl import mesh
    from mpl_toolkits import mplot3d
    from matplotlib import pyplot

    # Create a new plot
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)

    # Load the STL files and add the vectors to the plot
    your_mesh = mesh.Mesh.from_file('tests/stl_binary/HalfDonut.stl')
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

    # Auto scale to the mesh size
    scale = your_mesh.points.flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.show()

.. _numpy: http://numpy.org/
.. _matplotlib: http://matplotlib.org/
.. _python-utils: https://github.com/WoLpH/python-utils

Modifying Mesh objects
------------------------------------------------------------------------------

.. code-block:: python

    from stl import mesh
    import math
    import numpy

    # Create 3 faces of a cube
    data = numpy.zeros(6, dtype=mesh.Mesh.dtype)

    # Top of the cube
    data['vectors'][0] = numpy.array([[0, 1, 1],
                                      [1, 0, 1],
                                      [0, 0, 1]])
    data['vectors'][1] = numpy.array([[1, 0, 1],
                                      [0, 1, 1],
                                      [1, 1, 1]])
    # Right face
    data['vectors'][2] = numpy.array([[1, 0, 0],
                                      [1, 0, 1],
                                      [1, 1, 0]])
    data['vectors'][3] = numpy.array([[1, 1, 1],
                                      [1, 0, 1],
                                      [1, 1, 0]])
    # Left face
    data['vectors'][4] = numpy.array([[0, 0, 0],
                                      [1, 0, 0],
                                      [1, 0, 1]])
    data['vectors'][5] = numpy.array([[0, 0, 0],
                                      [0, 0, 1],
                                      [1, 0, 1]])

    # Since the cube faces are from 0 to 1 we can move it to the middle by
    # substracting .5
    data['vectors'] -= .5

    # Generate 4 different meshes so we can rotate them later
    meshes = [mesh.Mesh(data.copy()) for _ in range(4)]

    # Rotate 90 degrees over the Y axis
    meshes[0].rotate([0.0, 0.5, 0.0], math.radians(90))

    # Translate 2 points over the X axis
    meshes[1].x += 2

    # Rotate 90 degrees over the X axis
    meshes[2].rotate([0.5, 0.0, 0.0], math.radians(90))
    # Translate 2 points over the X and Y points
    meshes[2].x += 2
    meshes[2].y += 2

    # Rotate 90 degrees over the X and Y axis
    meshes[3].rotate([0.5, 0.0, 0.0], math.radians(90))
    meshes[3].rotate([0.0, 0.5, 0.0], math.radians(90))
    # Translate 2 points over the Y axis
    meshes[3].y += 2


    # Optionally render the rotated cube faces
    from matplotlib import pyplot
    from mpl_toolkits import mplot3d

    # Create a new plot
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)

    # Render the cube faces
    for m in meshes:
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(m.vectors))

    # Auto scale to the mesh size
    scale = numpy.concatenate([m.points for m in meshes]).flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.show()

Extending Mesh objects
------------------------------------------------------------------------------

.. code-block:: python

    from stl import mesh
    import math
    import numpy

    # Create 3 faces of a cube
    data = numpy.zeros(6, dtype=mesh.Mesh.dtype)

    # Top of the cube
    data['vectors'][0] = numpy.array([[0, 1, 1],
                                      [1, 0, 1],
                                      [0, 0, 1]])
    data['vectors'][1] = numpy.array([[1, 0, 1],
                                      [0, 1, 1],
                                      [1, 1, 1]])
    # Right face
    data['vectors'][2] = numpy.array([[1, 0, 0],
                                      [1, 0, 1],
                                      [1, 1, 0]])
    data['vectors'][3] = numpy.array([[1, 1, 1],
                                      [1, 0, 1],
                                      [1, 1, 0]])
    # Left face
    data['vectors'][4] = numpy.array([[0, 0, 0],
                                      [1, 0, 0],
                                      [1, 0, 1]])
    data['vectors'][5] = numpy.array([[0, 0, 0],
                                      [0, 0, 1],
                                      [1, 0, 1]])

    # Since the cube faces are from 0 to 1 we can move it to the middle by
    # substracting .5
    data['vectors'] -= .5

    cube_back = mesh.Mesh(data.copy())
    cube_front = mesh.Mesh(data.copy())

    # Rotate 90 degrees over the X axis followed by the Y axis followed by the
    # X axis
    cube_back.rotate([0.5, 0.0, 0.0], math.radians(90))
    cube_back.rotate([0.0, 0.5, 0.0], math.radians(90))
    cube_back.rotate([0.5, 0.0, 0.0], math.radians(90))

    cube = mesh.Mesh(numpy.concatenate([
        cube_back.data.copy(),
        cube_front.data.copy(),
    ]))

    # Optionally render the rotated cube faces
    from matplotlib import pyplot
    from mpl_toolkits import mplot3d

    # Create a new plot
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)

    # Render the cube
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(cube.vectors))

    # Auto scale to the mesh size
    scale = cube_back.points.flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.show()

Creating Mesh objects from a list of vertices and faces
------------------------------------------------------------------------------

.. code-block:: python

    import numpy as np
    from stl import mesh

    # Define the 8 vertices of the cube
    vertices = np.array([\
        [-1, -1, -1],
        [+1, -1, -1],
        [+1, +1, -1],
        [-1, +1, -1],
        [-1, -1, +1],
        [+1, -1, +1],
        [+1, +1, +1],
        [-1, +1, +1]])
    # Define the 12 triangles composing the cube
    faces = np.array([\
        [0,3,1],
        [1,3,2],
        [0,4,7],
        [0,7,3],
        [4,5,6],
        [4,6,7],
        [5,1,2],
        [5,2,6],
        [2,3,6],
        [3,7,6],
        [0,1,5],
        [0,5,4]])

    # Create the mesh
    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[f[j],:]

    # Write the mesh to file "cube.stl"
    cube.save('cube.stl')

Evaluating Mesh properties (Volume, Center of gravity, Inertia)
------------------------------------------------------------------------------

.. code-block:: python

    import numpy as np
    from stl import mesh

    # Using an existing closed stl file:
    your_mesh = mesh.Mesh.from_file('some_file.stl')

    volume, cog, inertia = your_mesh.get_mass_properties()
    print("Volume                                  = {0}".format(volume))
    print("Position of the center of gravity (COG) = {0}".format(cog))
    print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
    print("                                          {0}".format(inertia[1,:]))
    print("                                          {0}".format(inertia[2,:]))

Combining multiple STL files
------------------------------------------------------------------------------

.. code-block:: python

    import math
    import stl
    from stl import mesh
    import numpy


    # find the max dimensions, so we can know the bounding box, getting the height,
    # width, length (because these are the step size)...
    def find_mins_maxs(obj):
        minx = maxx = miny = maxy = minz = maxz = None
        for p in obj.points:
            # p contains (x, y, z)
            if minx is None:
                minx = p[stl.Dimension.X]
                maxx = p[stl.Dimension.X]
                miny = p[stl.Dimension.Y]
                maxy = p[stl.Dimension.Y]
                minz = p[stl.Dimension.Z]
                maxz = p[stl.Dimension.Z]
            else:
                maxx = max(p[stl.Dimension.X], maxx)
                minx = min(p[stl.Dimension.X], minx)
                maxy = max(p[stl.Dimension.Y], maxy)
                miny = min(p[stl.Dimension.Y], miny)
                maxz = max(p[stl.Dimension.Z], maxz)
                minz = min(p[stl.Dimension.Z], minz)
        return minx, maxx, miny, maxy, minz, maxz


    def translate(_solid, step, padding, multiplier, axis):
        if axis == 'x':
            items = [0, 3, 6]
        elif axis == 'y':
            items = [1, 4, 7]
        elif axis == 'z':
            items = [2, 5, 8]
        for p in _solid.points:
            # point items are ((x, y, z), (x, y, z), (x, y, z))
            for i in range(3):
                p[items[i]] += (step * multiplier) + (padding * multiplier)


    def copy_obj(obj, dims, num_rows, num_cols, num_layers):
        w, l, h = dims
        copies = []
        for layer in range(num_layers):
            for row in range(num_rows):
                for col in range(num_cols):
                    # skip the position where original being copied is
                    if row == 0 and col == 0 and layer == 0:
                        continue
                    _copy = mesh.Mesh(obj.data.copy())
                    # pad the space between objects by 10% of the dimension being
                    # translated
                    if col != 0:
                        translate(_copy, w, w / 10., col, 'x')
                    if row != 0:
                        translate(_copy, l, l / 10., row, 'y')
                    if layer != 0:
                        translate(_copy, h, h / 10., layer, 'z')
                    copies.append(_copy)
        return copies

    # Using an existing stl file:
    main_body = mesh.Mesh.from_file('ball_and_socket_simplified_-_main_body.stl')

    # rotate along Y
    main_body.rotate([0.0, 0.5, 0.0], math.radians(90))

    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(main_body)
    w1 = maxx - minx
    l1 = maxy - miny
    h1 = maxz - minz
    copies = copy_obj(main_body, (w1, l1, h1), 2, 2, 1)

    # I wanted to add another related STL to the final STL
    twist_lock = mesh.Mesh.from_file('ball_and_socket_simplified_-_twist_lock.stl')
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(twist_lock)
    w2 = maxx - minx
    l2 = maxy - miny
    h2 = maxz - minz
    translate(twist_lock, w1, w1 / 10., 3, 'x')
    copies2 = copy_obj(twist_lock, (w2, l2, h2), 2, 2, 1)
    combined = mesh.Mesh(numpy.concatenate([main_body.data, twist_lock.data] +
                                        [copy.data for copy in copies] +
                                        [copy.data for copy in copies2]))

    combined.save('combined.stl', mode=stl.Mode.ASCII)  # save as ASCII
