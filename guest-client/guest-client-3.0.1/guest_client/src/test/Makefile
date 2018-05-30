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

## Configuration Directory Variables
prefix := /usr/local
exec_prefix := $(prefix)
sysconfdir := $(prefix)/etc
includedir := $(prefix)/include
libdir := $(exec_prefix)/lib
bindir := $(exec_prefix)/bin

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_DIR := $(patsubst %/,%,$(dir $(MAKEFILE_PATH)))
BUILD_DIR := $(CURRENT_DIR)/build

.SUFFIXES:
.SUFFIXES: .c .o

.PHONY: all build create_build_dir clean distclean

program_NAME := guest-client-test
program_C_INCLUDES := -I$(CURRENT_DIR) -I$(CURRENT_DIR)/../
program_C_INCLUDES += -I$(CURRENT_DIR)/../heartbeat
program_C_INCLUDES += -I$(CURRENT_DIR)/../../include
program_C_SRCS := $(wildcard *.c)
program_C_OBJS := ${program_C_SRCS:.c=.o}
program_LDLIBS := -lrt

CFLAGS = -g -O2 -Wall -Werror -Wformat -DSYSCONFDIR=$(sysconfdir)

all: build

%.o: %.c
	$(CC) $(CFLAGS) $(program_C_INCLUDES) -c $^ -o $(BUILD_DIR)/$@ -ljson-c

$(program_NAME): $(program_C_OBJS)
	@(cd ../; make --no-print-directory build sysconfdir=$(sysconfdir) BUILD_DIR=$(BUILD_DIR))
	@-($(RM) $(BUILD_DIR)/guest_client.o $(BUILD_DIR)/guest-client)
	$(CC) $(CFLAGS) $(BUILD_DIR)/*.o $(program_LDLIBS) -o $(BUILD_DIR)/$(program_NAME) -ljson-c

create_build_dir:
	mkdir -p --mode 755 $(BUILD_DIR)

build: create_build_dir $(program_NAME)

clean:
	@-($(RM) $(BUILD_DIR)/*)

distclean: clean
