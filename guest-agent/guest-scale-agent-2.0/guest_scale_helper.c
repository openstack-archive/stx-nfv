/**
* Copyright (c) <2013-2016>, Wind River Systems, Inc.
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
*  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
* ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
* LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
* USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/



/* This is intended to run as a helper function, called by nova, to pass data up
 * into the guest and receive data back from the guest and return it to nova.
 */


#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <sys/time.h>
#include <signal.h>
#include <unistd.h>
#include <cgcs/host_guest_msg.h>
#include <json-c/json.h>

#include "misc.h"

hg_info_t *info;

#define SPARE_ALLOC 128

#define INSTANCE_NAME_SIZE 32
#define NACK_LOG_SIZE 500

#define UNIX_ADDR_LEN 16
#define DEFAULT_TIMEOUT_MS 1000
#define TIMEOUT_OVERHEAD_MS 500
#define MIN_SCRIPT_TIMEOUT_MS 500
int timeout_ms = DEFAULT_TIMEOUT_MS;

int *request_online_cpus;
int len_request_online_cpus;
int request_cpu;

void usage() {
    printf("guest_scale_helper --instance_name <name>\n");
    printf("                    --cpu_del | --cpu_add <index> <cur_mask>\n");
    printf("                    [--timeout <millisec, at least 1000>]\n");
    printf("\n");
    exit(-1);
}

void handle_cpu_scale_up(json_object *jobj_response, const char *source_instance)
{
    int rc = -1;
    char log_msg[NACK_LOG_SIZE];

    struct json_object *jobj_result;
    if (!json_object_object_get_ex(jobj_response, RESULT, &jobj_result)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse result");
        goto failed;
    }
    const char *result = json_object_get_string(jobj_result);

    if (!strcmp(result, "fail")) {
        struct json_object *jobj_err_msg;
        const char *err_msg;

        if (!json_object_object_get_ex(jobj_response, ERR_MSG, &jobj_err_msg))
            err_msg="";
        else
            err_msg = json_object_get_string(jobj_err_msg);
        ERR_LOG("Error: guest helper scaling cpu up failed: %s\n", err_msg);
        goto out;
    }

    struct json_object *jobj_online_cpu;
    if (!json_object_object_get_ex(jobj_response, ONLINE_CPU, &jobj_online_cpu)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse online_cpu");
        goto failed;
    }
    int online_cpu = json_object_get_int(jobj_online_cpu);

    struct json_object *jobj_online_cpus;

    json_object_object_get_ex(jobj_response, ONLINE_CPUS, &jobj_online_cpus);
    if (!json_object_is_type(jobj_online_cpus, json_type_array)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse online_cpus");
        goto failed;
    }

    int i, len_response;
    len_response = json_object_array_length(jobj_online_cpus);
    int *response_online_cpus = malloc(len_response*sizeof(int));

    for (i=0; i< len_response; i++){
        response_online_cpus[i] = json_object_get_int(json_object_array_get_idx(jobj_online_cpus, i));
    }

    // compare request and response, assuming cpus are in the same order
    if ( (len_response - len_request_online_cpus ) <=1 ) {
        int req =0;
        int rsp = 0;
        int found_req = 0;
        while (req < len_request_online_cpus){

            if (response_online_cpus[rsp] == request_online_cpus[req]) {
                req++; rsp++;
            } else if (response_online_cpus[rsp] == request_cpu) {
                rsp++;
                found_req = 1;
                // protect against infinite loop
                if (rsp == len_response)
                    break;
            } else {
                ERR_LOG("Error: cpu %d online by guest but not online in nova\n", response_online_cpus[rsp]);
                break;
            }
        }

        if ((!found_req) && (req == len_request_online_cpus)) {
            if ((len_response == len_request_online_cpus) ||
                (response_online_cpus[len_response] != request_cpu)) {
                ERR_LOG("Error: cpu %d online by nova but not online in guest\n", response_online_cpus[req]);
            }
        }
    }
    else {
        ERR_LOG("Error: guest's online cpu range doesn't match nova\n");
        char buf[1024];
        print_array(buf, response_online_cpus, len_response);
        ERR_LOG("guest online cpu range: %s\n", buf);
    }

    // Yay, everything looks good.
    free(response_online_cpus);
    free(request_online_cpus);
    exit(online_cpu);
    rc = online_cpu;
failed:
    send_nack(log_msg, source_instance);
out:
    free(request_online_cpus);
    exit(rc);
}


void handle_cpu_scale_down(json_object *jobj_response, const char *source_instance)
{
    int rc = -1;
    struct json_object *jobj_result;
    char log_msg[NACK_LOG_SIZE];

    if (!json_object_object_get_ex(jobj_response, RESULT, &jobj_result)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse result");
        goto failed;
    }
    const char *result = json_object_get_string(jobj_result);

    if (!strcmp(result, "fail")) {
        struct json_object *jobj_err_msg;
        const char *err_msg;
        if (!json_object_object_get_ex(jobj_response, ERR_MSG, &jobj_err_msg))
            err_msg="";
        else
            err_msg = json_object_get_string(jobj_err_msg);
        ERR_LOG("problem, guest helper scaling cpu down failed: %s\n", err_msg);
        goto out;
    }

    struct json_object *jobj_offline_cpu;
    if (!json_object_object_get_ex(jobj_response, OFFLINE_CPU, &jobj_offline_cpu)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse offline_cpu");
        goto failed;
    }
    int offline_cpu = json_object_get_int(jobj_offline_cpu);

    struct json_object *jobj_online_cpus;
    json_object_object_get_ex(jobj_response, ONLINE_CPUS, &jobj_online_cpus);
    if (!json_object_is_type(jobj_online_cpus, json_type_array)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse online_cpus");
        goto failed;
    }

    int i, len_response;
    len_response = json_object_array_length(jobj_online_cpus);
    int *response_online_cpus = malloc(len_response*sizeof(int));

    for (i=0; i< len_response; i++){
        response_online_cpus[i] = json_object_get_int(json_object_array_get_idx(jobj_online_cpus, i));
    }

    if (response_online_cpus[len_response] > offline_cpu) {
        ERR_LOG("Error: cpu %d is still online in guest\n", offline_cpu);
    }

    // Yay, everything looks good.
    free(response_online_cpus);
    free(request_online_cpus);
    rc = offline_cpu;
    exit(rc);
failed:
    send_nack(log_msg, source_instance);
out:
    free(request_online_cpus);
    exit(rc);
}

// This should call exit(0) on success or exit(-1) on permanent failure().
// Returning will continue listening.
// Theoretically this could come from any instance, need to fix that.
void msg_handler(const char *source_addr, const char *source_instance, struct json_object *jobj_response)
{
    // parse version
    struct json_object *jobj_version;
    char log_msg[NACK_LOG_SIZE];

    if (!json_object_object_get_ex(jobj_response, VERSION, &jobj_version)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse version");
        goto failed;
    }
    int version = json_object_get_int(jobj_version);

    if (version != CUR_VERSION) {
        snprintf(log_msg, NACK_LOG_SIZE, "invalid version %d, expecting %d", version, CUR_VERSION);
        goto failed;
    }

    struct json_object *jobj_resource;
    if (!json_object_object_get_ex(jobj_response, RESOURCE, &jobj_resource)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse resource");
        goto failed;
    }
    const char *resource = json_object_get_string(jobj_resource);

    struct json_object *jobj_direction;
    if (!json_object_object_get_ex(jobj_response, DIRECTION, &jobj_direction)) {
        snprintf(log_msg, NACK_LOG_SIZE, "failed to parse direction");
        goto failed;
    }
    const char *direction = json_object_get_string(jobj_direction);

    if (!strcmp(resource,"cpu")) {
        if (!strcmp(direction,"up")) {
            handle_cpu_scale_up(jobj_response, source_instance);
        } else if (!strcmp(direction,"down")) {
            handle_cpu_scale_down(jobj_response, source_instance);
        }
    }

    // if handle_cpu_scale_up/down is called, program should exit,
    // so this is only called when scale up/down are not properly handled.
    sprintf(log_msg, "unknown message, resource %s, direction %s",
            resource, direction);

failed:
    send_nack(log_msg, source_instance);
}

// instance_name will be of the form instance-xxxxxxxx
// We want to make a name of the form scale-xxxxxxxx
void instance_to_addr(const char *instance_name, char *addr)
{
    const char *match = "instance-";
    const char *replace = "scale-";
    char *tmp = strstr(instance_name, match);
    if (!tmp) {
        ERR_LOG("Instance name %s doesn't match expected pattern\n",
                instance_name);
        exit(-1);
    }
    strcpy(addr, replace);
    strncpy(addr+strlen(replace), instance_name+strlen(match),
        UNIX_ADDR_LEN-strlen(replace)-1);
    addr[UNIX_ADDR_LEN-1]='\0';
}

void handle_message(const char *request, const char *instance_name)
{
    int rc;
    fd_set rfds, rfds_tmp;
    int fd;
    char addr[UNIX_ADDR_LEN];

    INFO_LOG("handling scaling request: %s", request);

    // Create a unique address from the instance name.  When using a helper app
    // this is needed in order to handle simultaneous scale events for different
    // servers on the same hypervisor.
    instance_to_addr(instance_name, addr);

    fd = hg_init(msg_handler, addr, &info);
    if (fd == -1) {
        if (!info)
            ERR_LOG("Unable to allocate memory for info: %m");
        else
            ERR_LOG("Unable to initialize guest/host messaging: %s\n",
                                                    hg_get_error(info));
        exit(-1);
    }

    rc = hg_send_msg(info, SCALE_AGENT_ADDR, instance_name, request);
    if (rc < 0) {
        ERR_LOG("hg_send_msg failed: %s\n", hg_get_error(info));
        exit(-1);
    }

    FD_ZERO(&rfds);
    FD_SET(fd, &rfds);
 
    while(1) {
        rfds_tmp = rfds;
        rc = select(fd+1, &rfds_tmp, NULL, NULL, NULL);
        if (rc > 0) {
            if (hg_process_msg(info) < 0) {
                ERR_LOG("problem processing messages: %s\n",
                                                    hg_get_error(info));
            }
        } else if (rc < 0) {
            ERR_LOG("select(): %m");
        }
    }
}

void send_nack(char *log_msg, const char *instance_name)
{
    ERR_LOG("sending Nack with error: %s\n", log_msg);
    struct json_object *jobj_msg = json_object_new_object();
    if (jobj_msg == NULL) {
        ERR_LOG("failed to allocate json object for nack msg\n");
        return;
    }

    json_object_object_add(jobj_msg, VERSION, json_object_new_int(CUR_VERSION));
    json_object_object_add(jobj_msg, MSG_TYPE, json_object_new_string(MSG_TYPE_NACK));
    json_object_object_add(jobj_msg, LOG_MSG, json_object_new_string(log_msg));

    const char *msg = json_object_to_json_string_ext(jobj_msg, JSON_C_TO_STRING_PLAIN);
    hg_send_msg(info, SCALE_AGENT_ADDR, instance_name, msg);

    json_object_put(jobj_msg);
}

void handle_timeout(int sig)
{
    _exit(-2);
}

void setup_timeout(int timeout_ms)
{
    int rc;
    struct itimerval itv;
    itv.it_interval.tv_sec = 0;
    itv.it_interval.tv_usec = 0;
    itv.it_value.tv_sec = 0;
    itv.it_value.tv_usec = timeout_ms * 1000;

    // normalize the timer
    while(itv.it_value.tv_usec >= 1000000) {
        itv.it_value.tv_usec -= 1000000;
        itv.it_value.tv_sec += 1;
    }
    
    rc = setitimer(ITIMER_REAL, &itv, NULL);
    if (rc < 0) {
        ERR_LOG("unable to set timeout");
        exit(-1);
    }
    
    if (signal(SIGALRM, handle_timeout) == SIG_ERR)
        ERR_LOG("unable to set timeout handler, continuing anyway: %m");
}

struct json_object  *create_new_jobj_msg(int timeout_ms,
                                         const char *resource,
                                         const char *direction,
                                         int cpu,
                                         const char *online_cpus)
{
    //validate values
    if (timeout_ms < TIMEOUT_OVERHEAD_MS) {
        printf("timeout %d too short\n", timeout_ms);
        goto invalid_values;
    }

    if (strcmp(resource, "cpu")!=0) {
        printf("invalid resource %s\n", resource);
        goto invalid_values;
    }

    struct json_object *jobj_online_cpus;
    if (!strcmp(direction, "up")) {
        jobj_online_cpus = json_tokener_parse(online_cpus);
        if (!json_object_is_type(jobj_online_cpus, json_type_array)) {
            printf("invalid online_cpus %s\n", online_cpus);
            goto invalid_values;
        }
        len_request_online_cpus = json_object_array_length(jobj_online_cpus);
        request_online_cpus = malloc(len_request_online_cpus*sizeof(int));
        int i;
        for (i=0; i< len_request_online_cpus; i++) {
            request_online_cpus[i] = json_object_get_int(json_object_array_get_idx(jobj_online_cpus, i));
        }

    } else if (strcmp(direction, "down")!=0) {
        printf("invalid direction %s\n", direction);
        goto invalid_values;
    }

    struct json_object *jobj_msg = json_object_new_object();
    if (jobj_msg == NULL) {
        printf("failed to allocate json object for msg\n");
        return NULL;
    }

    json_object_object_add(jobj_msg, VERSION, json_object_new_int(CUR_VERSION));
    json_object_object_add(jobj_msg, MSG_TYPE, json_object_new_string(MSG_TYPE_SCALE_REQUEST));
    json_object_object_add(jobj_msg, TIMEOUT_MS, json_object_new_int(timeout_ms - MIN_SCRIPT_TIMEOUT_MS));
    json_object_object_add(jobj_msg, RESOURCE, json_object_new_string(resource));
    json_object_object_add(jobj_msg, DIRECTION, json_object_new_string(direction));

    if (!strcmp(direction, "up")) {
        json_object_object_add(jobj_msg, ONLINE_CPU, json_object_new_int(cpu));
        json_object_object_add(jobj_msg, ONLINE_CPUS, jobj_online_cpus);
    }

    return jobj_msg;

invalid_values:
    usage();
    return NULL;
}

int main(int argc, char *argv[])
{
    int i;
    char *instance_name;

    // msg values
    int cpu;
    const char *resource;
    const char *direction;
    const char *request_online_cpus_str = NULL;

    for(i=1;i<argc;i++) {
        if (0==strcmp(argv[i], "--timeout")) {
            i++;
            if (i<argc) {
                timeout_ms = atoi(argv[i]);
            } else {
                printf("timeout option specified without timeout value\n");
                usage();
            }
        } else if (0==strcmp(argv[i], "--instance_name")) {
            i++;
            if (i<argc) {
                int len = strlen(argv[i]) + 1;
                if (len > INSTANCE_NAME_SIZE) {
                    printf("instance name is too large\n");
                    usage();
                } else
                    instance_name = argv[i];
            }
            else {
                printf("instance_name option specified without name\n");
                usage();
            }
        } else if (0==strcmp(argv[i], "--cpu_add")) {
            i++;
            if (i<argc) {
                cpu = atoi(argv[i]);
                i++;
                if (i<argc) {
                    request_online_cpus_str = argv[i];
                } else {
                        printf("cpu_add option specified but missing online cpu range\n");
                        usage();
                }
            } else {
                printf("cpu_add option specified but missing cpu\n");
                usage();
            }
            resource = "cpu";
            direction = "up";
        } else if (0==strcmp(argv[i], "--cpu_del")) {
            resource = "cpu";
            direction = "down";
        } else if (0==strcmp(argv[i], "--help")) {
            usage();
        } else {
            printf("Unknown argument %s\n", argv[i]);
            usage();
        }
    }

    struct json_object *jobj_msg = create_new_jobj_msg(timeout_ms, resource, direction,
                                 cpu, request_online_cpus_str);

    if (jobj_msg == NULL) {
        return -1;
    }

    const char *msg = json_object_to_json_string_ext(jobj_msg, JSON_C_TO_STRING_PLAIN);
    // save request data to compare with response
    request_cpu = cpu;

    setup_timeout(timeout_ms);
    handle_message(msg, instance_name);

    json_object_put(jobj_msg);
    return 0;
}
