from __future__ import annotations


class Vector3:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.z = z

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


class Node:
    def __init__(
        self, id: str, vec: Vector3, support: bool = False, load: Vector3 | None = None
    ) -> None:
        self.id = id
        self.vec = vec
        self.support = support
        self.load = load


class Bar:
    def __init__(self, id: str, u: Node, v: Node) -> None:
        self.id = id
        self.u = u
        self.v = v
