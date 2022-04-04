# Lifter API Wrapper

[![Lint](https://github.com/ChristchurchCityWeightlifting/lifter-api-wrapper/actions/workflows/lint.yml/badge.svg)](https://github.com/ChristchurchCityWeightlifting/lifter-api-wrapper/actions/workflows/lint.yml)
[![Documentation Status](https://readthedocs.org/projects/lifter-api-wrapper/badge/?version=latest)](https://lifter-api-wrapper.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is a Python wrapper to access the Lifter API

## Installing and Setting Up

You can install this package using `pip` or your favourite package manager, e.g. `pipenv`, `poetry`, `conda`.

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

## Documentation

[Comprehensive documentation can be found here.](https://lifter-api-wrapper.readthedocs.io/en/latest/)

You can simple create an object like so:

```python
from lifter_api import LifterAPI

import os

lifter_api = LifterAPI(auth_token=os.getenv("API_TOKEN"))

# this will use default version, v1
# you can specify the version

lifter_api_version1 = LifterAPI(version="v1", auth_token=os.getenv("API_TOKEN"))
```

## For Local Development

For local development, you will need to download the [API from here](https://github.com/ChristchurchCityWeightlifting/lifter-api).

You will need to set a environment variable, `LOCAL_DEVELOPMENT=1` and it's a good idea to put this in the `.env` file. This will means the localhost API will be hit and not the live API.

## Contribution

I'm a one man show at the moment. This is still in development. So, I will be very conservative for now.
