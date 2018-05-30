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
	@echo -n "scripts/guest-agent.service" >> sdk/sdk.d
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

# Add the host clean as a dependency to the SDK stuff
clean: host_clean
host_clean:
	rm -rf sdk
