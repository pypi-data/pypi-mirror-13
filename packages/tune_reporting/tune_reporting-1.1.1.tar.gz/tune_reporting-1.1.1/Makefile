#   Makefile
#
#   Copyright (c) 2014 Tune, Inc
#   All rights reserved.
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#
# category  Tune
# package   tune.tests
# author    Jeff Tanner <jefft@tune.com>
# copyright 2014 Tune (http://www.tune.com)
# license   http://opensource.org/licenses/MIT The MIT License (MIT)
# update    $Date: 2015-12-11 20:56:46 $
# version   $Version: 1.0.6 $
# link      https://developers.mobileapptracking.com
#

.PHONY: clean venv install analysis examples27 examples3 tests tests-travis-ci tests-install build27 build3 dist dist27 dist3 register27 register3 docs-sphinx docs-doxygen

venv:
	sudo pip install virtualenv
	virtualenv venv

install: venv
	. venv/bin/activate; pip install --upgrade -r requirements.txt

tests-install: install
	. venv/bin/activate; pip install --upgrade -r tests/requirements.txt

clean:
	sudo rm -fR ./build/*
	sudo rm -fR ./docs/doxygen/*
	sudo rm -fR ./docs/sphinx/_build
	sudo rm -fR build/*
	sudo rm -fR dist/*
	sudo rm -fR ./tune_reporting.egg-info/*
	find . -name "*.pyc" -type f -delete
	rm -rf venv

dist-install27:
	sudo pip2.7 install -r requirements.txt

dist-install3:
	sudo pip3.4 install -r requirements.txt

dist27:
	sudo rm -fR ./dist/*
	sudo python2.7 setup.py sdist --format=zip,gztar upload
	sudo python2.7 setup.py bdist_egg upload
	sudo python2.7 setup.py bdist_wheel upload

dist3:
	sudo rm -fR ./dist/*
	sudo python3.4 setup.py sdist --format=zip,gztar bdist_egg bdist_wheel upload
	sudo python3.4 setup.py bdist_egg upload
	sudo python3.4 setup.py bdist_wheel upload

dist:
	sudo rm -fR ./dist/*
	sudo python3.4 setup.py sdist --format=zip,gztar upload
	sudo python2.7 setup.py bdist_egg upload
	sudo python2.7 setup.py bdist_wheel upload
	sudo python3.4 setup.py bdist_egg upload
	sudo python3.4 setup.py bdist_wheel upload

build27:
	sudo pip2.7 install --upgrade -r requirements27.txt
	sudo python2.7 setup.py clean
	sudo python2.7 setup.py build
	sudo python2.7 setup.py install

build3:
	sudo pip3.4 install --upgrade -r requirements3.txt
	sudo python3.4 setup.py clean
	sudo python3.4 setup.py build
	sudo python3.4 setup.py install

register27:
	sudo python2.7 setup.py register

register3:
	sudo python3.4 setup.py register

tests: build
	python ./tests/tune_reporting_tests.py $(api_key)

tests3: build3
	python3.4 ./tests/tune_reporting_tests.py $(api_key)

tests-travis-ci:
	flake8 --ignore=F401,E265,E129 tune
	flake8 --ignore=E123,E126,E128,E265,E501 tests
	python ./tests/tune_reporting_tests.py $(api_key)

tests-travis-ci3:
	flake8 --ignore=F401,E265,E129 tune
	flake8 --ignore=E123,E126,E128,E265,E501 tests
	python3.4 ./tests/tune_reporting_tests.py $(api_key)

examples27: build27
	python2.7 ./examples/tune_reporting_examples.py $(api_key)

examples3: build3
	python3.4 ./examples/tune_reporting_examples.py $(api_key)

analysis: install
	. venv/bin/activate; flake8 --ignore=E123,E126,E128,E265,E501 examples
	. venv/bin/activate; flake8 --ignore=E123,E126,E128,E265,E501 tests
	. venv/bin/activate; flake8 --ignore=F401,E265,E129 tune_reporting
	. venv/bin/activate; pylint --rcfile ./tools/pylintrc tune_reporting | more

lint: clean
	pylint --rcfile ./tools/pylintrc tune_reporting | more

docs-sphinx-gen:
	sudo rm -fR ./docs/sphinx/tune_reporting/*
	sphinx-apidoc -o ./docs/sphinx/tune_reporting/ ./tune_reporting

docs-install: venv
	. venv/bin/activate; pip install -r docs/sphinx/requirements.txt

docs-sphinx: docs-install
	sudo rm -fR ./docs/sphinx/_build
	cd docs/sphinx && make html
	x-www-browser docs/sphinx/_build/html/index.html

docs-doxygen:
	sudo rm -fR ./docs/doxygen/*
	sudo doxygen docs/Doxyfile
	x-www-browser docs/doxygen/html/index.html
