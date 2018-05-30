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
#include "guest_test_cli.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#include "guest_types.h"
#include "guest_debug.h"
#include "guest_selobj.h"
#include "guest_stream.h"

#include "guest_heartbeat_msg.h"

static GuestStreamT _stream;

// ****************************************************************************
// Guest Test CLI - Usage
// ======================
void guest_test_cli_usage( void )
{
    printf("***************************************************\n");
    printf("* CLI Options:                                    *\n");
    printf("*   1 - send action request [pause, revocable]    *\n");
    printf("*   2 - send action request [pause, irrevocable]  *\n");
    printf("***************************************************\n");
}
// ****************************************************************************

// ****************************************************************************
// Guest Test CLI - Dispatch
// =========================
static void guest_test_cli_dispatch( int selobj )
{
    int msg_size;
    int bytes_received;
    int result;
    GuestErrorT error;

    result = read(STDIN_FILENO, _stream.end_ptr, _stream.avail);
    if (0 > result)
    {
        if (EINTR == errno)
        {
            DPRINTFD("Interrupted on socket read, error=%s.", strerror(errno));
            return;

        } else {
            DPRINTFE("Failed to read from socket, error=%s.", strerror(errno));
            return;
        }
    } else if (0 == result) {
        DPRINTFD("No message received from socket.");
        return;

    } else {
        DPRINTFV("Received message, msg_size=%i.", result);
        bytes_received = result;
    }

    _stream.end_ptr += bytes_received;
    _stream.avail -= bytes_received;
    _stream.size += bytes_received;

    msg_size = guest_stream_get(&_stream);
    if (0 <= msg_size)
    {
        _stream.bytes[msg_size] = '\0';
        DPRINTFD("CLI message: %s, msg_size=%i", _stream.bytes, msg_size);

        switch(_stream.bytes[0])
        {
            case 'h':
                guest_test_cli_usage();
                break;

            case '1':
                error = guest_heartbeat_msg_send_action_notify(
                        rand(), GUEST_HEARTBEAT_EVENT_PAUSE,
                        GUEST_HEARTBEAT_NOTIFY_REVOCABLE, 5);
                if (GUEST_OKAY != error)
                    DPRINTFE("Failed to send action notify, error=%s.",
                             guest_error_str(error));
                break;

            case '2':
                error = guest_heartbeat_msg_send_action_notify(
                        rand(), GUEST_HEARTBEAT_EVENT_PAUSE,
                        GUEST_HEARTBEAT_NOTIFY_IRREVOCABLE, 5);
                if (GUEST_OKAY != error)
                    DPRINTFE("Failed to send action notify, error=%s.",
                             guest_error_str(error));
                break;

            default:
                break;
        }

        guest_stream_advance(msg_size+1, &_stream);
    }

    if (0 >= _stream.avail)
        guest_stream_reset(&_stream);
}
// ****************************************************************************

// ****************************************************************************
// Guest Test CLI - Initialize
// ===========================
GuestErrorT guest_test_cli_initialize( void )
{
    GuestSelObjCallbacksT callbacks;
    GuestErrorT error;

    memset(&callbacks, 0, sizeof(callbacks));
    callbacks.read_callback = guest_test_cli_dispatch;

    error = guest_selobj_register(STDIN_FILENO, &callbacks);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to register stdin selection object, error=%s.",
                 guest_error_str(error));
        return error;
    }

    error = guest_stream_setup("\n", 1, 256*2, &_stream);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to setup stdin stream, error=%s.",
                 guest_error_str(error));
        return error;
    }

    return GUEST_OKAY;
}
// ****************************************************************************

// ****************************************************************************
// Guest Test CLI - Finalize
// =========================
GuestErrorT guest_test_cli_finalize( void )
{
    GuestErrorT error;

    error = guest_stream_release(&_stream);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed release stream, error=%s.", guest_error_str(error));
    }

    error = guest_selobj_deregister(STDIN_FILENO);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to deregister stdin selection object, error=%s.",
                 guest_error_str(error));
    }

    return GUEST_OKAY;
}
// ****************************************************************************
