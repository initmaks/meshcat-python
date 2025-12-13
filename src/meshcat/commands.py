from .geometry import Geometry, Object, Mesh, MeshPhongMaterial, OrthographicCamera, PerspectiveCamera, PointsMaterial, Points, TextTexture, InstancedMesh
from .path import Path


class SetObject:
    __slots__ = ["object", "path"]
    def __init__(self, geometry_or_object, material=None, path=None):
        if isinstance(geometry_or_object, Object):
            if material is not None:
                raise(ValueError("Please supply either an Object OR a Geometry and a Material"))
            self.object = geometry_or_object
        elif isinstance(geometry_or_object, (OrthographicCamera, PerspectiveCamera, InstancedMesh)):
            self.object = geometry_or_object
        else:
            if material is None:
                material = MeshPhongMaterial()
            if isinstance(material, PointsMaterial):
                self.object = Points(geometry_or_object, material)
            else:
                self.object = Mesh(geometry_or_object, material)
        if path is not None:
            self.path = path
        else:
            self.path = Path()

    def lower(self):
        return {
            u"type": u"set_object",
            u"object": self.object.lower(),
            u"path": self.path.lower()
        }


class SetTransform:
    __slots__ = ["matrix", "path"]
    def __init__(self, matrix, path):
        self.matrix = matrix
        self.path = path

    def lower(self):
        return {
            u"type": u"set_transform",
            u"path": self.path.lower(),
            u"matrix": list(self.matrix.T.flatten())
        }


class SetCamTarget:
    """Set the camera target point."""
    __slots__ = ["value"]
    def __init__(self, pos):
        self.value = pos

    def lower(self):
        return {
            u"type": "set_target",
            u"path": "",
            u"value": list(self.value)
        }


class CaptureImage:

    def __init__(self, xres=None, yres=None):
        self.xres = xres
        self.yres = yres

    def lower(self):
        data = {
            u"type": u"capture_image"
        }
        if self.xres:
            data[u"xres"] = self.xres
        if self.yres:
            data[u"yres"] = self.yres
        return data


class Delete:
    __slots__ = ["path"]
    def __init__(self, path):
        self.path = path

    def lower(self):
        return {
            u"type": u"delete",
            u"path": self.path.lower()
        }

class SetProperty:
    __slots__ = ["path", "key", "value"]
    def __init__(self, key, value, path):
        self.key = key
        self.value = value
        self.path = path

    def lower(self):
        return {
            u"type": u"set_property",
            u"path": self.path.lower(),
            u"property": self.key.lower(),
            u"value": self.value
        }

class SetAnimation:
    __slots__ = ["animation", "play", "repetitions"]

    def __init__(self, animation, play=True, repetitions=1):
        self.animation = animation
        self.play = play
        self.repetitions = repetitions

    def lower(self):
        return {
            u"type": u"set_animation",
            u"animations": self.animation.lower(),
            u"options": {
                u"play": self.play,
                u"repetitions": self.repetitions
            },
            u"path": ""
        }


class SetInstanceMatrices:
    """
    Command to efficiently update instance matrices for an InstancedMesh.

    This allows updating the transforms of all instances without re-sending
    the geometry and material data, making it ideal for animating thousands
    of instances.
    """
    __slots__ = ["matrices", "path"]

    def __init__(self, matrices, path):
        """
        Args:
            matrices: numpy array of shape (N, 4, 4) containing transformation
                     matrices for each instance
            path: Path object indicating the location of the InstancedMesh
        """
        import numpy as np
        self.matrices = np.asarray(matrices, dtype=np.float32)
        self.path = path

    def lower(self):
        from .geometry import pack_numpy_array
        # Transpose each matrix for column-major order (Three.js convention)
        # and flatten to a single array
        matrices_flat = self.matrices.transpose(0, 2, 1).reshape(-1).astype(self.matrices.dtype)
        return {
            u"type": u"set_instance_matrices",
            u"path": self.path.lower(),
            u"matrices": pack_numpy_array(matrices_flat)
        }


class SetInstanceColors:
    """
    Command to efficiently update instance colors for an InstancedMesh.

    This allows updating the colors of all instances without re-sending
    the geometry and material data.
    """
    __slots__ = ["colors", "path"]

    def __init__(self, colors, path):
        """
        Args:
            colors: numpy array of shape (N, 3) or (N, 4) containing RGB/RGBA
                   color values in range [0, 1] for each instance
            path: Path object indicating the location of the InstancedMesh
        """
        import numpy as np
        colors = np.asarray(colors, dtype=np.float32)
        # Ensure RGBA format
        if colors.ndim == 2 and colors.shape[1] == 3:
            rgba = np.ones((colors.shape[0], 4), dtype=np.float32)
            rgba[:, :3] = colors
            colors = rgba
        self.colors = colors
        self.path = path

    def lower(self):
        from .geometry import pack_numpy_array
        return {
            u"type": u"set_instance_colors",
            u"path": self.path.lower(),
            u"colors": pack_numpy_array(self.colors.reshape(-1))
        }
