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
 This file is used to test functions in file host_guest_msg.c.
 Functions under test are directly copied to here to simplify compile.
 Once tested and refactored, the functions can be copied back to their
 original location with appropriate debug traces.

 build: gcc -I. -o test_host_guest_msg test_host_guest_msg.c -ljson-c

 usage: binary can be executed directly on a linux desktop.
    ./test_host_guest_msg - run without parameters to check TCs PASS or FAIL
    ./test_host_guest_msg 1 - show error logs
    ./test_host_guest_msg 2 - show error and debug logs
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
#include <json-c/json.h>

//number of guest
#define NUM_GUEST 3

//number of reads
#define NUM_READS 3

int debug = 0;
#define PRINT_ERR(format, ...) if(debug >= 1) printf(format, ##__VA_ARGS__)
#define PRINT_DEBUG(format, ...) if(debug >= 2) printf(format, ##__VA_ARGS__)

// One tokener for each instance connection serve as reassembly buffer
struct json_tokener* tok[NUM_GUEST];
void process_msg(json_object *jobj_msg, int fd);

//----------------------------------------------------------
//   Functions Under Test
//----------------------------------------------------------
void parser(void *buf, ssize_t len, int fd, json_tokener* tok, int newline_found)
{
    PRINT_DEBUG("parser: len=%lu, buf=%s\n", len, (char *)buf);

    json_object *jobj = json_tokener_parse_ex(tok, buf, len);
    enum json_tokener_error jerr = json_tokener_get_error(tok);

    if (jerr == json_tokener_success) {
        process_msg(jobj, fd);
        json_object_put(jobj);
        return;
    }

    else if (jerr == json_tokener_continue) {
        // partial JSON is parsed , continue to read from socket
        PRINT_DEBUG("partial message parsed, continue read socket\n");
        PRINT_DEBUG("processed so far buf=%s\n", (char *)buf);

        // if newline was found in the middle of the buffer, the message should
        // be completed at this point. Throw out incomplete message by resetting
        // tokener.
        if (newline_found) {
            PRINT_DEBUG("newline_found. throw out the partial message\n");
            json_tokener_reset(tok);
        }
    }
    else
    {
        PRINT_ERR("JSON Parsing Error: %s\n", json_tokener_error_desc(jerr));
        json_tokener_reset(tok);
    }
}


//----------------------------------------------------------
//   Functions Under Test
//----------------------------------------------------------
void handle_virtio_serial_msg(void *buf, ssize_t len, int fd, json_tokener* tok)
{
    void *origbuf = buf;
    void *newline;

    ssize_t len_head;

next:
    if (len == 0)
        return;

    PRINT_DEBUG("analyzing buffer at offset %lu, len %zd\n", buf-origbuf, len);

    // search for newline as delimiter
    newline = memchr(buf, '\n', len);

    if (newline) {
        PRINT_DEBUG("found newline start at offset %lu\n", newline - origbuf);

        // split buffer to head and tail at the location of newline.
        // feed the head to the parser and recursively process the tail.
        len_head = newline-buf;

        // parse head
        if (len_head > 0)
            parser(buf, len_head, fd, tok, 1);

        // start of the tail: skip newline
        buf += len_head+1;
        // length of the tail: deduct 1 for the newline character
        len -= len_head+1;
        // continue to process the tail.
        goto next;
    }
    else {
         parser(buf, len, fd, tok, 0);
    }
}


// buffer to simulate socket to read, one socket per guest
void *socket[NUM_GUEST][NUM_READS];

// resulting parsed socket
char socket_processed[NUM_GUEST][NUM_READS][500];

// expected result
char *socket_expected[NUM_GUEST][NUM_READS];

// track current buffer being processed for particular guest
int current_processed[NUM_GUEST];

void free_tok()
{
    int fd;
    for (fd=0; fd<NUM_GUEST; fd++) {
        if (tok[fd])
            free(tok[fd]);
            tok[fd] = NULL;
    }
}


// populate socket with contents
void init_socket_result()
{
    socket_expected[0][0] = "{\"name\":\"guest0\",\"seq\":1,\"data\":{\"secret\":101}}";
    socket_expected[0][1] = "{\"name\":\"guest0\",\"seq\":2,\"data\":{\"secret\":102}}";
    socket_expected[0][2] = "{\"name\":\"guest0\",\"seq\":3,\"data\":{\"secret\":103}}";

    socket_expected[1][0] = "{\"name\":\"guest1\",\"seq\":1,\"data\":{\"secret\":201}}";
    socket_expected[1][1] = "{\"name\":\"guest1\",\"seq\":2,\"data\":{\"secret\":202}}";
    socket_expected[1][2] = "{\"name\":\"guest1\",\"seq\":3,\"data\":{\"secret\":203}}";

    socket_expected[2][0] = "{\"name\":\"guest2\",\"seq\":1,\"data\":{\"secret\":301}}";
    socket_expected[2][1] = "{\"name\":\"guest2\",\"seq\":2,\"data\":{\"secret\":302}}";
    socket_expected[2][2] = "{\"name\":\"guest2\",\"seq\":3,\"data\":{\"secret\":303}}";
}

void setup_test()
{
    int fd;
    for (fd=0; fd<NUM_GUEST; fd++) {
        tok[fd] = json_tokener_new();
        current_processed[fd] = 0;
    }
    init_socket_result();
}


void reset_results()
{
    int fd, read;
    for(fd=0;fd<NUM_GUEST;fd++) {
        for (read = 0; read <NUM_READS; read++) {
           strcpy(socket_processed[fd][read], "\0");
        }
        current_processed[fd] = 0;
    }
}


// populate socket with contents
void init_socket_tc1()
{
    reset_results();
    socket[0][0] = "\n{\"name\":\"guest0\",\"seq\":1,\"data\":{\"secret\":101}}\n";
    socket[0][1] = "\n{\"name\":\"guest0\",\"seq\":2,\"data\":{\"secret\":102}}\n";
    socket[0][2] = "\n{\"name\":\"guest0\",\"seq\":3,\"data\":{\"secret\":103}}\n";

    socket[1][0] = "\n{\"name\":\"guest1\",\"seq\":1,\"data\":{\"secret\":201}}\n";
    socket[1][1] = "\n{\"name\":\"guest1\",\"seq\":2,\"data\":{\"secret\":202}}\n";
    socket[1][2] = "\n{\"name\":\"guest1\",\"seq\":3,\"data\":{\"secret\":203}}\n";

    socket[2][0] = "\n{\"name\":\"guest2\",\"seq\":1,\"data\":{\"secret\":301}}\n";
    socket[2][1] = "\n{\"name\":\"guest2\",\"seq\":2,\"data\":{\"secret\":302}}\n";
    socket[2][2] = "\n{\"name\":\"guest2\",\"seq\":3,\"data\":{\"secret\":303}}\n";
}

void init_socket_tc2()
{
    reset_results();
    socket[0][0] = "\n{\"name\":\n{\"name\":\"guest0\",\"seq\":1,\"data\":{\"secret\":101}";
    socket[0][1] = "}\n\n{\"name\":\"guest0\",\"seq\":2,\"data\":{\"secret\":102}}\n";
    socket[0][2] = "\n{\"name\":\"guest0\",\"seq\":3,\"data\":{\"secret\":103}}\n";

    socket[1][0] = "\n";
    socket[1][1] = "{\"name\":\"guest1\",\"seq\":1,\"data\":{\"secret\":201}}";
    socket[1][2] = "\n\n{\"name\":\"guest1\",\"seq\":2,\"data\":{\"secret\":202}}\n\n{\"name\":\"guest1\",\"seq\":3,\"data\":{\"secret\":203}}\n";

    socket[2][0] = "\n{\"name\":\"guest2\",\"seq\":1,\"data\":{\"secret\":301}";
    socket[2][1] = "}\n\n{\"name\":\"guest2\",\"seq\":2,\"data\":{\"secret\":302";
    socket[2][2] = "}}\n\n{\"name\":\"guest2\",\"seq\":3,\"data\":{\"secret\":303}}\n";

}

// insert garbage characters
void init_socket_tc3()
{
    reset_results();
    socket[0][0] = "\n{\"name\":\"guest0\",\"s";
    socket[0][1] = "eq\":1,\"data\":{\"secret\":101}}\\nJHgB\7b4\\sx34xbb\n{\"name\":\"guest0\",\"seq\":2,\"data\":{\"secret\":102}}\n7b4x34";
    socket[0][2] = "\n{\"name\":\"guest0\",\"seq\":3,\"data\":{\"secret\":103}}\n";

    socket[1][0] = "\n{\"name\":\"guest1\",\"seq\":1,\"data\":{\"secret\":201}}\n7x4\xa}}{{\n{\"name\":";
    socket[1][1] = "\"guest1\",\"seq\":2,\"data\":{\"secret\"";
    socket[1][2] = ":202}}}}           \n\n{\"name\":\"guest1\",\"seq\":3,\"data\":{\"secret\":203}}\n";

    socket[2][0] = "\n{\"name\":\"guest2\",\"seq\":1,\"data\":{\"secret\":301}";
    socket[2][1] = "}\n\n*&*&*&\n{\"name\":\"guest2\",\"seq\":2,\"data\":{\"secret\":302";
    socket[2][2] = "}}\n\n{\"name\":\"guest2\",\"seq\":3,\"data\":{\"secret\":303}}%%$%#$%#$%\n";
}


void init_socket_tc4()
{
    reset_results();
    socket[0][0] = "\n{\"name\":\"guest0\",\"seq\":1,\"data\":{\"secret\":101}}\n\n{\"name\":\"guest0\",\"seq\":2,\"data\":{\"secret\":102}}\n*^*&%^*{{%$\n{\"name\":\"guest0\",\"seq\":3,\"data\":{\"secret\":103}}\n";
    socket[0][1] = "\n";
    socket[0][2] = "\n{\"name\":\n";

    socket[1][0] = "\n{\"name\":\"guest1\",\"seq\":1,\"data\":{\"secret\":201}}\n\n{\"name\":\"guest1\",\"seq\":2,\"data\":";
    socket[1][1] = "{\"secret\":202}}\n\n{\"name\":\"guest1\",\"seq\":";
    socket[1][2] = "3,\"data\":{\"secret\":203}}\n";

    socket[2][0] = "\n{\"name\":\"guest2\",\"seq\":1,\"data\"";
    socket[2][1] = ":{\"secret\":301}}\n\n{\"name\":\"guest2\",\"seq\":2,\"data\":{\"secret\":302}}\n\n{\"name\":\"guest2\",\"seq\":3,\"data\":{\"secret\"";
    socket[2][2] = ":303}}\n";
}


void check_results()
{
    int fd, read;
    for(fd=0;fd<NUM_GUEST;fd++) {
        for (read = 0; read <NUM_READS; read++) {
           if (strcmp(socket_processed[fd][read], socket_expected[fd][read])!= 0 ) {
               printf("FAIL\n guest %d read %d not correct:\n expect=%s\n actual=%s\n", fd, read, socket_expected[fd][read], socket_processed[fd][read]);
               return;
            }
        }
    }
    printf("PASS\n");
}


void process_msg(json_object *jobj_msg, int fd)
{
    const char *msg = json_object_to_json_string_ext(jobj_msg, JSON_C_TO_STRING_PLAIN);
    if (msg[0]!='{'){
        PRINT_DEBUG("*********throw out processed msg*********** %s\n", msg);
        return;
    }
    PRINT_DEBUG("successfully processed guest=%d, read=%d, msg=%s\n", fd, current_processed[fd], msg);
    strcpy (socket_processed[fd][current_processed[fd]], msg);
    current_processed[fd]++;
}

void scan_guest_fd(int fd, int read)
{
    char *buf;

    // read from socket for guest fd
    buf = socket[fd][read];
    PRINT_DEBUG("handling guest=%d, read=%d, buf=%s\n", fd, read, buf);
    handle_virtio_serial_msg(buf, strlen(buf), fd, tok[fd]);
}


int main(int argc, char **argv)
{
    int read;
    int fd;

    if (argc > 1)
      debug = atoi(argv[1]);

    setup_test();

    printf("\n===== TC1 one valid message per read: ");
    init_socket_tc1();
    for (read = 0; read <NUM_READS; read++) {
        for(fd=0;fd<NUM_GUEST;fd++) {
           scan_guest_fd(fd, read);
        }
    }
    check_results();

    printf("\n===== TC2 partial messages: ");
    init_socket_tc2();
    for (read = 0; read <NUM_READS; read++) {
        for(fd=0;fd<NUM_GUEST;fd++) {
           scan_guest_fd(fd, read);
        }
    }
    check_results();

    printf("\n===== TC3 garbage in between messages: ");
    init_socket_tc3();
    for (read = 0; read <NUM_READS; read++) {
        for(fd=0;fd<NUM_GUEST;fd++) {
           scan_guest_fd(fd, read);
        }
    }
    check_results();

    printf("\n===== TC4 multiple messages: ");
    init_socket_tc4();
    for (read = 0; read <NUM_READS; read++) {
        for(fd=0;fd<NUM_GUEST;fd++) {
           scan_guest_fd(fd, read);
        }
    }
    check_results();

    free_tok();
    return 0;
}
