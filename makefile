ARGPATH = .
.PHONY: test
test:
	pipenv run pytest -k $(ARGPATH)

.PHONY: build
build:
	rm -rf build && \
	rm -rf dist && \
	rm -rf lifter_api_wrapper.egg-info && \
	pipenv run python setup.py sdist bdist_wheel

.PHONY: test-upload

test-upload:
	twine upload -r testpypi dist/*

.PHONY: clean
clean:
	rm -rf build && \
	rm -rf dist && \
	rm -rf lifter_api_wrapper.egg-info

.PHONY: docs
docs:
	cd docs && \
	make html

VERSIONTYPE = patch
.PHONY: deploy
deploy:
	make docs
	pipenv run bump2version $(VERSIONTYPE) --verbose --list --allow-dirty
