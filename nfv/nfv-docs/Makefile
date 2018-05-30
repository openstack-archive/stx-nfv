#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
DOC_BUILDER = python ./doc_builder.py

BUILD_DIR   = ./build

.PHONY: html clean help

html:
	$(DOC_BUILDER) -b html $(BUILD_DIR)/html
	@echo
	@echo "Build finished.  Build output is in $(BUILD_DIR)/html."

package:
	tar -pczf vim_documentation.tar.gz $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)/*

help:
	@echo "Please use make <target> where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  package    to tar and gzip documentation"	
