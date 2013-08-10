all: unit

export PYTHONPATH:=${PWD}

unit:
	@echo "Running unit tests"
	@nosetests -s --with-coverage --cover-erase --verbosity=2 \
		--cover-inclusive test --cover-package=pakrat

publish:
	@python setup.py sdist register upload
