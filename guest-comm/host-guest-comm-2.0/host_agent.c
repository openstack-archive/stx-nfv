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

/*
This is a backchannel messaging agent that will run on the host in order to
pass messages between the host and the guest.

When a new instance appears (detected by a new unix socket of the specified
format being added to the watched directory) we open a unix stream socket
and connect to the instance, storing the mapping from instance to socket.

When an instance dies we will close the socket and remove the mapping.

We will monitor the connections to the instances as well as a unix datagram
socket used to communicate with other apps on the host.  Messages coming
from an instance will be forwarded to the appropriate app, and vice versa.

If we try to send a message to a guest socket that has nothing listening
within the guest, by default the message will get queued up without giving
us any indication that there is no listener.  These messages can get bundled
together when they get delivered to the guest.
*/


#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <linux/un.h>
#include <fcntl.h>
#include <string.h>
#include <stddef.h>
#include <sys/time.h>
#include <signal.h>
#include <unistd.h>
#include <poll.h>
#include <limits.h>
#include <syslog.h>
#include <execinfo.h>
#include <json-c/json.h>

#include "misc.h"
#include "host_guest_msg_type.h"
#include "host_instance_mgmt.h"

int app_fd;

// One tokener for each instance connection serve as reassembly buffer
struct json_tokener* tok[MAX_FDS_HOST];

#define SERVER_SOCKET_FORMAT \
    "/var/lib/libvirt/qemu/cgcs.messaging.%s.sock"

// Message has arrived from the guest.
// This assumes the message has been validated
void process_msg(json_object *jobj_msg, int fd)
{
    int rc;
    struct sockaddr_un cliaddr;
    char *name;
    int addrlen;

    name = instance_name_by_fd(fd);
    if (!name) {
        PRINT_ERR("whoops, can't get instance name from fd, dropping\n");
        return;
    }

    // parse version
    struct json_object *jobj_version;
    if (!json_object_object_get_ex(jobj_msg, VERSION, &jobj_version)) {
        PRINT_ERR("failed to parse version\n");
        return;
    }
    int version  = json_object_get_int(jobj_version);
    if (version != CUR_VERSION) {
        PRINT_ERR("received version %d, expected %d\n", version, CUR_VERSION);
        return;
    }

    // parse source addr
    struct json_object *jobj_source_addr;
    if (!json_object_object_get_ex(jobj_msg, SOURCE_ADDR, &jobj_source_addr)) {
        PRINT_ERR("failed to parse source_addr\n");
        return;
    }

    // parse dest addr
    struct json_object *jobj_dest_addr;
    if (!json_object_object_get_ex(jobj_msg, DEST_ADDR, &jobj_dest_addr)) {
        PRINT_ERR("failed to parse dest_addr\n");
        return;
    }
    const char *dest_addr = json_object_get_string(jobj_dest_addr);

    // parse data. data is a json object that is nested inside the msg
    struct json_object *jobj_data;
    if (!json_object_object_get_ex(jobj_msg, DATA, &jobj_data)) {
        PRINT_ERR("failed to parse data\n");
        return;
    }

    //create outgoing message
    struct json_object *jobj_outmsg = json_object_new_object();
    if (jobj_outmsg == NULL) {
        PRINT_ERR("failed to allocate json object for jobj_outmsg\n");
        return;
    }

    json_object_object_add(jobj_outmsg, DATA, jobj_data);
    json_object_object_add(jobj_outmsg, VERSION, json_object_new_int(CUR_VERSION));
    json_object_object_add(jobj_outmsg, SOURCE_ADDR, jobj_source_addr);
    json_object_object_add(jobj_outmsg, SOURCE_INSTANCE, json_object_new_string(name));

    const char *outmsg = json_object_to_json_string_ext(jobj_outmsg, JSON_C_TO_STRING_PLAIN);
    ssize_t outlen = strlen(outmsg);

    // Set up destination address
    memset(&cliaddr, 0, sizeof(struct sockaddr_un));
    cliaddr.sun_family = AF_UNIX;
    cliaddr.sun_path[0] = '\0';
    strncpy(cliaddr.sun_path+1, dest_addr, strlen(dest_addr));
    addrlen = sizeof(sa_family_t) + strlen(dest_addr) + 1;

    // Send the message to the client.
    // This will get transparently restarted if interrupted by signal.
    rc = sendto(app_fd, outmsg, outlen, 0, (struct sockaddr *) &cliaddr,
                addrlen);
    if (rc == -1) {
        PRINT_ERR("unable to send msg to client %.*s: %m\n", UNIX_ADDR_LEN,
                                                            cliaddr.sun_path+1);
    } else if (rc != outlen) {
        PRINT_ERR("sendto didn't send the whole message to client\n");
    }
    json_object_put(jobj_outmsg);
}

// Read and process all messages from the guest.  If the guest dies, tear
// down the connection.
void scan_guest_fd(struct pollfd *pfd)
{
    char buf[10000];
    ssize_t rc;

    if (pfd->revents & POLLHUP) {
        // The only known cause of this is the death of the qemu process.
        // Tear everything down.
        disconnect_guest(pfd->fd);
    } else if (pfd->revents & POLLIN) {
        // Read a message from the guest socket.
        // We assume that all the data arrives in one packet.
        // To handle arbitrary messages sizes we should receive into a buffer
        // with knowledge of message length, etc.  Can extend later if needed.
        rc = read(pfd->fd, buf, sizeof(buf));
        if (rc == 0) {
            PRINT_INFO("got read of 0 bytes on guest fd\n");
            return;
        } else if (rc < 0) {
            if (errno == EAGAIN)
                // Odd, should have been a message
                return;
            else {
                PRINT_ERR("read from guest: %m");
                return;
            }
        }
        handle_virtio_serial_msg(buf, rc, pfd->fd, tok[pfd->fd]);
    }
}


// validate header and send message to specified guest
void handle_app_msg(const char *msg, struct sockaddr_un *cliaddr,
                    socklen_t cliaddrlen)
{
    int rc;
    char *app_addr;
    int sock;

    //parse incoming msg
    struct json_object *jobj_msg = json_tokener_parse(msg);
    if (jobj_msg == NULL) {
        PRINT_ERR("failed to parse msg\n");
        return;
    }

    // parse version
    struct json_object *jobj_version;
    int version;
    if (!json_object_object_get_ex(jobj_msg, VERSION, &jobj_version)) {
        PRINT_ERR("failed to parse version\n");
        goto done;
    }
    version = json_object_get_int(jobj_version);

    if (version != CUR_VERSION) {
        PRINT_ERR("message from app version %d, expected %d, dropping\n",
                version, CUR_VERSION);
        goto done;
    }

    // parse dest addr
    struct json_object *jobj_dest_addr;
    if (!json_object_object_get_ex(jobj_msg, DEST_ADDR, &jobj_dest_addr)) {
        PRINT_ERR("failed to parse dest_address\n");
        goto done;
    }

    // parse dest instance
    struct json_object *jobj_dest_instance;
    if (!json_object_object_get_ex(jobj_msg, DEST_INSTANCE, &jobj_dest_instance)) {
        PRINT_ERR("failed to parse dest_instance\n");
        goto done;
    }
    const char *dest_instance = json_object_get_string(jobj_dest_instance);

    // parse data
    struct json_object *jobj_data;
    if (!json_object_object_get_ex(jobj_msg, DATA, &jobj_data)) {
        PRINT_ERR("failed to parse data\n");
        goto done;
    }

    if (cliaddr->sun_path[0] == '\0') {
        app_addr = cliaddr->sun_path+1;
        // get length without family or leading null from abstract namespace
        cliaddrlen = cliaddrlen - sizeof(sa_family_t) - 1;
        app_addr[cliaddrlen] = '\0';
    } else {
        PRINT_INFO("client address not in abstract namespace, dropping\n");
        goto done;
    }

    // look up the guest socket based on the instance name
    sock = fd_find_by_instance_name((char *)dest_instance);
    if (sock == -1) {
        PRINT_INFO("unable to find instance connection socket for %.20s\n",
                                                              dest_instance);
        goto done;
    }


    struct json_object *jobj_outmsg = json_object_new_object();
    if (jobj_outmsg == NULL) {
        PRINT_ERR("failed to allocate json object for outmsg\n");
        goto done;
    }

    json_object_object_add(jobj_outmsg, DATA, jobj_data);
    json_object_object_add(jobj_outmsg, VERSION, jobj_version);
    json_object_object_add(jobj_outmsg, DEST_ADDR, jobj_dest_addr);
    json_object_object_add(jobj_outmsg, SOURCE_ADDR, json_object_new_string(app_addr));

    const char *outmsg = json_object_to_json_string_ext(jobj_outmsg, JSON_C_TO_STRING_PLAIN);

    // send to guest
    ssize_t outlen = strlen(outmsg);
    rc = send(sock, outmsg, outlen, 0);
    if (rc == -1) {
        PRINT_ERR("unable to send msg from %.*s: %m\n", UNIX_ADDR_LEN, app_addr);
    } else if (rc != outlen) {
        PRINT_ERR("write didn't write the whole message\n");
    }

    // use '\n' to delimit JSON string
    rc = send(sock, "\n", 1, 0);
    if (rc == -1) {
        PRINT_ERR("unable to send \\n \n");
    }

    json_object_put(jobj_outmsg);

done:
    json_object_put(jobj_msg);
}

// Read and process a message from the application socket
void scan_app_fd()
{
    char buf[10000];
    struct sockaddr_un cliaddr;
    ssize_t rc;

    // Process a message from the app socket
    socklen_t addrlen = sizeof(struct sockaddr_un);
    rc = recvfrom(app_fd, buf, sizeof(buf), 0,
                (struct sockaddr *) &cliaddr, &addrlen);
    if (rc < 0) {
        if (errno == EAGAIN)
            // Odd, should have been a message
            return;
        else {
            PRINT_ERR("error in recvfrom from app: %m");
            return;
        }
    }
    handle_app_msg(buf, &cliaddr, addrlen);
}

//dump stack trace on segfault
static void segv_handler(int signum)
{
   int count;
   void *syms[100];
   int fd = open("/var/log/host_agent_backtrace.log", O_RDWR|O_APPEND|O_CREAT, S_IRWXU);
   if (fd == -1) {
       PRINT_ERR("Unable to open host agent backtrace file: %m");
       goto out;
   }

   write(fd, "\n", 1);
   count = backtrace(syms, 100);
   if (count == 0) {
       char *log = "Got zero items in backtrace.\n";
       write(fd, log, strlen(log));
       goto out;
   }
   
   backtrace_symbols_fd(syms, count, fd);
out:
   fflush(NULL);
   exit(-1);
}

void free_tok()
{
    int i;
    for (i=0; i<MAX_FDS_HOST; i++) {
        free(tok[i]);
    }
}

int main(int argc, char **argv)
{
    struct sockaddr_un svaddr;
    int rc;
    int flags;
    int addrlen;

    PRINT_INFO("%s starting up\n", *argv);

    // optional arg for log level.  Higher number means more logs
    if (argc > 1) {
        char *endptr, *str;
        long val;
        str = argv[1];
        errno = 0;
        val = strtol(str, &endptr, 0);

        if ((errno == ERANGE && (val == LONG_MAX || val == LONG_MIN))
                || (errno != 0 && val == 0)) {
            PRINT_ERR("error parsing log level arg: strtol: %m");
            exit(-1);
        }

        if (endptr == str) {
            PRINT_ERR("No digits were found\n");
            exit(EXIT_FAILURE);
        }

        if (val > LOG_DEBUG)
            val = LOG_DEBUG;

        setlogmask(LOG_UPTO(val));
    } else
        setlogmask(LOG_UPTO(LOG_WARNING));

    signal(SIGSEGV, segv_handler);

    // set up socket for talking to apps
    app_fd = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (app_fd == -1) {
        PRINT_ERR("problem with socket: %m");
        exit(-1);
    }

    flags = fcntl(app_fd, F_GETFL, 0);
    fcntl(app_fd, F_SETFL, flags | O_NONBLOCK);

    memset(&svaddr, 0, sizeof(struct sockaddr_un));
    svaddr.sun_family = AF_UNIX;
    svaddr.sun_path[0] = '\0';
    strncpy(svaddr.sun_path+1, AGENT_ADDR, sizeof(svaddr.sun_path) - 2);

    addrlen = sizeof(sa_family_t) + strlen(AGENT_ADDR) + 1;
    if (bind(app_fd, (struct sockaddr *) &svaddr, addrlen) == -1) {
        PRINT_ERR("problem with bind to agent addr: %m");
        exit(-1);
    }

    pollfd_add(app_fd, POLLIN);

    // This will set up monitoring for new/deleted instances
    // and will set up connections for existing instances.
    if (server_scan_init() < 0)
        return -1;

    int i;
    for (i=0; i<MAX_FDS_HOST; i++) {
        tok[i] = json_tokener_new();
    }

    while(1) {
        int i;

        // The timeout is for processing delayed connection retries.
        rc = poll(pollfds, nfds, next_connection_retry_interval());

        if (rc == -1) {
            if (errno == EINTR)
                continue;
            PRINT_ERR("problem with poll: %m");
            free_tok();
            exit(-1);
        }

        // With poll() we can't tell if we timed out without actually checking
        // the time, so run this unconditionally.
        process_connection_retries();

        for(i=0;i<nfds;i++) {
            if ((pollfds[i].fd == app_fd) && (pollfds[i].revents & POLLIN))
                scan_app_fd();
            else if ((pollfds[i].fd == inotify_fd) && (pollfds[i].revents & POLLIN))
                handle_inotify_event();
            else
                scan_guest_fd(pollfds+i);
        }
    }

    free_tok();
    return 0;
}
