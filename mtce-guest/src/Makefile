#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

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
LDLIBS = -lstdc++ -ldaemon -lcommon -lfmcommon -ljson-c -levent -lrt -lcrypto -luuid 
INCLUDES = -I. -I/usr/include/mtce-common -I/usr/include/mtce-daemon

build: $(OBJS)
	$(CXX) $(CCPFLAGS) $(AGENT_OBJS)  $(LDLIBS) -L. -o guestAgent
	$(CXX) $(CCPFLAGS) $(SERVER_OBJS) $(LDLIBS) -L. -o guestServer

.cpp.o:
	$(CXX) $(INCLUDES) $(CCPFLAGS) $(EXTRACCFLAGS) -c $< -o $@

clean:
	@rm -v -f $(OBJ) guestAgent guestServer *.o *.a

