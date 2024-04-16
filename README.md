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