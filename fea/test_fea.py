import unittest

from fea.openseespy import fea_opensees
from fea.pynite import fea_pynite
from utils.parser import read_json

test_cases = [
    {"name": "complex_pyramid.json", "pynite": True, "openseespy": True},
    {"name": "dino.json", "pynite": True, "openseespy": True},
    {"name": "floating_point.json", "pynite": False, "openseespy": False},
    {"name": "perpendicular_pyramid.json", "pynite": True, "openseespy": True},
    {"name": "simple_pyramid.json", "pynite": True, "openseespy": True},
    {"name": "single_beam.json", "pynite": False, "openseespy": False},
    {"name": "sparse_tower.json", "pynite": False, "openseespy": False},
    {"name": "triangle.json", "pynite": False, "openseespy": False},
]


class TestFEA(unittest.TestCase):
    def test_pynite(self):
        for test_case in test_cases:
            with self.subTest(test_case):
                file_name = test_case["name"]
                nodes, edges = read_json(f"fea/models/{file_name}")
                if test_case["pynite"]:
                    self.assertIsInstance(fea_pynite(nodes, edges), dict)
                else:
                    self.assertRaises(Exception, fea_pynite, nodes, edges)

    def test_openseespy(self):
        for test_case in test_cases:
            with self.subTest(test_case):
                file_name = test_case["name"]
                nodes, edges = read_json(f"fea/models/{file_name}")
                if test_case["openseespy"]:
                    self.assertIsInstance(fea_opensees(nodes, edges), dict)
                else:
                    self.assertRaises(Exception, fea_opensees, nodes, edges)


if __name__ == "__main__":
    unittest.main(verbosity=2)
