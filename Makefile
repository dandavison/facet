lint:
	find . -type f -name '*.py' | xargs flake8

test:
	python3 -m unittest facet/tests/test_facet.py
