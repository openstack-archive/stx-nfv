#
# Copyright
#
# SPDX-License-Identifier: Apache-2.0
#
import mock
import kubernetes
import threading
from kubernetes.client.rest import ApiException
from . import testcase
from nfv_plugins.nfvi_plugins.clients import kubernetes_client

test_node_repo = {}
mutex = threading.Lock()


def mock_read_node(obj, node_name):
    print('mock read_node')
    if node_name in test_node_repo:
        return test_node_repo[node_name]
    else:
        raise ApiException


def mock_load_kube_config(path):
    print('mock load_kube_config')
    return


def exchange_json_to_V1Node(body):
    node = kubernetes.client.V1Node()

    # exchange taints only.
    if 'spec' not in body:
        return node

    node.spec = kubernetes.client.V1NodeSpec()
    if 'taints' not in body['spec']:
        return node

    node.spec.taints = []
    for taint in body['spec']['taints']:
        if type(taint) is kubernetes.client.models.v1_taint.V1Taint:
            node.spec.taints.append(taint)
            continue

        if 'key' in taint and 'effect' in taint:
            taintBody = kubernetes.client.V1Taint(taint['effect'], taint['key'])
            if 'value' in taint:
                taintBody.value = taint['value']
            node.spec.taints.append(taintBody)

    return node


def mock_patch_node(obj, node_name, body):
    print("mock patch_node. body is: %s" % (body))
    if node_name in test_node_repo:
        mutex.acquire()
        test_node_repo[node_name] = exchange_json_to_V1Node(body)
        mutex.release()
    else:
        raise ApiException

    return test_node_repo[node_name]


@mock.patch('kubernetes.config.load_kube_config', mock_load_kube_config)
@mock.patch('kubernetes.client.CoreV1Api.read_node', mock_read_node)
@mock.patch('kubernetes.client.CoreV1Api.patch_node', mock_patch_node)
class TestNFVPluginsK8SNodeTaint(testcase.NFVTestCase):

    test_node_name = 'testNode'
    test_key1 = 'testKey1'
    test_value1 = 'testValue1'
    test_key2 = 'testKey2'
    test_value2 = 'testValue2'

    def check_taint_exist(self, node_name, effect, key, value):
        try:
            kube_client = kubernetes_client.get_client()
            response = kube_client.read_node(node_name)
        except ApiException as e:
            return False

        taints = response.spec.taints
        if taints is not None:
            for taint in taints:
                if taint.key == key and taint.effect == effect and taint.value == value:
                    return True
        return False

    def setup_node_repo(self, node_name):
        body = kubernetes.client.V1Node()
        body.spec = kubernetes.client.V1NodeSpec()
        body.spec.taints = []

        mutex.acquire()
        test_node_repo[node_name] = body
        mutex.release()

    def node_repo_clear(self):
        mutex.acquire()
        test_node_repo.clear()
        mutex.release()

    def setUp(self):
        print('setUp')
        super(TestNFVPluginsK8SNodeTaint, self).setUp()
        self.setup_node_repo(self.test_node_name)

    def tearDown(self):
        print('tearDown')
        super(TestNFVPluginsK8SNodeTaint, self).tearDown()
        self.node_repo_clear()

    def test_when_add_taint_and_get_then_get_it(self):
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is False
        kubernetes_client.taint_node(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1)
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is True

    def test_when_add_two_taints_and_get_then_get_them(self):
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is False
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key2, self.test_value2) is False

        kubernetes_client.taint_node(self.test_node_name, 'NoExecute', self.test_key2, self.test_value2)
        kubernetes_client.taint_node(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1)

        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is True
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key2, self.test_value2) is True

    def test_when_delete_exist_taint_and_get_then_get_none(self):
        kubernetes_client.taint_node(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1)
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is True
        kubernetes_client.untaint_node(self.test_node_name, 'NoExecute', self.test_key1)
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is False

    def test_when_delete_no_exist_taint_and_get_then_get_none(self):
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is False
        kubernetes_client.untaint_node(self.test_node_name, 'NoExecute', self.test_key1)
        assert self.check_taint_exist(self.test_node_name, 'NoExecute', self.test_key1, self.test_value1) is False

    def test_when_add_taint_twice_and_delete_it_and_get_then_get_none(self):
        kubernetes_client.taint_node(self.test_node_name, 'NoSchedule', self.test_key1, self.test_value1)
        kubernetes_client.taint_node(self.test_node_name, 'NoSchedule', self.test_key1, self.test_value1)
        assert self.check_taint_exist(self.test_node_name, 'NoSchedule', self.test_key1, self.test_value1) is True

        kubernetes_client.untaint_node(self.test_node_name, 'NoSchedule', self.test_key1)
        assert self.check_taint_exist(self.test_node_name, 'NoSchedule', self.test_key1, self.test_value1) is False
