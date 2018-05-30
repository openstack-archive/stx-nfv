#
#   BSD LICENSE
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
# Note: if you change either Makefile or Makefile.sdk you need to manually
# do a "make clean" and then "make".

EXECS = guest_scale_helper guest_scale_agent

CFLAGS= -g -Wall
ODIR=obj
BINDIR=bin

BINEXECS=$(addprefix $(BINDIR)/, $(EXECS))

GUEST_SCALE_HELPER_SRCS = guest_scale_helper.c parser.c
GUEST_SCALE_HELPER_OBJ := $(patsubst %,$(ODIR)/%,$(GUEST_SCALE_HELPER_SRCS:.c=.o))

GUEST_SCALE_AGENT_SRCS= guest_scale_agent.c parser.c
GUEST_SCALE_AGENT_OBJ := $(patsubst %,$(ODIR)/%,$(GUEST_SCALE_AGENT_SRCS:.c=.o))

OBJS = $(GUEST_SCALE_OBJ) $(GUEST_SCALE_AGENT_OBJ)
DEPS = $(OBJS:.o=.d) sdk/sdk.d
-include $(DEPS)

EXPORT_SDK := wrs-guest-scale-$(MAJOR).$(MINOR).$(PATCH)

# SYSROOT = $(shell for i in $(LD) ; do echo $$i; done | grep sysroot= | awk -F = '{ print $$2 }'`)
SYSROOT = $(shell echo "$(LD)" | sed -n -e 's/^.*sysroot=//p' | awk '{ print $$1 }')
LIBSERVERGROUP_VER = $(shell find $(SYSROOT) | grep libservergroup.so. | sed -n -e 's/^.*libservergroup\.so\.//p')

print-%:
	@echo $* = $($*)

printvars:
	@$(foreach V,$(sort $(.VARIABLES)), $(if $(filter-out environment% default automatic, $(origin $V)),$(warning $V=$($V) ($(value $V)))))

.PHONY: printvars

all: host_all 
host_all: $(BINEXECS) sdk/$(EXPORT_SDK).tgz

# The dependency tracking for the SDK tarball is rather crude.  If any
# file changes they're all copied over again.  This is quick, so it's
# not worth getting fancy.
sdk/$(EXPORT_SDK).tgz: printvars
	@echo "Making SDK"
	@mkdir -p sdk/$(EXPORT_SDK)
	@mkdir -p sdk/$(EXPORT_SDK)/bin
	@mkdir -p sdk/$(EXPORT_SDK)/obj
	@mkdir -p sdk/$(EXPORT_SDK)/scripts
	@cp scripts/* sdk/$(EXPORT_SDK)/scripts
	@echo "MAJOR=$(MAJOR)" > sdk/$(EXPORT_SDK)/Makefile
	@echo "MINOR=$(MINOR)" >> sdk/$(EXPORT_SDK)/Makefile
	@echo "PATCH=$(PATCH)" >> sdk/$(EXPORT_SDK)/Makefile
	@cat Makefile.sdk >> sdk/$(EXPORT_SDK)/Makefile
	@cat docs/README.txt | sed 's/1\.0\.0/$(MAJOR).$(MINOR).$(PATCH)/' | sed 's/9.9.9/${LIBSERVERGROUP_VER}/' > sdk/$(EXPORT_SDK)/README.txt
	@cp docs/TiS-Guest-Resource-Scaling.pdf sdk/$(EXPORT_SDK)/TiS-Guest-Resource-Scaling.pdf
	@cp LICENSE sdk/$(EXPORT_SDK)/LICENSE
	@cp $(GUEST_SCALE_AGENT_SRCS) sdk/$(EXPORT_SDK)
	@cp misc.h sdk/$(EXPORT_SDK)
	@cd sdk && tar czf $(EXPORT_SDK).tgz $(EXPORT_SDK)
	@echo -n "sdk/$(EXPORT_SDK).tgz: Makefile.sdk docs/README.txt docs/TiS-Guest-Resource-Scaling.pdf " > sdk/sdk.d
	@echo -n "scripts/init_offline_cpus scripts/offline_cpus scripts/offline-cpus.service" >> sdk/sdk.d
	@echo -n "scripts/app_scale_helper " >> sdk/sdk.d
	@echo -n "$(GUEST_SCALE_AGENT_SRCS) " >> sdk/sdk.d
	@echo "misc.h " >> sdk/sdk.d
	@echo '*' > sdk/.gitignore


$(ODIR)/%.o: %.c
	$(CC) -c $(CFLAGS) $(CFLAGS2) -MMD -o $@ $<

$(BINDIR)/guest_scale_agent: $(GUEST_SCALE_AGENT_OBJ)
	$(CC) -o $@ $^ $(LDFLAGS) -lguesthostmsg  -ljson-c

$(BINDIR)/guest_scale_helper: $(GUEST_SCALE_HELPER_OBJ)
	$(CC) -o $@ $^ $(LDFLAGS) -lhostguestmsg  -ljson-c

# Add the host clean as a dependency to the SDK stuff
clean: host_clean
host_clean:
	rm -rf sdk
