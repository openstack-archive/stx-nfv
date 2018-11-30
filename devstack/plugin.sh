#!/bin/bash

# devstack/plugin.sh
# Triggers specific functions to install and configure stx-nfv

echo_summary "stx-nfv devstack plugin.sh called: $1/$2"

# check for service enabled
if is_service_enabled stx-nfv; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing stx-nfv"
        install_stx_nfv

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring stx-nfv"
        configure_stx_nfv

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing stx-nfv"
        start_stx_nfv

    elif [[ "$1" == "stack" && "$2" == "test-config" ]]; then
        echo_summary "Do sanity test on stx-nfv"
        test_stx_nfv
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Shutdown stx-nfv services"
        stop_stx_nfv
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Cleanup stx-nfv"
        cleanup_stx_nfv
    fi
fi

