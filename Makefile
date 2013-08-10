all: unit

export PYTHONPATH:=${PWD}

unit:
	@echo "Running unit tests"
	@nosetests -s --verbosity=2 --with-coverage --cover-erase \
		--cover-inclusive test --cover-package=pakrat

publish:
	@python setup.py sdist register upload
