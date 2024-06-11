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

## Representation

We are using JSON files to represent inputs (anchors and forces) and trusses (name?, vertices and edges).
