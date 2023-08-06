.PHONY: all list install test lint coverage version release

PACKAGE := oki
VERSION := $(shell head -n 1 opendata/VERSION)

all: install

# http://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: \
	'/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | \
	sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

install:
	pip install -e .
	pip install --upgrade tox twine

test:
	PACKAGE=$(PACKAGE) tox

lint:
	pylint $(PACKAGE)

coverage:
	coverage run --source=$(PACKAGE)

version:
	@echo $(VERSION)

release:
	# git tag $(VERSION)
	# git push --tags
	python setup.py sdist bdist_wheel --universal && twine upload dist/*

register:
	python setup.py register -r pypi
