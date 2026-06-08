"""Pure trimesh STL loading with validation guards.

Kept separate from preview.py so consumers that only need mesh loading
don't pay the pyrender + PyOpenGL import cost. Only depends on trimesh + numpy.

Source: adapted from flowful-ai/cad-skill (MIT).
"""
import numpy as np
import trimesh


def load_mesh(path):
    """Load an STL file via trimesh.

    Raises ValueError if the file cannot be parsed, contains no geometry,
    has zero faces, or has non-finite vertex coordinates.
    """
    try:
        tm = trimesh.load(path, force="mesh")
    except Exception as e:
        raise ValueError(f"Failed to load STL: {e}") from e
    if not hasattr(tm, "vertices") or len(tm.vertices) == 0:
        raise ValueError("STL file contains no vertices")
    if not hasattr(tm, "faces") or len(tm.faces) == 0:
        raise ValueError("STL file contains no triangles")
    if not np.isfinite(tm.vertices).all():
        raise ValueError("STL file has non-finite vertex coordinates (NaN or inf)")
    # BREP exporters (build123d/CadQuery) write topologically unmerged but
    # geometrically closed meshes; merge before any watertight judgement.
    tm.merge_vertices(digits_vertex=4)
    tm.process(validate=True)
    return tm
