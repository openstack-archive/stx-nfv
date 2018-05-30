/*
 * Copyright (c) 2013-2016, Wind River Systems, Inc.
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * 1) Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * 2) Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation and/or
 * other materials provided with the distribution.
 *
 * 3) Neither the name of Wind River Systems nor the names of its contributors may be
 * used to endorse or promote products derived from this software without specific
 * prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
 * USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 build: gcc -I../ -o guest_app guest_app.c -ljson-c
*/

#include <stddef.h>
#include <errno.h>
#include <error.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/select.h>
#include <sys/un.h>
#include <sys/socket.h>
#include <json-c/json.h>
#include "host_guest_msg_type.h"

struct json_object *create_new_jobj_data()
{
    struct json_object *jobj_data = json_object_new_object();
    if (jobj_data == NULL) {
        printf("failed to allocate json object for data\n");
        return NULL;
    }

    json_object_object_add(jobj_data, VERSION, json_object_new_int(CUR_VERSION));
    json_object_object_add(jobj_data, "resource", json_object_new_string("cpu"));
    json_object_object_add(jobj_data, "direction", json_object_new_string("down"));
    return jobj_data;
}

// create app to daemon msg
const char *create_outmsg(int msg_count)
{
    struct json_object *jobj_msg = json_object_new_object();
    if (jobj_msg == NULL) {
        printf("failed to allocate json object for msg\n");
        return NULL;
    }

    json_object_object_add(jobj_msg, VERSION, json_object_new_int(CUR_VERSION));
    json_object_object_add(jobj_msg, DEST_ADDR, json_object_new_string("h_scale_agent"));
    json_object_object_add(jobj_msg, "msg_count", json_object_new_int(msg_count));

    struct json_object *jobj_data = create_new_jobj_data();
    if (jobj_data == NULL) {
        json_object_put(jobj_msg);
        return NULL;
    }

    json_object_object_add(jobj_msg, DATA, create_new_jobj_data());
    const char *msg = json_object_to_json_string_ext(jobj_msg, JSON_C_TO_STRING_PLAIN);
    return msg;
}

// create daemon to app msg
const char *create_inmsg()
{
    struct json_object *jobj_msg = json_object_new_object();
    if (jobj_msg == NULL) {
        printf("failed to allocate json object for msg\n");
        return NULL;
    }

    json_object_object_add(jobj_msg, VERSION, json_object_new_int(CUR_VERSION));
    json_object_object_add(jobj_msg, SOURCE_ADDR, json_object_new_string("h_scale_agent"));

    struct json_object *jobj_data = create_new_jobj_data();
    if (jobj_data == NULL) {
        json_object_put(jobj_msg);
        return NULL;
    }

    json_object_object_add(jobj_msg, DATA, create_new_jobj_data());
    const char *msg = json_object_to_json_string_ext(jobj_msg, JSON_C_TO_STRING_PLAIN);
    return msg;
}

int main()
{
    char buf[4096];
    int len;
    struct sockaddr_un cliaddr, srvaddr;
    int rc;
    
    // set up socket for talking to host agent
    int fd = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (fd == -1) {
        perror("socket");
        exit(-1);
    }
    
    memset(&cliaddr, 0, sizeof(struct sockaddr_un));
    cliaddr.sun_family = AF_UNIX;
    cliaddr.sun_path[0] = '\0';
    strncpy(cliaddr.sun_path+1, "g_scale_agent", sizeof(cliaddr.sun_path) - 2);

    if (bind(fd, (struct sockaddr *) &cliaddr, sizeof(struct sockaddr_un)) == -1) {
        perror("bind");
        exit(-1);
    }

    /* Construct address of server */
    memset(&srvaddr, 0, sizeof(struct sockaddr_un));
    srvaddr.sun_family = AF_UNIX;
    srvaddr.sun_path[0] = '\0';
    strncpy(srvaddr.sun_path+1, AGENT_ADDR, sizeof(srvaddr.sun_path) - 2);
    
    const char* inmsg = create_inmsg();
    const char* outmsg = create_outmsg(1);
    len = strlen(outmsg);
    rc = sendto(fd, outmsg, len, 0, (struct sockaddr *) &srvaddr,
            sizeof(struct sockaddr_un));
    if (rc != len) {
            perror("sendto");
            exit(-1);
    }
    outmsg = create_outmsg(2);
    len = strlen(outmsg);
    rc = sendto(fd, outmsg, len, 0, (struct sockaddr *) &srvaddr,
            sizeof(struct sockaddr_un));
    if (rc != len) {
            perror("sendto");
            exit(-1);
    }
    
    while (1) {
        len = recv(fd, buf, sizeof(buf), 0);
        if (len == -1) {
            perror("recvfrom");
            exit(-1);
        }
        printf("Msg from host: %s\n", buf);
        fflush(0);
    }
}


