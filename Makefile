.PHONY: test

test: test-min test-man
test-min:
	poetry run python -m unittest discover -v 2>&1 | tee test_output.txt
test-man:
	poetry run python manual_test.py

build:
	poetry build

publish:
	poetry publish

config:
	poetry config pypi-token.pypi your-token-here

reformat:
	poetry run black webtoolkit
