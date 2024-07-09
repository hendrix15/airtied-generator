from __future__ import annotations

import numpy as np


class Vector3:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, obj: Vector3) -> Vector3:
        return Vector3(self.x + obj.x, self.y + obj.y, self.z + obj.z)

    def __sub__(self, obj: Vector3) -> Vector3:
        return Vector3(self.x - obj.x, self.y - obj.y, self.z - obj.z)

    def __mul__(self, obj: Vector3 | float | int) -> Vector3:
        if isinstance(obj, Vector3):
            return Vector3(
                self.y * obj.z - self.z * obj.y,
                self.z * obj.x - self.x * obj.z,
                self.x * obj.y - self.y * obj.x,
            )
        if isinstance(obj, float) or isinstance(obj, int):
            return Vector3(self.x * obj, self.y * obj, self.z * obj)

    def __str__(self) -> str:
        return str("(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")")

    def length(self) -> float:
        return (self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5

    def length2(self) -> float:
        return float(self.x * self.x + self.y * self.y + self.z * self.z)

    def norm(self) -> Vector3:
        length = self.length()
        return Vector3(self.x / length, self.y / length, self.z / length)

    def __eq__(self, other: Vector3) -> bool:
        assert isinstance(other, Vector3)
        if (
            abs(self.x - other.x) < 1e-8
            and abs(self.y - other.y) < 1e-8
            and abs(self.z - other.z) < 1e-8
        ):
            return True
        else:
            return False


class Bool3:
    def __init__(self, x: bool = False, y: bool = False, z: bool = False) -> None:
        self.x = x
        self.y = y
        self.z = z


class Node:
    def __init__(
        self,
        id: str,
        vec: Vector3,
        r_support: Bool3 | None = None,
        t_support: Bool3 | None = None,
        load: Vector3 | None = None,
        fixed: bool = False,
    ) -> None:
        self.id = id
        self.vec = vec
        self.r_support = r_support
        self.t_support = t_support
        self.load = load
        self.fixed = fixed

    def get_json(self) -> dict:
        return {
            "id": self.id,
            "vec": {"x": self.vec.x, "y": self.vec.y, "z": self.vec.z},
            "r_support": (
                {"x": self.r_support.x, "y": self.r_support.y, "z": self.r_support.z}
                if self.r_support
                else None
            ),
            "t_support": (
                {"x": self.t_support.x, "y": self.t_support.y, "z": self.t_support.z}
                if self.t_support
                else None
            ),
            "load": (
                {"x": self.load.x, "y": self.load.y, "z": self.load.z}
                if self.load
                else None
            ),
            "fixed": self.fixed,
        }
    
    def to_array(self):
        return [self.vec.x, self.vec.y, self.vec.z]


class Edge:
    def __init__(self, id: str, u: Node, v: Node) -> None:
        self.id = id
        self.u = u
        self.v = v

    def get_json(self) -> dict:
        return {"id": self.id, "u": self.u.id, "v": self.v.id}

    def length(self) -> float:
        p1 = np.array([self.u.vec.x, self.u.vec.y, self.u.vec.z])
        p2 = np.array([self.v.vec.x, self.v.vec.y, self.v.vec.z])

        squared_dist = np.sum((p1 - p2) ** 2, axis=0)
        return np.sqrt(squared_dist)
