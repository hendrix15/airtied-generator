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

We are using JSON files to represent inputs (anchors and forces) and trusses (name?, vertices and edges).
