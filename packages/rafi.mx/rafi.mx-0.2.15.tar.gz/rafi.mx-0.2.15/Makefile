.DEFAULT_GOAL := test

NAME = mx

build:
	python build.py

clean:
	find . -name __pycache__ -type d | xargs rm -rf; \
	rm -rf src/*.egg-info dist

develop:
	python setup.py develop

install:
	python setup.py install

publish: clean build
	python setup.py register sdist upload

test:
	py.test .

uninstall:
	pip uninstall $(NAME)
