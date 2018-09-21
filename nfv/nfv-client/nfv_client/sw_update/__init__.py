# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_client.sw_update._sw_update import STRATEGY_NAME_SW_PATCH  # noqa: F401
from nfv_client.sw_update._sw_update import STRATEGY_NAME_SW_UPGRADE  # noqa: F401
from nfv_client.sw_update._sw_update import APPLY_TYPE_SERIAL  # noqa: F401
from nfv_client.sw_update._sw_update import APPLY_TYPE_PARALLEL  # noqa: F401
from nfv_client.sw_update._sw_update import APPLY_TYPE_IGNORE  # noqa: F401
from nfv_client.sw_update._sw_update import INSTANCE_ACTION_MIGRATE  # noqa: F401
from nfv_client.sw_update._sw_update import INSTANCE_ACTION_STOP_START  # noqa: F401
from nfv_client.sw_update._sw_update import ALARM_RESTRICTIONS_STRICT  # noqa: F401
from nfv_client.sw_update._sw_update import ALARM_RESTRICTIONS_RELAXED  # noqa: F401
from nfv_client.sw_update._sw_update import create_strategy  # noqa: F401
from nfv_client.sw_update._sw_update import delete_strategy  # noqa: F401
from nfv_client.sw_update._sw_update import apply_strategy  # noqa: F401
from nfv_client.sw_update._sw_update import abort_strategy  # noqa: F401
from nfv_client.sw_update._sw_update import show_strategy  # noqa: F401
