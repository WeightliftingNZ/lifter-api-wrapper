# Lifter API Wrapper

[![Documentation Status](https://readthedocs.org/projects/lifter-api-wrapper/badge/?version=latest)](https://lifter-api-wrapper.readthedocs.io/en/latest/?badge=latest)
[![Pylint](https://github.com/ChristchurchCityWeightlifting/lifter-api-wrapper/actions/workflows/pylint.yml/badge.svg)](https://github.com/ChristchurchCityWeightlifting/lifter-api-wrapper/actions/workflows/pylint.yml)

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
from lifter_api_wrapper import LifterAPI

import os

lifter_api = LifterAPI(auth_token=os.getenv("API_TOKEN")

# this will use default version, v1
# you can specify the version

lifter_api_version1 = LifterAPI(version="v1", auth_token=os.getenv("API_TOKEN"))
```

## Contribution

I'm a one man show at the moment. This is still in development. So, I will be very conservative for now.
