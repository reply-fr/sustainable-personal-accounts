# Copyright Reply.com or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

help:
	@echo "make setup - install code and dependencies"
	@echo "make presentation - present the overview deck interactively"
	@echo "make pdf - produce a PDF copy of the overview presentation"
	@echo "make pptx - produce an editable file of the overview presentation"
	@echo "make serve - run local web server on port 8082"
	@echo "make shell - load python local environment"
	@echo "make lint - analyze python code"
	@echo "make lint-json - check json syntax"
	@echo "make test-all - perform all python tests"
	@echo "make test - perform python tests not marked with @pytest.mark.slow"
	@echo "make test-wip - run tests marked with @pytest.mark.wip"
	@echo "make coverage - track untested code in web browser"
	@echo "make bandit - look for secret strings in the code"
	@echo "make stats - count lines of code and more"
	@echo "make rebase - rebase current code from origin main branch"
	@echo "make diff - check foreseen changes in cloud resources before deployment"
	@echo "make deploy - build or update cloud resources for this workload"
	@echo "make destroy - delete cloud resources for this workload"
	@echo "make clean - delete transient files in this project"
	@echo " ... and you should have access to all cdk commands as well, e.g.: cdk ls"

# ensure that child processes get variables set in this Makefile
.EXPORT_ALL_VARIABLES:

# by default, target this environment
ENVIRONMENT ?= Alpha

# determine which shell is used for commands launched by make
MAKESHELL ?= /bin/bash

# use this presentation file by default
PRESENTATION_NAME ?= PITCHME
# example: $ PRESENTATION_NAME=my_file make presentation

# by default, use this configuration file
SETTINGS ?= settings.yaml

# by default, prefix for stacks created in AWS CloudFormation
STACK_PREFIX ?= Spa

# by default, limit verbosity to informational messages -- DEBUG, INFO, WARNING
# for example, you can run: VERBOSITY=DEBUG make diff
VERBOSITY ?= INFO

# locate python code for static analysis
CODE_PATH := code resources ./build_resources.py

setup:
	@echo "Installing python virtual environment..."
	python3 -m venv venv
	. venv/bin/activate && python -m pip install --upgrade pip -r requirements.txt
	@echo "Installing CDK and other NPM modules..."
	npm install -g aws-cdk@latest --force
	cdk --version
	@echo "Installing MARP locally..."
	npm install -g @marp-team/marp-cli --force
	marp --version

presentation:
	@echo "Hit <Ctl-D> to exit the presentation"
	marp ${PRESENTATION_NAME}.md --preview

serve: ${PRESENTATION_NAME}.html
	@echo "Hit <Ctl-D> to stop the service"
	python3 -m http.server 8080

html: ${PRESENTATION_NAME}.html

${PRESENTATION_NAME}.html: ${PRESENTATION_NAME}.md
	marp ${PRESENTATION_NAME}.md

pdf: ${PRESENTATION_NAME}.pdf

${PRESENTATION_NAME}.pdf: ${PRESENTATION_NAME}.md
	marp ${PRESENTATION_NAME}.md --pdf --allow-local-files

pptx: ${PRESENTATION_NAME}.pptx

${PRESENTATION_NAME}.pptx: ${PRESENTATION_NAME}.md
	marp ${PRESENTATION_NAME}.md --pptx --allow-local-files

venv:
	python3 -m venv venv
	touch setup.py

venv/bin/activate: requirements.txt setup.py
	venv/bin/python -m pip install -r requirements.txt
	touch venv/bin/activate

shell:
	@echo "Use command 'exit' to kill this shell, or hit <Ctl-D>"
	. venv/bin/activate && ${MAKESHELL}

pre-commit: lint test bandit

lint: venv/bin/activate
	venv/bin/python -m flake8 --max-complexity 8 --ignore E402,E501,F841,W503 --builtins="toggles" ${CODE_PATH} tests

test: venv/bin/activate
	venv/bin/python -m pytest -ra --durations=0 -m "not slow" tests/

test-wip: venv/bin/activate
	venv/bin/python -m pytest -m wip -v tests/

test-all: venv/bin/activate
	venv/bin/python -m pytest -ra --durations=0 tests/

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := venv/bin/python -c "$$BROWSER_PYSCRIPT"

coverage: venv/bin/activate
	venv/bin/python -m coverage run --omit "*/venv/*,*/tests/*" -m pytest
	venv/bin/python -m coverage report -m
	venv/bin/python -m coverage html
	$(BROWSER) htmlcov/index.html

bandit: venv/bin/activate
	venv/bin/python -m bandit -r ${CODE_PATH}

lint-json:
	venv/bin/python -m json.tool cdk.json >> /dev/null && exit 0 || echo "NOT valid JSON"; exit 1
	venv/bin/python -m json.tool package.json >> /dev/null && exit 0 || echo "NOT valid JSON"; exit 1

stats: venv/bin/activate
	pygount --format=summary ${CODE_PATH} documents features media tests

rebase:
	git stash
	git pull --rebase origin main
	git stash pop

diff: venv/bin/activate
	@echo "Checking environment '${ENVIRONMENT}'..."
	cdk diff

deploy: venv/bin/activate
	@echo "Deploying environment '${ENVIRONMENT}'..."
	cdk deploy --all

destroy: venv/bin/activate
	@echo "Destroying environment '${ENVIRONMENT}'..."
	cdk destroy --all

put-events:
	aws events put-events --cli-input-json file://tests/events/cli-put-events.json

clean:
	rm -rf ${PRESENTATION_NAME}.html
	rm -rf ${PRESENTATION_NAME}.pdf
	rm -rf ${PRESENTATION_NAME}.pptx
