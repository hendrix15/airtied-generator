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

## Pipeline

Start the pipeline

```sh
python main.py
```

## Helper

Convert an obj truss into the used json format

```sh
python convert.py --input dino.obj --output dino.json
```

Analyze an existing truss structure

```sh
python analyze.py --input output/dino.json
```

## Representation

```json
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
