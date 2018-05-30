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
#include "guest_test.h"

#include <stdbool.h>
#include <string.h>

#include "guest_types.h"
#include "guest_debug.h"
#include "guest_timer.h"

#include "guest_heartbeat_types.h"
#include "guest_heartbeat_msg.h"

static bool _challenge_response_recvd = false;
static GuestTimerIdT _heartbeat_timer_id = GUEST_TIMER_ID_INVALID;
static GuestTimerIdT _heartbeat_timeout_timer_id = GUEST_TIMER_ID_INVALID;

// ****************************************************************************
// Guest Heartbeat - Timeout
// =========================
static bool guest_heartbeat_timeout( GuestTimerIdT timer_id )
{
    GuestErrorT error;

    DPRINTFE("--------> HEARTBEAT TIMEOUT <--------");

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timer_id = GUEST_TIMER_ID_INVALID;
    }

    return false; // don't rearm
}
// ****************************************************************************

// ****************************************************************************
// Guest Heartbeat - Periodic
// ==========================
static bool guest_heartbeat_periodic( GuestTimerIdT timer_id )
{
    GuestErrorT error;

    if (_challenge_response_recvd)
    {
        error = guest_heartbeat_msg_send_challenge();
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to send challenge, error=%s.",
                     guest_error_str(error));
        }
        _challenge_response_recvd = false;
    }
    return true; // rearm
}
// ****************************************************************************

// ****************************************************************************
// Guest Heartbeat - Receive Init Message
// ======================================
static void guest_heartbeat_recv_init_msg(
        int invocation_id, GuestHeartbeatMsgInitDataT* data )
{
    GuestErrorT error;

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timer_id = GUEST_TIMER_ID_INVALID;
    }

    error = guest_timer_register(data->heartbeat_interval_ms,
                                 guest_heartbeat_periodic,
                                 &_heartbeat_timer_id);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to start heartbeat timer, error=%s.",
                 guest_error_str(error));
        return;
    }

    error = guest_heartbeat_msg_send_init_ack(invocation_id);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to send init ack, error=%s.", guest_error_str(error));
    }

    error = guest_heartbeat_msg_send_challenge();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to send challenge, error=%s.", guest_error_str(error));
    }

    _challenge_response_recvd = false;

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timeout_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timeout_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timeout timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timeout_timer_id = GUEST_TIMER_ID_INVALID;
    }

    error = guest_timer_register(data->heartbeat_interval_ms*2,
                                 guest_heartbeat_timeout,
                                 &_heartbeat_timeout_timer_id);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to start heartbeat timeout timer, error=%s.",
                 guest_error_str(error));
        return;
    }
}
// ****************************************************************************

// ****************************************************************************
// Guest Heartbeat - Receive Exit Message
// ======================================
static void guest_heartbeat_recv_exit_msg( char log_msg[] )
{
    GuestErrorT error;

    DPRINTFI("--------> HEARTBEAT EXIT <--------");
    DPRINTFI("reason=%s", log_msg);

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timer_id = GUEST_TIMER_ID_INVALID;
    }

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timeout_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timeout_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timeout timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timeout_timer_id = GUEST_TIMER_ID_INVALID;
    }
}
// ****************************************************************************

// ****************************************************************************
// Guest Heartbeat - Receive Challenge Ack Message
// ===============================================
static void guest_heartbeat_recv_challenge_ack_msg(
        bool health, GuestHeartbeatActionT corrective_action, char log_msg[] )
{
    GuestErrorT error;

    _challenge_response_recvd = true;

    if (!health)
    {
        DPRINTFE("--------> HEARTBEAT UNHEALTHY <--------");
        DPRINTFE("corrective_action=%s, reason=%s",
                 guest_heartbeat_action_str(corrective_action), log_msg);

        if (GUEST_TIMER_ID_INVALID != _heartbeat_timer_id)
        {
            error = guest_timer_deregister(_heartbeat_timer_id);
            if (GUEST_OKAY != error)
            {
                DPRINTFE("Failed to cancel heartbeat timer, error=%s.",
                         guest_error_str(error));
            }
            _heartbeat_timer_id = GUEST_TIMER_ID_INVALID;
        }

        if (GUEST_TIMER_ID_INVALID != _heartbeat_timeout_timer_id)
        {
            error = guest_timer_deregister(_heartbeat_timeout_timer_id);
            if (GUEST_OKAY != error)
            {
                DPRINTFE("Failed to cancel heartbeat timeout timer, error=%s.",
                         guest_error_str(error));
            }
            _heartbeat_timeout_timer_id = GUEST_TIMER_ID_INVALID;
        }

        return;
    }

    guest_timer_reset(_heartbeat_timeout_timer_id);
}
// ****************************************************************************

// ****************************************************************************
// Guest Heartbeat - Receive Action Response Message
// =================================================
static void guest_heartbeat_recv_action_response_msg(
        int invocation_id, GuestHeartbeatEventT event,
        GuestHeartbeatNotifyT notify, GuestHeartbeatVoteResultT vote_result,
        char log_msg[] )
{
    DPRINTFI("--------> ACTION RESPONSE <--------");
    DPRINTFI("invocation_id=%i event=%s, notify=%s, vote-result=%s, reason=%s",
             invocation_id, guest_heartbeat_event_str(event),
             guest_heartbeat_notify_str(notify),
             guest_heartbeat_vote_result_str(vote_result), log_msg);
}
// ****************************************************************************

// ****************************************************************************
// Guest Test - Initialize
// =======================
GuestErrorT guest_test_initialize( char* comm_device )
{
    GuestHeartbeatMsgCallbacksT callbacks;
    GuestErrorT error;

    memset(&callbacks, 0, sizeof(callbacks));

    callbacks.recv_init = guest_heartbeat_recv_init_msg;
    callbacks.recv_exit = guest_heartbeat_recv_exit_msg;
    callbacks.recv_challenge_ack = guest_heartbeat_recv_challenge_ack_msg;
    callbacks.recv_action_response = guest_heartbeat_recv_action_response_msg;

    error = guest_heartbeat_msg_initialize(comm_device, &callbacks);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize heartbeat messaging, error=%s.",
                 guest_error_str(error));
        return error;
    }

    return GUEST_OKAY;
}
// ****************************************************************************

// ****************************************************************************
// Guest Test - Finalize
// =====================
GuestErrorT guest_test_finalize( void )
{
    GuestErrorT error;

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timer_id = GUEST_TIMER_ID_INVALID;
    }

    if (GUEST_TIMER_ID_INVALID != _heartbeat_timeout_timer_id)
    {
        error = guest_timer_deregister(_heartbeat_timeout_timer_id);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Failed to cancel heartbeat timeout timer, error=%s.",
                     guest_error_str(error));
        }
        _heartbeat_timeout_timer_id = GUEST_TIMER_ID_INVALID;
    }

    error = guest_heartbeat_msg_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finalize heartbeat messaging, error=%s.",
                 guest_error_str(error));
    }

    return GUEST_OKAY;
}
// ****************************************************************************
