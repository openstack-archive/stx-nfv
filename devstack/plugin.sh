# Initial source of lib script
source $DEST/stx-nfv/devstack/lib/stx-nfv

# check for service enabled
if is_service_enabled stx-nfv; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
	# Perform installation of service source
	echo_summary "Installing stx-nfv"
        install_guest_client

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
	# Configure after the other layer 1 and 2 services have been configured
	echo_summary "Configuring stx-nfv"
	:
    fi

fi

if [[ "$1" == "unstack" ]]; then
    :
fi

if [[ "$1" == "clean" ]]; then
    echo_summary "Clean stx-nfv"
    clean_guest_client
fi
