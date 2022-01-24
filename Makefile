# Copyright Reply.com or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
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
	@echo "make rebase - rebase current code from origin main branch"
	@echo "make clean - delete transient files in this project"

# ensure that child processes get variables set in this Makefile
.EXPORT_ALL_VARIABLES:

# ensure there is a shell
MAKESHELL ?= /bin/bash

setup:
	@echo "Installing MARP locally..."
	npm install --save-dev @marp-team/marp-cli

presentation:
	@echo "Hit <Ctl-D> to exit the presentation"
	marp PITCHME.md --preview

pdf:
	marp PITCHME.md --pdf --allow-local-files

pptx:
	marp PITCHME.md --pptx --allow-local-files

rebase:
	git stash
	git pull --rebase origin main
	git stash pop

clean:
	rm -rf PITCHME.html
	rm -rf PITCHME.pdf
	rm -rf PITCHME.pptx
