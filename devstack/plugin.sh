#!/bin/bash

# devstack/plugin.sh
# Triggers specific functions to install and configure stx-nfv

echo_summary "stx-nfv devstack plugin.sh called: $1/$2"

# check for service enabled
if is_service_enabled stx-nfv; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing stx-nfv"
        if is_service_enabled nfv-vim || is_service_enabled nfv-vim-api || is_service_enabled nfv-vim-webserver; then
            install_nfv
        fi
        if is_service_enabled nova-api-proxy; then
            install_nova_api_proxy
        fi
        if is_service_enabled guest-client; then
            install_guest_client
        fi

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring stx-nfv"
        :

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Starting stx-nfv"
        if is_service_enabled nfv-vim || is_service_enabled nfv-vim-api || is_service_enabled nfv-vim-webserver; then
            start_nfv
        fi
        if is_service_enabled nova-api-proxy; then
            start_nova_api_proxy
        fi
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Shutdown stx-nfv"
        if is_service_enabled nfv-vim || is_service_enabled nfv-vim-api || is_service_enabled nfv-vim-webserver; then
            stop_nfv
        fi
        if is_service_enabled nova-api-proxy; then
            stop_nova_api_proxy
        fi
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Clean stx-nfv"
        if is_service_enabled nfv-vim || is_service_enabled nfv-vim-api || is_service_enabled nfv-vim-webserver; then
            cleanup_nfv
        fi
        if is_service_enabled nova-api-proxy; then
            cleanup_nova_api_proxy
        fi
        if is_service_enabled guest-client; then
            cleanup_guest_client
        fi
    fi
fi
