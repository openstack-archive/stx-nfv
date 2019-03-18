#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

DESTDIR ?= /
PREFIX ?= /usr/local
LOCALBINDIR ?= /usr/local/bin
SYSCONFDIR ?= /etc
UNITDIR ?= /var/lib/systemd/system

SRCS =	guestClass.cpp guestInstClass.cpp \
		guestSvrFsm.cpp guestSvrHdlr.cpp \
		guestServer.cpp guestAgent.cpp \
		guestHttpSvr.cpp guestHttpUtil.cpp guestVimApi.cpp \
		guestUtil.cpp  guestSvrUtil.cpp guestSvrMsg.cpp \
		guestVirtio.cpp guestStubs.cpp
AGENT_OBJS = \
		guestAgent.o  guestClass.o guestHttpSvr.o guestHttpUtil.o guestVimApi.o guestUtil.o guestStubs.o
SERVER_OBJS = \
		guestServer.o guestInstClass.o \
		guestSvrFsm.o guestSvrHdlr.o \
		guestSvrMsg.o guestVirtio.o \
		guestUtil.o guestSvrUtil.o

OBJS = $(SRCS:.cpp=.o)

CCPFLAGS = -g -O2 -Wall -Wextra -Werror
LDLIBS = $(EXTRALDFLAGS) -lstdc++ -ldaemon -lcommon -lfmcommon -ljson-c -levent -lrt -lcrypto -luuid
INCLUDES = -I. -I/usr/include/mtce-common -I/usr/include/mtce-daemon

build: $(OBJS)
	$(CXX) $(CCPFLAGS) $(AGENT_OBJS)  $(LDLIBS) -L. -o guestAgent
	$(CXX) $(CCPFLAGS) $(SERVER_OBJS) $(LDLIBS) -L. -o guestServer

.cpp.o:
	$(CXX) $(INCLUDES) $(CCPFLAGS) $(EXTRACCFLAGS) -c $< -o $@

install:
	install -m 755 -d $(SYSCONFDIR)
	install -m 755 -d $(PREFIX)
	install -m 755 -d $(LOCALBINDIR)
	install -m 755 -d $(SYSCONFDIR)/mtc
	install -m 755 -d $(SYSCONFDIR)/mtc/tmp

# resource agent stuff
	install -m 755 -d $(DESTDIR)/usr/lib
	install -m 755 -d $(DESTDIR)/usr/lib/ocf
	install -m 755 -d $(DESTDIR)/usr/lib/ocf/resource.d
	install -m 755 -d $(DESTDIR)/usr/lib/ocf/resource.d/platform
	install -m 755 -p -D scripts/guestAgent.ocf $(DESTDIR)/usr/lib/ocf/resource.d/platform/guestAgent

# config files
	install -m 644 -p -D scripts/guest.ini $(SYSCONFDIR)/mtc/guestAgent.ini
	install -m 644 -p -D scripts/guest.ini $(SYSCONFDIR)/mtc/guestServer.ini

# binaries
	install -m 755 -p -D guestServer $(LOCALBINDIR)/guestServer
	install -m 755 -p -D guestAgent $(LOCALBINDIR)/guestAgent

# init script files
	install -m 755 -p -D scripts/guestServer $(SYSCONFDIR)/init.d/guestServer
	install -m 755 -p -D scripts/guestAgent $(SYSCONFDIR)/init.d/guestAgent

# systemd service files
	install -m 644 -p -D scripts/guestServer.service $(UNITDIR)/guestServer.service
	install -m 644 -p -D scripts/guestAgent.service $(UNITDIR)/guestAgent.service

# process monitor config files
	install -m 755 -d $(SYSCONFDIR)/pmon.d
	install -m 644 -p -D scripts/guestServer.pmon $(SYSCONFDIR)/pmon.d/guestServer.conf

# log rotation
	install -m 755 -d $(SYSCONFDIR)/logrotate.d
	install -m 644 -p -D scripts/guestAgent.logrotate $(SYSCONFDIR)/logrotate.d/guestAgent.logrotate
	install -m 644 -p -D scripts/guestServer.logrotate $(SYSCONFDIR)/logrotate.d/guestServer.logrotate

# volatile directores
	install -m 755 -d $(DESTDIR)/var
	install -m 755 -d $(DESTDIR)/var/run

clean:
	@rm -v -f $(OBJ) guestAgent guestServer *.o *.a

