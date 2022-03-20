run:
	pipenv run python main.py

.PHONY test
test:
	pipenv run pytest -vv
