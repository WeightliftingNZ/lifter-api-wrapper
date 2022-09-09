# Lifter API Wrapper

[![Lint](https://github.com/WeightliftingNZ/lifter-api-wrapper/actions/workflows/lint.yml/badge.svg)](https://github.com/ChristchurchCityWeightlifting/lifter-api-wrapper/actions/workflows/lint.yml)
[![Documentation Status](https://readthedocs.org/projects/lifter-api-wrapper/badge/?version=latest)](https://lifter-api-wrapper.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Latest Version](https://img.shields.io/pypi/v/lifter-api-wrapper.svg)](https://pypi.python.org/pypi/lifter-api-wrapper/)
[![Format](https://img.shields.io/pypi/format/lifter-api-wrapper.svg)](https://pypi.python.org/pypi/lifter-api-wrapper/)
[![Python Versions](https://img.shields.io/pypi/pyversions/lifter-api-wrapper.svg)](https://pypi.python.org/pypi/lifter-api-wrapper/)
[![Implementation](https://img.shields.io/pypi/implementation/lifter-api-wrapper.svg)](https://pypi.python.org/pypi/lifter-api-wrapper/)
[![License](https://img.shields.io/pypi/status/lifter-api-wrapper.svg)](https://pypi.python.org/pypi/lifter-api-wrapper/)


This is a wrapper for making calls to [Lifter API](https://github.com/WeightliftingNZ/lifter-api).

## Getting Started

You can install this package using `pip` or your favourite package manager, e.g. `pipenv`, `poetry`.

```sh
pip install lifter-api-wrapper

# example using pipenv
pipenv install lifter-api-wrapper
```

You will also need an API key to have complete functionality. I suggest storing this as a `.env` file, and remember to add this to your `.gitignore` so you don't share this to a public repository by accident.

```sh
# .env

API_TOKEN=KeyGoesHere
```

If you use `pipenv`, then the key is loaded as a environment variable `API_TOKEN`automatically. Otherwise you might have to use a library like `dotenv`.

You can simple create an object like so:

```python
from lifter_api import LifterAPI

import os

lifter_api = LifterAPI(auth_token=os.getenv("API_TOKEN"))

# this will use default version, v1
# you can specify the version

lifter_api_version1 = LifterAPI(version="v1", auth_token=os.getenv("API_TOKEN"))
```
