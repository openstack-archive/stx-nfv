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
*/

#include <dirent.h>
#include <errno.h>
#include <execinfo.h>
#include <fcntl.h>
#include <limits.h>
#include <netdb.h>
#include <poll.h>
#include <pthread.h>
#include <resolv.h>
#include <sched.h>
#include <signal.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/inotify.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/un.h>
#include <sys/wait.h>
#include "misc.h"
#include "host_instance_mgmt.h"


/* When a new instance starts up it will create a named unix socket in a known
directory with a known filename format.

We will monitor the directory using inotify.  On detection of a new instance we
will add the instance to our list of instances, create a socket, and connect it
to the named socket.  On detection of a deleted instance we will tear it all
down.

We need to be able to map from socket to instance name and vice versa.
*/

// Main poll structure management stuff
struct pollfd pollfds[MAX_INSTANCES];
int nfds;

int inotify_fd;
static int inotify_watch_id;
static struct inotify_event *event_ptr;
static int event_size;

// Directory to watch for sockets
const char* host_virtio_dir = "/var/lib/libvirt/qemu";

// Mapping between instance name and fd for its connection
typedef struct {
    int fd;
    int pollfd_index;
    char name[INSTANCE_NAME_SIZE];
} instance_t;

static int max_instance=-1;
static instance_t instances[MAX_INSTANCES];


// Lookup table indexed by instance connection fd.
// Assumes fd re-use otherwise the table would need to be bigger.
static instance_t *instance_ptrs[MAX_FDS_HOST];


// Linked list nodes for queue of connections to be retried.
struct conn_retry {
    struct conn_retry *next;
    unsigned long long next_try;  // next retry time in nanoseconds
    int sock;
    int addrlen;
    struct sockaddr_un un;
    char instance_name[INSTANCE_NAME_SIZE];
    char file_name[];
};
typedef struct conn_retry conn_retry_t;

// Head/tail pointers for queue of connections to be retried.
static conn_retry_t *retry_list;
static conn_retry_t *retry_list_tail;


// Look up the instance given the fd
char *instance_name_by_fd(int fd)
{
    if (fd < MAX_FDS_HOST)
        return instance_ptrs[fd]->name;
    else
        return NULL;
}

// Look up the instance given the instance name
instance_t *instance_find_by_instance_name(char *name)
{
    int i;
    for (i=0;i<=max_instance;i++) {
        instance_t *instance = instances + i;

        // Skip the entry if it has been invalidated.
        if (instance->fd == -1)
            continue;
        if (strncmp(instance->name, name, INSTANCE_NAME_SIZE -1) == 0)
            return instance;
    }
    return NULL;
}

// Look up the connection socket given the instance name
int fd_find_by_instance_name(char *name)
{
    instance_t *instance = instance_find_by_instance_name(name);
    if (instance)
        return instance->fd;
    else
        return -1;
}


// Get the next available slot in the instance table.
instance_t *instance_get_entry()
{
    int i;

    // Use empty element in the existing array if possible.
    for (i=0;i<=max_instance;i++) {
        instance_t *instance = instances+i;
        if (instance->fd == -1)
            return instance;
    }
    // No empty elements, use a new one.
    if (max_instance <=  MAX_INSTANCES) {
        max_instance++;
        return instances+max_instance;
    }
    PRINT_ERR("unable to add fd, already at limit\n");
    return NULL;
}

// Return the instance to the instance table.
void instance_put_entry(instance_t *instance)
{
    int i;
    instance->fd = -1;
    i = (instance - instances)/sizeof(*instance);
    if (i == max_instance)
        max_instance--;
}


void init_pollfd(struct pollfd *pfd, int fd, short events)
{
    pfd->fd = fd;
    pfd->events = events;
    pfd->revents = 0;
}

// Add a new file descriptor to be monitored, return the index
// in the pollfds table.
int pollfd_add(int fd, short events)
{
    int i;
    // Use empty element in the existing array if possible.
    for (i=0;i<nfds;i++) {
        if (pollfds[i].fd == -1) {
            // Use this element
            printf("reusing pollfd index %d\n", i);
            init_pollfd(pollfds+i, fd, events);
            return i;
        }
    }
    // No empty elements, use a new one.
    if (nfds < MAX_INSTANCES) {
        int tmp = nfds;
        nfds++;
        PRINT_DEBUG("using new pollfd index %d\n", tmp);
        init_pollfd(pollfds+tmp, fd, events);
        return tmp;
    }
    PRINT_ERR("unable to add fd, already at limit\n");
    return -1;
}

// Delete the specified index in the pollfds table. */
void pollfd_del_idx(int idx)
{
    // Invalidate the pollfd table entry.
    pollfds[idx].fd = -1;

    // If we just invalidated the last entry in the array
    // then decrement nfds until we get to a valid entry.
    while(pollfds[nfds-1].fd == -1)
        nfds--;
}

// Set up all the data structures for a new instance.
int add_instance(int fd, short events, char *name)
{
    if (fd >= MAX_FDS_HOST) {
        PRINT_ERR("fd too large to store");
        return -1;
    }

    // Check if the instance is already in our list;
    instance_t *ptr = instance_find_by_instance_name(name);
    if (ptr) {
        PRINT_INFO("instance %.20s already in table", name);
        return 0;
    } else {
        instance_t *instance;
        int idx;
        if (max_instance == MAX_INSTANCES-1) {
            PRINT_ERR("hit max number of instances");
            return -1;
        }

        idx = pollfd_add(fd, events);
        if (idx == -1)
            return -1;

        PRINT_DEBUG("adding instance %.20s at pollfd index %d\n", name, idx);

        // Claim a new instance struct element.
        instance = instance_get_entry();
        instance->fd = fd;
        instance->pollfd_index = idx;
        if(snprintf(instance->name, sizeof(instance->name), "%s", name) < 0) {
            PRINT_ERR("snprintf error for instance_name %s", name);
            return -1;
        }

        // Index the new element for easy access later.
        instance_ptrs[fd] = instance;

        return 0;
    }
}

// The instance socket has disappeared, tear it all down.
void vio_full_disconnect(instance_t *instance)
{
    close(instance->fd);

    // Clear the lookup table entry.
    instance_ptrs[instance->fd] = NULL;

    // Clear the pollfd table entry.
    pollfd_del_idx(instance->pollfd_index);

    // Clear the instance table entry
    instance_put_entry(instance);
}


/*
 * Check a filename against the expected pattern for a cgcs messaging socket.
 * If satisfied, writes to the passed-in instance_name arg;
 *
 * Returns a pointer to the instance name on success, or NULL on failure.
 */
char *file_to_instance_name(char *filename, char* instance_name) {
    int rc;
    rc = sscanf(filename, "cgcs.messaging.%[^.].sock", instance_name);
    if (rc == 1)
        return instance_name;
    else
        return NULL;
}

// poll() has told us the socket has been disconnected
void disconnect_guest(int fd)
{
    instance_t *instance = instance_ptrs[fd];

    // Sanity check
    if (instance->fd != fd)
        return;

    PRINT_INFO("Detected disconnect of instance '%.20s'\n", instance->name);
    vio_full_disconnect(instance);
}



// Inotify has told us that a file has been deleted.
static void socket_deleted(char *fn)
{
    char buf[INSTANCE_NAME_SIZE];
    char* instance_name;
    instance_t * instance;

    if (!fn)
        return;

    instance_name = file_to_instance_name(fn, buf);
    if (!instance_name)
        // Not a file we care about.
        return;

    instance = instance_find_by_instance_name(instance_name);
    if (!instance) {
        PRINT_ERR("Couldn't find record for instance %.20s\n", instance_name);
        return;
    }

    PRINT_INFO("Detected deletion of vio file '%s'\n", fn);
    vio_full_disconnect(instance);
}

// Get time in nanoseconds
static unsigned long long gettime()
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (unsigned long long)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

// Time till next connection retry in milliseconds, for use as poll() timeout.
int next_connection_retry_interval()
{
    unsigned long long time_ns;
    if (!retry_list)
        return -1;                                        // infinite timeout

    time_ns = gettime();
    if (time_ns > retry_list->next_try)
        return 0;                                         // immediate timeout
    else
        return (retry_list->next_try - time_ns)/1000000;  // calculated timeout
}

// We always enqueue at the list tail
static void enqueue_retry(conn_retry_t *retry)
{
    if (retry_list_tail)
        retry_list_tail->next = retry;
    else
        retry_list = retry;
    retry_list_tail = retry;
    retry->next = NULL;
}

// We always dequeue from the list head
static conn_retry_t *dequeue_retry()
{
    conn_retry_t *tmp = retry_list;
    if (retry_list)
        retry_list = retry_list->next;
    if (!retry_list)
        retry_list_tail = NULL;
    return tmp;
}

// The initial connection attempt failed, add the socket to the connection
// retry list.
static void queue_connection_retry(int sock, char *filename,
                    char *instance_name, struct sockaddr_un *un, int addrlen)
{
    PRINT_DEBUG("attempting to queue '%s' for connection retry\n", filename);
    conn_retry_t *retry = malloc(sizeof(*retry) + strlen(filename) + 1);
    if (!retry) {
        PRINT_ERR("unable to allocate memory for connection retry\n");
        return;
    }

    retry->sock = sock;

    if(snprintf(retry->instance_name, sizeof(retry->instance_name), "%s", instance_name) < 0) {
        PRINT_ERR("snprintf error for instance_name %s", instance_name);i
        free(retry);
        return;
    }

    strcpy(retry->file_name, filename);

    retry->next_try = gettime() + 1000000000ULL;  // delay for one second
    memcpy(&retry->un, un, sizeof(retry->un));
    retry->addrlen = addrlen;

    enqueue_retry(retry);
}


// We've detected a new socket corresponding to a VM.  Try and open
// a connection to it.
static int socket_added(char *filename)
    {
    int rc;
    int addrlen;
    int sock;
    struct sockaddr_un un;
    char pathname[PATH_MAX];
    char *instance_name;
    char namebuf[INSTANCE_NAME_SIZE];
    instance_t * instance;
    int flags;

    if (!filename) {
        PRINT_ERR("socket_added called with null filename\n");
        return -1;
    }

    instance_name = file_to_instance_name(filename, namebuf);
    if (!instance_name) {
        // Not a bug, just not a file we care about.
        return -1;
    }

    instance = instance_find_by_instance_name(instance_name);
    if (instance) {
        PRINT_DEBUG("'%s' is already known\n", instance_name);
        return 0;
    }

    if(snprintf(pathname, sizeof(pathname), "%s/%s", host_virtio_dir, filename) < 0) {
        PRINT_ERR("encoding error when generate pathname %s.", filename);
        return -1;
    }

    sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock < 0) {
        PRINT_ERR("failed to get socket: %m\n");
        return -1;
    }

    flags = fcntl(sock, F_GETFL, 0);
    rc = fcntl(sock, F_SETFL, flags | O_NONBLOCK);
    if (rc < 0) {
        PRINT_ERR("fcntl failed: %s\n", strerror(errno));
        close(sock);
        return -1;
    }

    un.sun_family = AF_UNIX;
    snprintf(pathname, sizeof(pathname), "%s/%s", host_virtio_dir, filename);
    strcpy(un.sun_path, pathname);
    addrlen = offsetof(struct sockaddr_un, sun_path) + strlen(pathname);

    rc = connect(sock, (struct sockaddr *)&un, addrlen);
    if (rc < 0) {
        if (errno == ECONNREFUSED || errno == EAGAIN) {
           // temporary glitch, retry later
            queue_connection_retry(sock, filename, instance_name, &un, addrlen);
            return 0;
        } else {
            PRINT_ERR("connect to '%s' failed: %m\n", pathname);
            close(sock);
            return -1;
        }
    }

    PRINT_INFO("Connection accepted to '%s'\n", pathname);

    rc = add_instance(sock, POLLIN, instance_name);
    if (rc < 0) {
        close(sock);
        return -1;
    }

    PRINT_INFO("added instance at '%s'\n", filename);
    PRINT_INFO("registered instance sock %d\n", sock);
    return 0;
}

// process any outstanding connection retries
void process_connection_retries()
{
    int rc;
    conn_retry_t *retry;
    unsigned long long time;

    while (retry_list) {
        time = gettime();
        if (time < retry_list->next_try)
            return;

        retry = dequeue_retry();
        PRINT_DEBUG("dequeued '%s' for connect() retry\n", retry->file_name);
        rc = connect(retry->sock, (struct sockaddr *)&retry->un,
                                                        retry->addrlen);
        if (rc < 0) {
            if (errno == ECONNREFUSED || errno == EAGAIN) {
                // VM hasn't registered socket yet, retry later
                retry->next_try = time + 1000000000ULL;  //try again in a second
                PRINT_DEBUG("connection for '%s' refused, enqueuing for retry\n",
                                                             retry->file_name);
                enqueue_retry(retry);
                continue;
            } else {
                PRINT_ERR("connect() for '%s' failed: %m\n", retry->file_name);
                close(retry->sock);
                free(retry);
                continue;
            }
        }

        PRINT_INFO("Connection accepted to '%s'\n", retry->file_name);

        rc = add_instance(retry->sock, POLLIN, retry->instance_name);
        if (rc < 0) {
            close(retry->sock);
            free(retry);
            continue;
        }

        // Success path
        PRINT_INFO("registered instance sock %d\n", retry->sock);

        PRINT_DEBUG("freeing retry struct for '%s'\n", retry->un.sun_path);
        free(retry);
    }
}

void handle_inotify_event()
{
    int len;
    int bufsize = sizeof(struct inotify_event) + PATH_MAX + 1;
    char buf[bufsize];
    int offset = 0;

    len = read(inotify_fd, buf, bufsize);
    if (len < 0)
        return;

    // There can be multiple events returned in a single buffer, need
    // to process all of them.
    while (len-offset > sizeof(struct inotify_event)) {
        struct inotify_event *in_event_p = (struct inotify_event *)(buf+offset);

        if ((in_event_p->mask & IN_CREATE) == IN_CREATE) {
            PRINT_DEBUG("inotify creation event for '%s'\n", in_event_p->name);
            socket_added(in_event_p->name);
        } else if ((in_event_p->mask & IN_DELETE) == IN_DELETE) {
            PRINT_DEBUG("inotify deletion event for '%s'\n", in_event_p->name);
            socket_deleted(in_event_p->name);
        }

        // Now skip to the next inotify event if there is one
        offset += (sizeof(struct inotify_event) + in_event_p->len);
    }
}

static void server_scan()
{
    DIR *dirp;
    struct dirent entry;
    struct dirent *result;
    int rc;

    dirp = opendir(host_virtio_dir);
    if (!dirp) {
        PRINT_ERR("opendir %s failed: %m\n", host_virtio_dir);
        return;
    }

    while(0 == readdir_r(dirp, &entry, &result)) {
        if (!result)
            break;

        rc = socket_added(result->d_name);
        if (rc == 0) {
            PRINT_DEBUG("added '%s'\n", result->d_name);
        }
    }

    closedir(dirp);
}


int server_scan_init()
{
    event_size = sizeof(struct inotify_event) + PATH_MAX + 1;
    event_ptr = malloc(event_size);
    inotify_fd = inotify_init();
    if (inotify_fd < 0) {
        PRINT_ERR("inotify_init failed: %m\n");
        return -1;
    }

    inotify_watch_id = inotify_add_watch(inotify_fd, host_virtio_dir, IN_CREATE | IN_DELETE);
    if (inotify_watch_id < 0) {
        PRINT_ERR("vio_add_watch failed: %s\n", strerror(errno));
        close(inotify_fd);
        inotify_fd = -1;
        return -1;
    }

    pollfd_add(inotify_fd, POLLIN);
    PRINT_INFO("registered vio inotify sock %d\n", inotify_fd);

    // Do initial scan to pick up existing instance connections
    server_scan();

    return 0;
}
