.PHONY: clean-pyc clean-build clean
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "watch-test - run tests every time a Python file is saved"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release to the internal PyPI server"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo "develop - bootstrap a development environment"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 flask_nameko tests

develop: clean
	virtualenv --python=python2.7 venv
	. venv/bin/activate && pip install -r requirements_dev.txt

test:
	python setup.py test

watch-test: test
	watchmedo shell-command -p '*.py' -c '$(MAKE) test' -R -D .

test-all:
	tox

coverage:
	coverage run --source flask_nameko setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

release: clean dist
	twine upload -r clefpypi dist/*

dist: clean
	python setup.py sdist
	ls -l dist

install: clean
	python setup.py install
