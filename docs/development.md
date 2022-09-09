# Local Development

For local development, you will need to clone the [API from here](https://github.com/WeightliftingNZ/lifter-api).

You will need to set a environment variable, `LOCAL_DEVELOPMENT=1` and it's a good idea to put this in the `.env` file. This will ensure the locally hosted API will be used and not the live API.

The default URL for the locally hosted API is `http://localhost:8000`. Alternatively, you can define the url to your liking: `LifterAPI(url="http://localhost:8001")`.

```bash
git clone https://github.com/WeightliftingNZ/lifter-api

cd lifter-api

make run
```

This will run a server and allow you to run tests for this wrapper.
