#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim.rpc._rpc_defs import RPC_MSG_RESULT  # noqa: F401
from nfv_vim.rpc._rpc_defs import RPC_MSG_TYPE  # noqa: F401
from nfv_vim.rpc._rpc_defs import RPC_MSG_VERSION  # noqa: F401
from nfv_vim.rpc._rpc_message import RPCMessage  # noqa: F401

from nfv_vim.rpc._rpc_message_image import APIRequestCreateImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIRequestDeleteImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIRequestGetImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIRequestUpdateImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIResponseCreateImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIResponseDeleteImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIResponseGetImage  # noqa: F401
from nfv_vim.rpc._rpc_message_image import APIResponseUpdateImage  # noqa: F401

from nfv_vim.rpc._rpc_message_volume import APIRequestCreateVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIRequestDeleteVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIRequestGetVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIRequestUpdateVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIResponseCreateVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIResponseDeleteVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIResponseGetVolume  # noqa: F401
from nfv_vim.rpc._rpc_message_volume import APIResponseUpdateVolume  # noqa: F401

from nfv_vim.rpc._rpc_message_instance import APIRequestColdMigrateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestCreateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestDeleteInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestEvacuateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestGetInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestLiveMigrateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestPauseInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestRebootInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestResumeInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestStartInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestStopInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestSuspendInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIRequestUnpauseInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseColdMigrateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseCreateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseDeleteInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseEvacuateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseGetInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseLiveMigrateInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponsePauseInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseRebootInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseResumeInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseStartInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseStopInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseSuspendInstance  # noqa: F401
from nfv_vim.rpc._rpc_message_instance import APIResponseUnpauseInstance  # noqa: F401

from nfv_vim.rpc._rpc_message_subnet import APIRequestCreateSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIRequestDeleteSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIRequestGetSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIRequestUpdateSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIResponseCreateSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIResponseDeleteSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIResponseGetSubnet  # noqa: F401
from nfv_vim.rpc._rpc_message_subnet import APIResponseUpdateSubnet  # noqa: F401

from nfv_vim.rpc._rpc_message_network import APIRequestCreateNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIRequestDeleteNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIRequestGetNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIRequestUpdateNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIResponseCreateNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIResponseDeleteNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIResponseGetNetwork  # noqa: F401
from nfv_vim.rpc._rpc_message_network import APIResponseUpdateNetwork  # noqa: F401

from nfv_vim.rpc._rpc_message_sw_update import APIRequestAbortSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIRequestApplySwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIRequestCreateSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIRequestCreateSwUpgradeStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIRequestDeleteSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIRequestGetSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIResponseAbortSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIResponseApplySwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIResponseCreateSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIResponseDeleteSwUpdateStrategy  # noqa: F401
from nfv_vim.rpc._rpc_message_sw_update import APIResponseGetSwUpdateStrategy  # noqa: F401
