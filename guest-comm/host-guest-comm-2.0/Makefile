#
#   Copyright(c) 2013-2016, Wind River Systems, Inc. All rights reserved.
#   All rights reserved.
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

# Note: if you change either Makefile or Makefile.sdk you need to manually
# do a "make clean" and then "make".

# Import the Makefile that we give to the customer so we eat our own dogfood
include Makefile.sdk

DESTDIR ?= /
SYSCONFDIR ?= /etc
UNITDIR ?= /usr/lib/systemd/system
LIBDIR ?= /usr/lib64
SDK_DEPLOY_DIR ?= /opt/deploy/cgcs_sdk
MAJOR ?= 2
MINOR ?= 0
VERSION ?= $(MAJOR).$(MINOR)
PATCH ?= 0

# This needs to be extended from what the customer will build.
EXECS += host_agent
BINEXECS=$(addprefix $(BINDIR)/, $(EXECS))

HOST_AGENT_SRCS = host_guest_msg.c host_agent.c host_instance_mgmt.c
HOST_AGENT_OBJ := $(patsubst %,$(ODIR)/%,$(HOST_AGENT_SRCS:.c=.o))

LIBHOSTGUESTMSG_SRCS := lib_host_guest_msg.c
LIBHOSTGUESTMSG_OBJ := $(patsubst %,$(ODIR)/%,$(LIBHOSTGUESTMSG_SRCS:.c=.o))
LIBHOSTGUESTMSG := hostguestmsg
LIBHOSTGUESTMSG_SO := $(patsubst %,lib%.so,$(LIBHOSTGUESTMSG))
LIBHOSTGUESTMSG_DEP := $(patsubst %,$(LIBDIR)/%,$(LIBHOSTGUESTMSG_SO))

LIBS= $(LIBHOSTGUESTMSG)
LIBDEPS:=$(patsubst %,$(LIBDIR)/lib%.so,$(LIBS))

EXPORT_SDK := wrs-server-group-$(MAJOR).$(MINOR).$(PATCH)

# Add the host build as a dependency to the SDK build
all: host_all
host_all: $(BINEXECS)  $(LIBDEPS) sdk/$(EXPORT_SDK).tgz

OBJS = $(HOST_AGENT_OBJ)
DEPS = $(OBJS:.o=.d) sdk/sdk.d
-include $(DEPS)

# The dependency tracking for the SDK tarball is rather crude.  If any
# file changes they're all copied over again.  This is quick, so it's
# not worth getting fancy.
sdk/$(EXPORT_SDK).tgz:
	@echo "Making SDK"
	@mkdir -p sdk/$(EXPORT_SDK)
	@mkdir -p sdk/$(EXPORT_SDK)/lib
	@mkdir -p sdk/$(EXPORT_SDK)/bin
	@mkdir -p sdk/$(EXPORT_SDK)/obj
	@mkdir -p sdk/$(EXPORT_SDK)/scripts
	@cp scripts/guest-agent.service sdk/$(EXPORT_SDK)/scripts
	@echo "MAJOR=$(MAJOR)" > sdk/$(EXPORT_SDK)/Makefile
	@echo "MINOR=$(MINOR)" >> sdk/$(EXPORT_SDK)/Makefile
	@echo "PATCH=$(PATCH)" >> sdk/$(EXPORT_SDK)/Makefile
	@cat Makefile.sdk >> sdk/$(EXPORT_SDK)/Makefile
	@cp LICENSE sdk/$(EXPORT_SDK)
	@cp docs/README.txt sdk/$(EXPORT_SDK)
	@cp docs/TiS-Guest-Server-Group-Messaging.pdf sdk/$(EXPORT_SDK)
	@cp $(GUEST_CLIENT_APP_SRCS) sdk/$(EXPORT_SDK)
	@cp $(LIBSERVERGROUP_SRCS) sdk/$(EXPORT_SDK)
	@cp $(LIBGUESTHOSTMSG_SRCS) sdk/$(EXPORT_SDK)
	@cp $(GUEST_AGENT_SRCS) sdk/$(EXPORT_SDK)
	@cp host_guest_msg_type.h server_group.h misc.h guest_host_msg.h sdk/$(EXPORT_SDK)

	@cd sdk && tar czf $(EXPORT_SDK).tgz $(EXPORT_SDK)
	@echo -n "sdk/$(EXPORT_SDK).tgz: Makefile.sdk docs/README.txt docs/TiS-Guest-Server-Group-Messaging.pdf " > sdk/sdk.d
	@echo -n "scripts/guest-agent.service " >> sdk/sdk.d
	@echo -n "$(GUEST_CLIENT_APP_SRCS) $(LIBSERVERGROUP_SRCS) $(GUEST_AGENT_SRCS) $(LIBGUESTHOSTMSG_SRCS)" >> sdk/sdk.d
	@echo " host_guest_msg.h server_group.h misc.h" >> sdk/sdk.d
	@echo '*' > sdk/.gitignore

$(LIBHOSTGUESTMSG_DEP): CFLAGS2 = -fPIC
$(LIBHOSTGUESTMSG_DEP): $(LIBHOSTGUESTMSG_OBJ)
	$(CC) -shared -Wl,-soname,$(LIBHOSTGUESTMSG_SO).$(MAJOR) $^ -o $(LIBHOSTGUESTMSG_DEP).$(MAJOR).$(MINOR).$(PATCH)
	ln -sf $(LIBHOSTGUESTMSG_SO).$(MAJOR).$(MINOR).$(PATCH) $(LIBHOSTGUESTMSG_DEP).$(MAJOR)
	ln -sf $(LIBHOSTGUESTMSG_SO).$(MAJOR) $(LIBHOSTGUESTMSG_DEP)

$(BINDIR)/host_agent: $(HOST_AGENT_OBJ)
	$(CC) -o $@ $^ $(LDFLAGS) -lrt -ljson-c

install:
	install -m 750 -d $(DESTDIR)/usr/sbin
	install -m 755 -d $(DESTDIR)/usr/lib64
	install -m 755 -d $(DESTDIR)/usr/include
	install -m 755 -d $(DESTDIR)/usr/include/cgcs
	install -m 750 -d $(SYSCONFDIR)/init.d
	install -m 750 -d $(SYSCONFDIR)/pmon.d
	install -m 750 -d $(UNITDIR)

	install -m 750 -d $(DESTDIR)/usr
	install -m 750 -d $(DESTDIR)/usr/src
	install -m 750 -d $(DESTDIR)/usr/src/debug
	install -m 750 -d $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)

	install -m 644 host_guest_msg_type.h $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/host_guest_msg_type.h
	install -m 644 server_group_app.c	$(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/server_group_app.c
	install -m 644 server_group.c $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/server_group.c
	install -m 644 guest_agent.c $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/guest_agent.c
	install -m 644 lib_host_guest_msg.c $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/lib_host_guest_msg.c
	install -m 644 host_guest_msg.c $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/host_guest_msg.c
	install -m 644 lib_guest_host_msg.c	$(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/lib_guest_host_msg.c
	install -m 644 host_instance_mgmt.h	$(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/host_instance_mgmt.h
	install -m 644 host_instance_mgmt.c	$(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/host_instance_mgmt.c
	install -m 644 guest_host_msg.h	$(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/guest_host_msg.h
	install -m 644 host_guest_msg.h	$(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/host_guest_msg.h
	install -m 644 host_agent.c $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/host_agent.c
	install -m 644 server_group.h $(DESTDIR)/usr/src/debug/host-guest-comm-$(VERSION)/server_group.h

	install -m 750 scripts/host_agent $(SYSCONFDIR)/init.d/host_agent
	install -m 644 scripts/host_agent.service $(UNITDIR)/host_agent.service
	install -m 644 scripts/guest-agent.service $(UNITDIR)/guest-agent.service
	install -m 640 scripts/host_agent.conf $(SYSCONFDIR)/pmon.d/host_agent.conf
	install -m 750 bin/host_agent $(DESTDIR)/usr/sbin/host_agent
	install -m 750 bin/guest_agent $(DESTDIR)/usr/sbin/guest_agent
	install -m 750 bin/server_group_app $(DESTDIR)/usr/sbin/server_group_app
	install -m 644 guest_host_msg.h	$(DESTDIR)/usr/include/cgcs/guest_host_msg.h
	install -m 644 host_guest_msg.h	$(DESTDIR)/usr/include/cgcs/host_guest_msg.h

# Deploy to the SDK deployment directory

	install -d $(SDK_DEPLOY_DIR)
	install -m 644 sdk/wrs-server-group-$(VERSION).$(PATCH).tgz  $(SDK_DEPLOY_DIR)/wrs-server-group-$(VERSION).$(PATCH).tgz

	install -m 755 -p -D lib/libguesthostmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libguesthostmsg.so.$(MAJOR).$(MINOR).$(PATCH)
	ln -s libguesthostmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libguesthostmsg.so.$(MAJOR).$(MINOR)
	ln -s libguesthostmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libguesthostmsg.so.$(MAJOR)
	ln -s libguesthostmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libguesthostmsg.so

	install -m 755 -p -D lib/libhostguestmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libhostguestmsg.so.$(MAJOR).$(MINOR).$(PATCH)
	ln -s libhostguestmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libhostguestmsg.so.$(MAJOR).$(MINOR)
	ln -s libhostguestmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libhostguestmsg.so.$(MAJOR)
	ln -s libhostguestmsg.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libhostguestmsg.so

	install -m 755 -p -D lib/libservergroup.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libservergroup.so.$(MAJOR).$(MINOR).$(PATCH)
	ln -s libservergroup.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libservergroup.so.$(MAJOR).$(MINOR)
	ln -s libservergroup.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libservergroup.so.$(MAJOR)
	ln -s libservergroup.so.$(MAJOR).$(MINOR).$(PATCH) $(LIBDIR)/libservergroup.so

# Add the host clean as a dependency to the SDK stuff
clean: host_clean
host_clean:
	rm -rf sdk
