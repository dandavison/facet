lint:
	find . -type f -name '*.py' | xargs flake8

test:
	nosetests
