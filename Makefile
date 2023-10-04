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
	@echo "make all-tests - perform all python tests"
	@echo "make unit-tests - run tests marked with @pytest.mark.unit_tests"
	@echo "make integration-tests - run tests marked with @pytest.mark.integration_tests"
	@echo "make wip-tests - run tests marked with @pytest.mark.wip"
	@echo "make coverage - track untested code in web browser"
	@echo "make bandit - look for secret strings in the code"
	@echo "make stats - count lines of code and more"
	@echo "make rebase - pull changes from origin main branch and rebase your code"
	@echo "make push - rebase from main branch and push current branch to remote repository"
	@echo "make diff - check foreseen changes in cloud resources before deployment"
	@echo "make deploy - build or update cloud resources for this workload"
	@echo "make destroy - delete cloud resources for this workload"
	@echo "make history - remember issues and related threads"
	@echo "make clean - delete transient files in this project"
	@echo " ... and you should have access to all cdk commands as well, e.g.: cdk ls"

# ensure that child processes get variables set in this Makefile
.EXPORT_ALL_VARIABLES:

# determine current AWS account
AWS_CURRENT_ACCOUNT ?= $(shell aws sts get-caller-identity --query "Account" --output text)

# by default, use this AWS region -- mostly useful for "make all-tests" in a pipeline
AWS_DEFAULT_REGION ?= eu-west-1

# determine which shell is used for commands launched by make
MAKESHELL ?= /bin/bash

# use this presentation file by default
PRESENTATION_NAME ?= PITCHME
# example: $ PRESENTATION_NAME=my_file make presentation

# by default, use this configuration file
SETTINGS ?= settings.yaml

# by default, limit verbosity to informational messages -- DEBUG, INFO, WARNING
# for example, you can run: VERBOSITY=DEBUG make diff
VERBOSITY ?= INFO

# locate python code for static analysis
CODE_PATH := cdk lambdas ./build_resources.py

setup: setup-python setup-cdk

setup-python:
	@echo "Installing python virtual environment..."
	python3 -m venv venv
	. venv/bin/activate && python -m pip install --upgrade pip -r requirements.txt

setup-cdk:
	@echo "Installing CDK and related NPM modules..."
	npm install -g aws-cdk
	cdk --version

bootstrap-cdk:
	@echo "Bootstrapping CDK..."
	mkdir -p lambdas.out
	cp -n fixtures/settings/settings.yaml ./settings.yaml || true
	. venv/bin/activate && cdk bootstrap ${AWS_CURRENT_ACCOUNT}/${AWS_DEFAULT_REGION}

setup-marp:
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

pre-commit: lint bandit

lint: lint-python

lint-python: venv/bin/activate
	venv/bin/python -m flake8 --max-complexity 8 --ignore E402,E501,F841,W503 --builtins="toggles" --per-file-ignores="cdk/serverless_stack.py:F401 tests/conftest.py:F401" ${CODE_PATH} tests

lint-json:
	venv/bin/python -m json.tool cdk.json >> /dev/null && exit 0 || echo "NOT valid JSON"; exit 1
	venv/bin/python -m json.tool package.json >> /dev/null && exit 0 || echo "NOT valid JSON"; exit 1

all-tests: venv/bin/activate
	venv/bin/python -m pytest -ra --durations=0 tests/

unit-tests: venv/bin/activate
	venv/bin/python -m pytest -m unit_tests -v tests/

integration-tests: venv/bin/activate
	venv/bin/python -m pytest -m integration_tests -v tests/

wip-tests: venv/bin/activate
	venv/bin/python -m pytest -m wip -v tests/

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
	rm -rf cdk.out/ htmlcov/
	venv/bin/python -m coverage run --omit "*/lambdas.out/*,*/node_modules/*,*/tests/*,*/venv/*" -m pytest
	venv/bin/python -m coverage report -m
	venv/bin/python -m coverage html
	$(BROWSER) htmlcov/index.html

bandit: venv/bin/activate
	venv/bin/python -m bandit -r ${CODE_PATH}

stats:
	pygount --format=summary ${CODE_PATH} features fixtures media tests workbooks *.ini cdk.json package.json *.md *.py *.txt Makefile

rebase:
	git pull --rebase origin main

push: rebase
	git push

lambdas.out: venv/bin/activate setup.py lambdas/*.py
	mkdir -p lambdas.out
	rm -rf lambdas.out || true
	venv/bin/python -m pip install --upgrade -e . -t lambdas.out --use-pep517
	cp lambdas/*.py lambdas.out
	touch lambdas.out

diff: venv/bin/activate lambdas.out
	cdk diff

deploy: venv/bin/activate lambdas.out
	cdk deploy --all

destroy: venv/bin/activate
	cdk destroy --all

put-events:
	aws events put-events --cli-input-json file://fixtures/events/cli-put-events.json

put-exceptions:
	aws events put-events --cli-input-json file://fixtures/events/cli-put-exceptions.json

put-to-microsoft-teams:
	aws events put-events --cli-input-json file://fixtures/events/cli-put-to-microsoft-teams.json

check-accounts:
	aws lambda invoke --function-name SpaCheckAccounts --log-type Tail --cli-read-timeout 0 check-accounts.log
	cat check-accounts.log
	rm check-accounts.log

.PHONY: history
history: venv/bin/activate
	mkdir -p history
	rm -f history/*.md
	gh2md --multiple-files --no-prs --idempotent reply-fr/sustainable-personal-accounts history

clean:
	rm -rf lambdas.out
	rm -rf ${PRESENTATION_NAME}.html
	rm -rf ${PRESENTATION_NAME}.pdf
	rm -rf ${PRESENTATION_NAME}.pptx
	rm -rf htmlcov/
	rm -rf cdk.out/asset.*

define PURGE_INCIDENT_RECORDS_PYSCRIPT
import boto3, sys
prefix = sys.argv[1].replace(':response-plan/', ':incident-record/')
im = boto3.client('ssm-incidents')
items = im.list_incident_records()
for item in items['incidentRecordSummaries']:
	arn = item['arn']
	if arn.startswith(prefix):
		print(f"deleting incident record ‘{arn}'")
		im.delete_incident_record(arn=arn)
	else:
		print(f"skipping incident record ‘{arn}'")
endef
export PURGE_INCIDENT_RECORDS_PYSCRIPT
PURGE_INCIDENT_RECORDS := venv/bin/python -c "$$PURGE_INCIDENT_RECORDS_PYSCRIPT"

clean-incident-records:
	@[ "$(RESPONSE_PLAN_ARN)" ] || (echo "[ERROR] RESPONSE_PLAN_ARN environment variable is not set" ; exit 1)
	@echo "Purging response plan '${RESPONSE_PLAN_ARN}'"
	@$(PURGE_INCIDENT_RECORDS) ${RESPONSE_PLAN_ARN}

compute-daily-cost-metric:
	@[ "$(METRIC_DAY)" ] || (echo "[ERROR] Missing METRIC_DAY, e.g., METRIC_DAY=2023-02-20 make compute-daily-cost-metric" ; exit 1)
	@echo "Computing cost metric for '${METRIC_DAY}'"
	aws lambda invoke --function-name SpaOnDailyCostsMetric \
                      --payload '{"date": "$(METRIC_DAY)" }' \
                      --invocation-type Event \
                      --cli-binary-format raw-in-base64-out \
                      output.log
	rm output.log

compute-monthly-cost-report:
	@[ "$(REPORT_MONTH)" ] || (echo "[ERROR] Missing REPORT_MONTH, e.g., REPORT_MONTH=2023-02 make compute-monthly-cost-report" ; exit 1)
	@echo "Computing cost report for '${REPORT_MONTH}'"
	aws lambda invoke --function-name SpaOnMonthlyCostReport \
                      --payload '{"date": "$(REPORT_MONTH)" }' \
                      --invocation-type Event \
                      --cli-binary-format raw-in-base64-out \
                      output.log
	rm output.log
