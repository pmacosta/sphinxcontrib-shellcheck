# Makefile
# Copyright (c) 2018-2020 Pablo Acosta-Serafini
# See LICENSE for details

PKG_NAME := sphinxcontrib
PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
REPO_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SOURCE_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/$(PKG_NAME)
EXTRA_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SBIN_DIR := $(EXTRA_DIR)/bin
### Custom pylint plugins configuration
NUM_CPUS := $(shell python3 -c "from __future__ import print_function; import multiprocessing; print(multiprocessing.cpu_count())")
PYLINT_PLUGINS_DIR := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then echo "$(EXTRA_DIR)/pylint_plugins"; fi)
PYLINT_PLUGINS_LIST := $(shell PYLINT_PLUGINS_DIR=$(PYLINT_PLUGINS_DIR) python3 -c "from __future__ import print_function;import glob; import os; sdir = os.environ.get('PYLINT_PLUGINS_DIR', ''); print(','.join([os.path.basename(fname).replace('.py', '') for fname in glob.glob(os.path.join(sdir, '*.py')) if not os.path.basename(fname).startswith('common')]) if sdir else '')" )
PYLINT_CMD := pylint \
	--rcfile=$(EXTRA_DIR)/.pylintrc \
	-j$(NUM_CPUS) \
	$(PYLINT_CLI_APPEND) \
	--output-format=colorized \
	--reports=no \
	--score=no
LINT_FILES := $(shell $(SBIN_DIR)/get-pylint-files.sh $(PKG_NAME) $(REPO_DIR) $(SOURCE_DIR) $(EXTRA_DIR))
###

asort:
	@echo "Sorting Aspell whitelist"
	@$(PKG_DIR)/bin/sort-whitelist.sh $(PKG_DIR)/data/whitelist.en.pws

bdist:
	@echo "Creating binary distribution"
	@$(PKG_DIR)/bin/make-pkg.sh

black:
	@echo "Running Black on package files"
	@black $(LINT_FILES)

clean: FORCE
	@echo "Cleaning package"
	@rm -rf $(PKG_DIR)/.tox
	@find $(PKG_DIR) -name '*.pyc' -delete
	@find $(PKG_DIR) -name '__pycache__' -delete
	@find $(PKG_DIR) -name '.coverage*' -delete
	@find $(PKG_DIR) -name '*.tmp' -delete
	@find $(PKG_DIR) -name '*.pkl' -delete
	@find $(PKG_DIR) -name '*.error' -delete
	@rm -rf $(PKG_DIR)/build
	@rm -rf	$(PKG_DIR)/dist
	@rm -rf $(PKG_DIR)/sphinxcontrib_shellcheck.egg-info
	@rm -rf $(PKG_DIR)/.eggs
	@rm -rf $(PKG_DIR)/.cache
	@rm -rf $(PKG_DIR)/tests/support1/_build
	@rm -rf $(PKG_DIR)/tests/support2/_build

distro: clean sdist wheel
	@rm -rf build sphinxcontrib-shellcheck.egg-info

default:
	@echo "No default action"

FORCE:

lint: pylint pydocstyle

pydocstyle:
	@echo "Running Pydocstyle on package files"
	@pydocstyle --config=$(EXTRA_DIR)/.pydocstyle $(LINT_FILES)

pylint:
	@echo "Running Pylint on package files"
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(LINT_FILES)

sdist:
	@echo "Creating source distribution"
	@cd $(PKG_DIR) && python3 setup.py sdist --formats=zip
	@$(PKG_DIR)/bin/list-authors.sh

sterile: clean
	@echo "Removing tox directory"
	@rm -rf $(PKG_DIR)/.tox

test: FORCE
	@$(PKG_DIR)/bin/rtest.sh $(ARGS)

upload: lint distro
	@twine upload $(PKG_DIR)/dist/*

wheel: lint
	@echo "Creating wheel distribution"
	@SHELLCHECK_TEST_ENV="" $(PKG_DIR)/bin/make-wheels.sh
	@rm -rf $(PKG_DIR)/build
	@rm -rf $(PKG_DIR)/sphinxcontrib_shellcheck.egg-info
	@rm -rf $(PKG_DIR)/.eggs
	@$(PKG_DIR)/bin/list-authors.sh
