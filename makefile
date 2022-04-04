.PHONY: test
test:
	pipenv run pytest -vv

.PHONY: build
build:
	rm -rf build && \
	rm -rf dist && \
	rm -rf lifter_api_wrapper.egg-info && \
	pipenv run python setup.py sdist bdist_wheel

.PHONY: test-upload

test-upload:
	twine upload -r testpypi dist/*
