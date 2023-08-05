.PHONY:	test upload clean bootstrap

test:
	nosetests tests

CHANGES.rst:
	git log --oneline --pretty=format:"* %ad: %s\n" --date=short > CHANGES.rst

test-all:
	tox

upload:	test-all
	python setup.py sdist upload
	make clean

register:
	python setup.py register

clean:
	rm -f CHANGES.rst
	rm -f MANIFEST
	rm -rf dist

bootstrap:	_virtualenv
	_venv/bin/pip install -r requirements.txt
	make clean

_virtualenv:
	virtualenv _venv
	_venv/bin/pip install --upgrade pip
	_venv/bin/pip install --upgrade setuptools

