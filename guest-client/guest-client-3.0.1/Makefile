#
#   Copyright(c) 2013-2016, Wind River Systems, Inc.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     * Neither the name of Wind River Systems nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
SHELL = /bin/sh

VERSION := 3.0.1

## Configuration Directory Variables
prefix := /usr/local
exec_prefix := $(prefix)
sysconfdir := /etc
includedir := $(prefix)/include
libdir := $(exec_prefix)/lib
bindir := $(exec_prefix)/bin
unitdir := /usr/lib/systemd/system

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_DIR := $(patsubst %/,%,$(dir $(MAKEFILE_PATH)))
PARENT_DIR := $(patsubst %/,%,$(dir $(CURRENT_DIR)))
BUILD_DIR := $(CURRENT_DIR)/build
PACKAGE_DIR := $(BUILD_DIR)/package
PACKAGE_ROOT_DIR := $(PACKAGE_DIR)/rootdir
SDK_DEPLOY_DIR := /opt/deplot/cgcs_sdk

ARCHIVE_NAME := wrs-guest-client-3.0.1
ARCHIVE_PKG_NAME := wrs-guest-client-3.0.1_pkg

INIT_TYPE := sysv

.PHONY: all build sample clean distclean tar package install uninstall

all: build

build:
	mkdir -p --mode 755 $(BUILD_DIR)
	@(cd guest_client_api; make --no-print-directory build \
	sysconfdir=$(sysconfdir) BUILD_DIR=$(BUILD_DIR))
	@(cd guest_client; make --no-print-directory build \
	sysconfdir=$(sysconfdir) BUILD_DIR=$(BUILD_DIR))

tar:
	@(mkdir -p --mode 755 $(BUILD_DIR))
	@(ln -sf $(CURRENT_DIR) $(BUILD_DIR)/$(ARCHIVE_NAME))
	@(cd $(BUILD_DIR); tar -pczf $(ARCHIVE_NAME).tgz \
	$(ARCHIVE_NAME)/Makefile \
	$(ARCHIVE_NAME)/LICENSE \
	$(ARCHIVE_NAME)/README \
	$(ARCHIVE_NAME)/README.build \
	$(ARCHIVE_NAME)/README.usage \
	$(ARCHIVE_NAME)/TiS-Guest-Heartbeat-Service.pdf \
	$(ARCHIVE_NAME)/packaging \
	$(ARCHIVE_NAME)/include \
	$(ARCHIVE_NAME)/guest_client \
	$(ARCHIVE_NAME)/guest_client_api \
	--exclude $(ARCHIVE_NAME)/guest_client/build \
	--exclude $(ARCHIVE_NAME)/guest_client/src/test \
	--exclude $(ARCHIVE_NAME)/guest_client_api/build \
	--directory $(BUILD_DIR))

sample:
	mkdir -p --mode 755 $(BUILD_DIR)
	@(cd guest_client_api; make --no-print-directory sample \
	sysconfdir=$(sysconfdir) BUILD_DIR=$(BUILD_DIR))
	@(cd guest_client; make --no-print-directory sample \
	sysconfdir=$(sysconfdir) BUILD_DIR=$(BUILD_DIR))

clean:
	@-(cd guest_client_api; make --no-print-directory clean BUILD_DIR=$(BUILD_DIR))
	@-(cd guest_client; make --no-print-directory clean BUILD_DIR=$(BUILD_DIR))

distclean: clean

package:
	@(mkdir -p --mode 755 $(PACKAGE_DIR))
	@(mkdir -p --mode 755 $(PACKAGE_ROOT_DIR))
	@(ln -sf $(PACKAGE_DIR) $(BUILD_DIR)/$(ARCHIVE_PKG_NAME))
	@(echo "Packaging guest-client.pkg in $(PACKAGE_DIR)")
	@(cp $(CURRENT_DIR)/packaging/guest-client.pkg $(PACKAGE_DIR)/guest-client.pkg)
	@(chmod 755 $(PACKAGE_DIR)/guest-client.pkg)
	@-(cd guest_client_api; make --no-print-directory package BUILD_DIR=$(BUILD_DIR) \
	PACKAGE_DIR=$(PACKAGE_DIR) prefix=$(prefix) exec_prefix=$(exec_prefix) \
	sysconfdir=$(sysconfdir) includedir=$(includedir) libdir=$(libdir) \
	bindir=$(bindir))
	@-(cd guest_client; make --no-print-directory package BUILD_DIR=$(BUILD_DIR) \
	PACKAGE_DIR=$(PACKAGE_DIR) prefix=$(prefix) exec_prefix=$(exec_prefix) \
	sysconfdir=$(sysconfdir) includedir=$(includedir) libdir=$(libdir) \
	bindir=$(bindir))
	@(cd $(BUILD_DIR); tar -pczf $(ARCHIVE_PKG_NAME).tgz \
	$(ARCHIVE_PKG_NAME)/* --directory $(PACKAGE_DIR))

install:
	install -m 750 -d $(prefix)
	install -m 750 -d $(includedir)
	install -m 750 -d $(includedir)/guest-client
	install -m 640 -p -D guest_client/src/heartbeat/guest_heartbeat_msg_defs.h $(includedir)/guest-client/guest_heartbeat_msg_defs.h
	install -m 755 -d $(SDK_DEPLOY_DIR)
	install -m 640 build/wrs-guest-heartbeat-$(VERSION).tgz $(SDK_DEPLOY_DIR)
	install -m 644 -p -D guest_client/scripts/guest-client.service $(unitdir)/guest-client.service
	install -m 744 -p -D guest_client/scripts/guest-client.systemd $(sysconfdir)/guest-client/guest-client.systemd
	install -m 750 -d $(sysconfdir)/guest-client/heartbeat
	install -m 755 -p -D guest_client/scripts/guest_heartbeat.conf $(sysconfdir)/guest-client/heartbeat/guest_heartbeat.conf
	install -m 755 -p -D guest_client/scripts/sample_event_handling_script $(sysconfdir)/guest-client/heartbeat/sample_event_handling_script
	install -m 755 -p -D guest_client/scripts/sample_health_check_script $(sysconfdir)/guest-client/heartbeat/sample_health_check_script
	install -m 640 -p -D build/guest-client $(prefix)/local/bin/guest-client
	install -m 640 -p -D build/libguest_common_api.so.$(VERSION) $(prefix)/local/lib/libguest_common_api.so.$(VERSION)
	install -m 640 -p -D build/libguest_heartbeat_api.so.$(VERSION) $(prefix)/local/lib/libguest_heartbeat_api.so.$(VERSION)

uninstall: package
	@(echo "Uninstalling ...")
	@(cd $(PACKAGE_DIR); ./guest-client.pkg uninstall $(INIT_TYPE) $(DESTDIR))
