.PHONY: test

test:
	poetry run python -m unittest discover -v 2>&1 | tee test_output.txt

build:
	poetry build

publish:
	poetry publish

config:
	poetry config pypi-token.pypi your-token-here

reformat:
	poetry run black webtoolkit
