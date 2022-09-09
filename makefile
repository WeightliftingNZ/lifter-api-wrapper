ARGPATH = .
.PHONY: test
test:
	pipenv run pytest -vv -k $(ARGPATH)

# build project
.PHONY: build
build:
	rm -rf build && \
	rm -rf dist && \
	rm -rf lifter_api_wrapper.egg-info && \
	pipenv run python setup.py sdist bdist_wheel

# test an upload
.PHONY: test-upload
test-upload:
	twine upload -r testpypi dist/*

# clean up
.PHONY: clean
clean:
	rm -rf build && \
	rm -rf dist && \
	rm -rf lifter_api_wrapper.egg-info

# install packages and pre-commit
.PHONY: install
install:
	pre-commit install && \
	pre-commit autoupdate && \
	pipenv install --skip-lock --dev

# Serve the documentation
.PHONY: serve-docs
serve-docs:
	pipenv run mkdocs serve --dev-addr '127.0.0.1:8123'

# Deploy the documentation
.PHONY: deploy-docs
deploy-docs:
	pipenv run mkdocs gh-deploy
