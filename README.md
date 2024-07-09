# AirTied Generator

## Installation

Install needed packages

```sh
sudo apt-get install python3-dev cmake ninja-build
```

Install poetry

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Install dependencies

```sh
poetry config virtualenvs.in-project true
poetry env use python3.11
poetry install
```

## FEA Analysis

For the FEA analysis of an existing truss structure, two different implementations can be used.

The simple one is based on PyNite and does not require the specification of material coefficients.
Self weight of the beams is not taken into account.

```sh
python analyze.py --input fea/models/dino.json  --fea simple
```

The complex one is based on OpenSeesPy and requires the specification of correct material coefficients.
Self weight of the beams is taken into account.

```sh
python analyze.py --input fea/models/dino.json  --fea complex
```

The material coefficients are specified in the file `fea/coefficients.yaml`. Because `k`, `g`, `nu`, `iy`, `iz` and `j` are currently not known for Airtied, the corresponding coefficients of steel are used. Only `rho` and `a` are specified for the small Airtied beam with 20cm diameter.

## Truss Generation

Generate a truss for a given scenario defined in a config file

```sh
python main.py --config config/tower.yaml
```

For the UCT search the simple FEA is used because of the missing material coefficients.

## Model Representation

Input for scenarios and resulting models are defined in a custom json format

```
{
    "nodes": {
        "node1": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "node2": {
            "x": 0,
            "y": 3,
            "z": 1
        },
        ...
    },
    "edges": {
        "edge1": {
            "start": "node1",
            "end": "node2"
        },
        ...
    },
    "anchors": {
        "node1": {
            "rx": false,
            "ry": false,
            "rz": false,
            "tx": true,
            "ty": true,
            "tz": true
        },
        ...
    },
    "forces": {
        "force1": {
            "nodes": [
                "node1"
            ],
            "x": 0,
            "y": -49,
            "z": 0
        }
        ...
    }
}
```

Convert an obj truss into the used json format

```sh
python convert.py --input dino.obj --output dino.json
```
