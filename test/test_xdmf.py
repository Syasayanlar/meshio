# -*- coding: utf-8 -*-
#
import numpy
import pytest

import meshio

import helpers
import legacy_reader
import legacy_writer

vtk = pytest.importorskip("vtk")
lxml = pytest.importorskip("lxml")

test_set_full = [
    helpers.tri_mesh,
    helpers.tri_mesh_2d,
    helpers.triangle6_mesh,
    helpers.quad_mesh,
    helpers.quad8_mesh,
    helpers.tri_quad_mesh,
    helpers.tet_mesh,
    helpers.tet10_mesh,
    helpers.hex_mesh,
    helpers.hex20_mesh,
    helpers.add_point_data(helpers.tri_mesh, 1),
    helpers.add_cell_data(helpers.tri_mesh, 1),
]

test_set_reduced = [
    helpers.tri_mesh,
    helpers.tri_mesh_2d,
    helpers.quad_mesh,
    helpers.tri_quad_mesh,
    helpers.tet_mesh,
    helpers.hex_mesh,
    helpers.add_point_data(helpers.tri_mesh, 1),
    helpers.add_cell_data(helpers.tri_mesh, 1),
]


@pytest.mark.parametrize("mesh", test_set_full)
@pytest.mark.parametrize("data_format", ["XML", "Binary", "HDF"])
def test_xdmf3(mesh, data_format):
    def write(*args, **kwargs):
        return meshio.xdmf_io.write(*args, data_format=data_format, **kwargs)

    helpers.write_read(write, meshio.xdmf_io.read, mesh, 1.0e-15)
    return


@pytest.mark.skipif(not hasattr(vtk, "vtkXdmf3Writer"), reason="Need XDMF3")
@pytest.mark.parametrize("mesh", test_set_reduced)
def test_xdmf3_legacy_writer(mesh):
    # test with legacy writer
    def lw(*args, **kwargs):
        return legacy_writer.write("xdmf3", *args, **kwargs)

    helpers.write_read(lw, meshio.xdmf_io.read, mesh, 1.0e-15)
    return


@pytest.mark.skipif(not hasattr(vtk, "vtkXdmf3Reader"), reason="Need XDMF3")
@pytest.mark.parametrize("mesh", test_set_reduced)
def test_xdmf3_legacy_reader(mesh):
    # test with legacy reader
    def lr(filename):
        return legacy_reader.read("xdmf3", filename)

    helpers.write_read(meshio.xdmf_io.write, lr, mesh, 1.0e-15)
    return


@pytest.mark.skipif(not hasattr(vtk, "vtkXdmfWriter"), reason="Need XDMF3")
@pytest.mark.parametrize(
    "mesh",
    [
        helpers.tri_mesh,
        helpers.quad_mesh,
        helpers.tet_mesh,
        helpers.hex_mesh,
        helpers.add_point_data(helpers.tri_mesh, 1),
        helpers.add_cell_data(helpers.tri_mesh, 1),
    ],
)
def test_xdmf2_legacy_writer(mesh):
    # test with legacy writer
    def lw(*args, **kwargs):
        return legacy_writer.write("xdmf2", *args, **kwargs)

    helpers.write_read(
        lw,
        meshio.xdmf_io.read,
        # The legacy writer stores data in only single precision
        # <https://gitlab.kitware.com/vtk/vtk/issues/17037>
        mesh,
        1.0e-6,
    )
    return


def test_generic_io():
    helpers.generic_io("test.xdmf")
    # With additional, insignificant suffix:
    helpers.generic_io("test.0.xdmf")
    return


def test_time_series():
    # write the data
    filename = "out.xdmf"

    # TODO with ... as writer:
    writer = meshio.XdmfTimeSeriesWriter(filename)
    writer.write_mesh(helpers.tri_mesh_2d)
    n = helpers.tri_mesh_2d.points.shape[0]
    for t in numpy.linspace(0.0, 1.0, 5):
        writer.write_point_data({"phi": numpy.full(n, t)}, t)

    # # and read it again
    # data = meshio.read_xdmf_time_series(filename)
    # print(data.grids)
    # grids[0]["mesh"] == 0
    # exit(1)
    return


if __name__ == "__main__":
    # test_xdmf3_legacy_writer(helpers.tri_mesh)
    test_time_series()
