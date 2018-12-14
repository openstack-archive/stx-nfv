#!/bin/bash

# devstack/plugin.sh
# Triggers specific functions to install and configure stx-nfv

echo_summary "stx-nfv devstack plugin.sh called: $1/$2"

# check for service enabled
if is_service_enabled stx-nfv; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing stx-nfv"
        install_nfv
        install_nova_api_proxy
        install_guest_client
        install_mtce_guest

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring stx-nfv"
        configure_nfv
        configure_nova_api_proxy
        configure_mtce_guest

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Starting stx-nfv"
        start_nfv
        start_nova_api_proxy
        start_mtce_guest
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Shutdown stx-nfv"
        stop_nfv
        stop_nova_api_proxy
        stop_mtce_guest
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Clean stx-nfv"
        cleanup_nfv
        cleanup_nova_api_proxy
        cleanup_guest_client
        cleanup_mtce_guest
    fi
fi
