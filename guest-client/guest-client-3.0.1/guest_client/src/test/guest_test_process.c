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
#include "guest_test_process.h"

#include <signal.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>

#include "guest_limits.h"
#include "guest_types.h"
#include "guest_debug.h"
#include "guest_signal.h"
#include "guest_config.h"
#include "guest_selobj.h"
#include "guest_timer.h"
#include "guest_channel.h"
#include "guest_stream.h"
#include "guest_test.h"
#include "guest_test_cli.h"

static sig_atomic_t _stay_on = 1;

// ****************************************************************************
// Guest Test Process - Signal Handler
// ===================================
static void guest_test_process_signal_handler( int signum )
{
    switch (signum)
    {
        case SIGINT:
        case SIGTERM:
        case SIGQUIT:
            _stay_on = 0;
            break;

        case SIGCONT:
            DPRINTFD("Ignoring signal SIGCONT (%i).", signum);
            break;

        case SIGPIPE:
            DPRINTFD("Ignoring signal SIGPIPE (%i).", signum);
            break;

        default:
            DPRINTFD("Signal (%i) ignored.", signum);
            break;
    }
}
// ****************************************************************************

// ****************************************************************************
// Guest Test Process - Initialize
// ===============================
static GuestErrorT guest_test_process_initialize(
        int argc, char *argv[], char *envp[] )
{
    GuestConfigT* config = NULL;
    GuestErrorT error;

    error = guest_config_initialize(argc, argv, envp);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize configuration module, error=%s.",
                 guest_error_str(error));
        guest_config_show_usage();
        return GUEST_FAILED;
    }

    error = guest_selobj_initialize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize selection object module, error=%s.",
                 guest_error_str(error));
        return GUEST_FAILED;
    }

    error = guest_timer_initialize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize timer module, error=%s.",
                 guest_error_str(error));
        return GUEST_FAILED;
    }

    error = guest_channel_initialize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize channel module, error=%s.",
                 guest_error_str(error));
        return GUEST_FAILED;
    }

    error = guest_stream_initialize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize stream module, error=%s.",
                 guest_error_str(error));
        return GUEST_FAILED;
    }

    config = guest_config_get();

    error = guest_test_initialize(config->comm_device);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize test module, error=%s.",
                 guest_error_str(error));
        return GUEST_FAILED;
    }

    error = guest_test_cli_initialize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to initialize test cli module, error=%s.",
                 guest_error_str(error));
        return GUEST_FAILED;
    }

    return GUEST_OKAY;
}
// ****************************************************************************

// ****************************************************************************
// Guest Test Process - Finalize
// =============================
static GuestErrorT guest_test_process_finalize( void )
{
    GuestErrorT error;

    error = guest_test_cli_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finalize test cli module, error=%s.",
                 guest_error_str(error));
    }

    error = guest_test_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finalize test module, error=%s.",
                 guest_error_str(error));
    }

    error = guest_stream_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finalize stream module, error=%s.",
                 guest_error_str(error));
    }

    error = guest_channel_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finalize channel module, error=%s.",
                 guest_error_str(error));
    }

    error = guest_timer_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finalize timer module, error=%s.",
                 guest_error_str(error));
    }

    error = guest_selobj_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finialize selection object module, error=%s.",
                 guest_error_str(error));
    }

    error = guest_config_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed to finialize configuration module, error=%s.",
                 guest_error_str(error));
    }

    return GUEST_OKAY;
}
// ****************************************************************************

// ****************************************************************************
// Guest Test Process - Main
// =========================
GuestErrorT guest_test_process_main( int argc, char *argv[], char *envp[] )
{
    unsigned int next_interval_in_ms;
    GuestErrorT error;

    DPRINTFI("Starting.");

    guest_signal_register_handler(SIGINT,  guest_test_process_signal_handler);
    guest_signal_register_handler(SIGTERM, guest_test_process_signal_handler);
    guest_signal_register_handler(SIGQUIT, guest_test_process_signal_handler);
    guest_signal_register_handler(SIGCONT, guest_test_process_signal_handler);
    guest_signal_register_handler(SIGPIPE, guest_test_process_signal_handler);

    error = guest_test_process_initialize(argc, argv, envp);
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed initialize test process, error=%s.",
                 guest_error_str(error));
        return error;
    }

    DPRINTFI("Started.");

    guest_test_cli_usage();

    while (_stay_on)
    {
        next_interval_in_ms = guest_timer_schedule();

        error = guest_selobj_dispatch(next_interval_in_ms);
        if (GUEST_OKAY != error)
        {
            DPRINTFE("Selection object dispatch failed, error=%s.",
                     guest_error_str(error));
            break;
        }
    }

    DPRINTFI("Shutting down.");

    error = guest_test_process_finalize();
    if (GUEST_OKAY != error)
    {
        DPRINTFE("Failed finalize test process, error=%s.",
                 guest_error_str(error) );
    }

    DPRINTFI("Shutdown complete.");

    return GUEST_OKAY;
}
// ****************************************************************************
