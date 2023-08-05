# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
from oslo_messaging.rpc import dispatcher as rpc
import six

from senlin.common import exception
from senlin.db import api as db_api
from senlin.engine.actions import base as action_mod
from senlin.engine import dispatcher
from senlin.engine import environment
from senlin.engine import service
from senlin.tests.unit.common import base
from senlin.tests.unit.common import utils
from senlin.tests.unit import fakes


class ClusterPolicyTest(base.SenlinTestCase):

    def setUp(self):
        super(ClusterPolicyTest, self).setUp()
        self.ctx = utils.dummy_context(project='cluster_policy_test_project')
        self.eng = service.EngineService('host-a', 'topic-a')
        self.eng.init_tgm()

        self.eng.dispatcher = mock.Mock()
        self.patchobject(dispatcher, 'notify')

        env = environment.global_env()
        env.register_profile('TestProfile-1.0', fakes.TestProfile)
        env.register_policy('TestPolicy-1.0', fakes.TestPolicy)

        profile_spec = {
            'type': 'TestProfile',
            'version': '1.0',
            'properties': {'INT': 10, 'STR': 'string'},
        }
        self.profile = self.eng.profile_create(self.ctx, 'p-test',
                                               profile_spec)

        policy_spec = {
            'type': 'TestPolicy',
            'version': '1.0',
            'properties': {'KEY2': 5},
        }
        self.policy = self.eng.policy_create(self.ctx, 'policy_1', policy_spec)

        self.cluster = self.eng.cluster_create(self.ctx, 'c-1', 0,
                                               self.profile['id'])

    def _verify_action(self, obj, action, name, target, cause, inputs=None):
        if inputs is None:
            inputs = {}
        self.assertEqual(action, obj['action'])
        self.assertEqual(name, obj['name'])
        self.assertEqual(target, obj['target'])
        self.assertEqual(cause, obj['cause'])
        self.assertEqual(inputs, obj['inputs'])

    @mock.patch.object(dispatcher, 'start_action')
    def test_cluster_policy_attach(self, notify):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']
        action = self.eng.cluster_policy_attach(
            self.ctx, cluster_id, policy_id, False)

        action_id = action['action']
        action = db_api.action_get(self.ctx, action_id)
        self.assertIsNotNone(action)
        inputs = {
            'policy_id': policy_id,
            'enabled': True
        }
        self._verify_action(action, 'CLUSTER_ATTACH_POLICY',
                            'attach_policy_%s' % cluster_id[:8],
                            cluster_id, cause=action_mod.CAUSE_RPC,
                            inputs=inputs)
        notify.assert_called_with(action_id=action_id)

        self.assertEqual(1, notify.call_count)

    @mock.patch.object(dispatcher, 'start_action')
    def test_cluster_policy_attach_using_default(self, notify):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']
        action = self.eng.cluster_policy_attach(self.ctx, cluster_id,
                                                policy_id)

        action_id = action['action']
        action = db_api.action_get(self.ctx, action_id)
        self.assertIsNotNone(action)
        inputs = {
            'policy_id': policy_id,
            'enabled': True
        }
        self._verify_action(action, 'CLUSTER_ATTACH_POLICY',
                            'attach_policy_%s' % cluster_id[:8],
                            cluster_id, cause=action_mod.CAUSE_RPC,
                            inputs=inputs)
        notify.assert_called_with(action_id=action_id)

        self.assertEqual(1, notify.call_count)

    def test_cluster_policy_attach_cluster_not_found(self):
        policy_id = self.policy['id']
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_attach,
                               self.ctx, 'Bogus', policy_id)
        self.assertEqual(exception.ClusterNotFound, ex.exc_info[0])
        self.assertEqual("The cluster (Bogus) could not be found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_attach_policy_not_found(self):
        cluster_id = self.cluster['id']
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_attach,
                               self.ctx, cluster_id, 'BOGUS')
        self.assertEqual(exception.SenlinBadRequest, ex.exc_info[0])
        self.assertEqual("The request is malformed: The specified policy "
                         "(BOGUS) is not found.",
                         six.text_type(ex.exc_info[1]))

    @mock.patch.object(dispatcher, 'start_action')
    def test_cluster_policy_attach_enabled_not_boolean(self, notify):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']

        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_attach,
                               self.ctx, cluster_id, policy_id,
                               enabled='No')
        self.assertEqual(exception.InvalidParameter, ex.exc_info[0])
        self.assertEqual("Invalid value 'No' specified for 'enabled'",
                         six.text_type(ex.exc_info[1]))

    @mock.patch.object(dispatcher, 'start_action')
    def test_cluster_policy_detach(self, notify):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']

        values = {'enabled': True}
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy_id, values)
        action = self.eng.cluster_policy_detach(self.ctx, cluster_id,
                                                policy_id)

        action_id = action['action']
        action = db_api.action_get(self.ctx, action_id)
        self.assertIsNotNone(action)
        self._verify_action(action, 'CLUSTER_DETACH_POLICY',
                            'detach_policy_%s' % cluster_id[:8],
                            cluster_id, cause=action_mod.CAUSE_RPC,
                            inputs={'policy_id': policy_id})
        notify.assert_called_with(action_id=action_id)

        # called twice: attach and detach
        self.assertEqual(1, notify.call_count)

    def test_cluster_policy_detach_cluster_not_found(self):
        policy_id = self.policy['id']
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_detach,
                               self.ctx, 'Bogus', policy_id)
        self.assertEqual(exception.ClusterNotFound, ex.exc_info[0])
        self.assertEqual("The cluster (Bogus) could not be found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_detach_policy_not_found(self):
        cluster_id = self.cluster['id']
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_detach,
                               self.ctx, cluster_id, 'Bogus')
        self.assertEqual(exception.SenlinBadRequest, ex.exc_info[0])
        self.assertEqual("The request is malformed: The specified policy "
                         "(Bogus) is not found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_detach_binding_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_detach,
                               self.ctx, self.cluster['id'], self.policy['id'])
        self.assertEqual(exception.SenlinBadRequest, ex.exc_info[0])
        self.assertEqual(("The request is malformed: The policy (%(p)s) is "
                          "not attached to the specified cluster (%(c)s)." %
                          dict(p=self.policy['id'], c=self.cluster['id'])),
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_get(self):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']
        values = {
            'enabled': True
        }
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy_id, values)

        result = self.eng.cluster_policy_get(self.ctx, cluster_id, policy_id)
        self.assertEqual(cluster_id, result['cluster_id'])
        self.assertEqual(policy_id, result['policy_id'])
        self.assertEqual(self.cluster['name'], result['cluster_name'])
        self.assertEqual(self.policy['type'], result['policy_type'])
        self.assertEqual(self.policy['name'], result['policy_name'])
        self.assertTrue(result['enabled'])

    def test_cluster_policy_get_cluster_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_get,
                               self.ctx, 'Bogus', self.policy['id'])
        self.assertEqual(exception.ClusterNotFound, ex.exc_info[0])
        self.assertEqual("The cluster (Bogus) could not be found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_get_policy_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_get,
                               self.ctx, self.cluster['id'], 'Bogus')
        self.assertEqual(exception.PolicyNotFound, ex.exc_info[0])
        self.assertEqual("The policy (Bogus) could not be found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_get_binding_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_get,
                               self.ctx, self.cluster['id'], self.policy['id'])
        self.assertEqual(exception.PolicyBindingNotFound, ex.exc_info[0])
        self.assertEqual(("The policy (%(policy)s) is not found attached to "
                          "the specified cluster (%(cluster)s)." %
                          dict(policy=self.policy['id'],
                               cluster=self.cluster['id'])),
                         six.text_type(ex.exc_info[1]))

    def _prepare_policy(self, name, type_name=None, version=None):
        if type_name is not None:
            env = environment.global_env()
            type_str = "-".join([type_name, version])
            env.register_policy(type_str, fakes.TestPolicy)
        else:
            type_name = 'TestPolicy'

        spec = {
            'type': type_name,
            'version': '1.0',
            'properties': {'KEY2': 5}
        }
        return self.eng.policy_create(self.ctx, name, spec)

    def test_cluster_policy_list(self):
        cluster_id = self.cluster['id']
        policy1 = self._prepare_policy('p-1', 'Type1', '1.0')
        policy2 = self._prepare_policy('p-2', 'Type2', '1.0')
        v = {
            'enabled': True
        }
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy1['id'], v)
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy2['id'], v)

        result = self.eng.cluster_policy_list(self.ctx, cluster_id)
        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))
        policy_ids = [b['policy_id'] for b in result]
        self.assertIn(policy1['id'], policy_ids)
        self.assertIn(policy2['id'], policy_ids)

    def test_cluster_policy_list_cluster_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_list,
                               self.ctx, 'Bogus')
        self.assertEqual(exception.ClusterNotFound, ex.exc_info[0])
        self.assertEqual("The cluster (Bogus) could not be found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_list_no_binding(self):
        result = self.eng.cluster_policy_list(self.ctx, self.cluster['id'])
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))

    def test_cluster_policy_list_filters(self):
        cluster_id = self.cluster['id']
        policy1 = self._prepare_policy('p-1', 'Type1', '1.0')
        policy2 = self._prepare_policy('p-2', 'Type2', '1.0')

        v = {'enabled': True}
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy1['id'], v)
        v = {'enabled': False}
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy2['id'], v)

        # filter by enabled
        result = self.eng.cluster_policy_list(self.ctx, cluster_id,
                                              filters={'enabled': True})
        policy_ids = [b['policy_id'] for b in result]
        self.assertEqual(1, len(policy_ids))
        self.assertIn(policy1['id'], policy_ids)

    def test_cluster_policy_list_sorting(self):
        cid = self.cluster['id']
        policy1 = self._prepare_policy('p-1', 'Type1', '1.0')
        policy2 = self._prepare_policy('p-2', 'Type2', '1.0')

        v = {'enabled': True}
        db_api.cluster_policy_attach(self.ctx, cid, policy1['id'], v)
        v = {'enabled': False}
        db_api.cluster_policy_attach(self.ctx, cid, policy2['id'], v)

        # sort by enabled
        result = self.eng.cluster_policy_list(self.ctx, cid, sort='enabled')
        policy_ids = [b['policy_id'] for b in result]
        self.assertIn(policy1['id'], policy_ids[1])

    @mock.patch.object(dispatcher, 'start_action')
    def test_cluster_policy_update(self, notify):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']
        values = {
            'enabled': False
        }
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy_id, values)

        action = self.eng.cluster_policy_update(
            self.ctx, cluster_id, policy_id, enabled=True)

        action_id = action['action']
        action = db_api.action_get(self.ctx, action_id)
        self.assertIsNotNone(action)
        self._verify_action(action, 'CLUSTER_UPDATE_POLICY',
                            'update_policy_%s' % cluster_id[:8],
                            cluster_id, cause=action_mod.CAUSE_RPC,
                            inputs={'policy_id': policy_id, 'enabled': True})
        notify.assert_called_once_with(action_id=action_id)

    def test_cluster_policy_update_cluster_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_update,
                               self.ctx, 'Bogus', self.policy['id'],
                               enabled=True)
        self.assertEqual(exception.ClusterNotFound, ex.exc_info[0])
        self.assertEqual("The cluster (Bogus) could not be found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_update_policy_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_update,
                               self.ctx, self.cluster['id'], 'Bogus',
                               enabled=True)
        self.assertEqual(exception.SenlinBadRequest, ex.exc_info[0])
        self.assertEqual("The request is malformed: The specified policy "
                         "(Bogus) is not found.",
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_update_binding_not_found(self):
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_update,
                               self.ctx,
                               self.cluster['id'], self.policy['id'],
                               enabled=True)
        self.assertEqual(exception.SenlinBadRequest, ex.exc_info[0])
        self.assertEqual(("The request is malformed: The policy (%(p)s) is "
                          "not attached to the specified cluster (%(c)s)." %
                          dict(p=self.policy['id'], c=self.cluster['id'])),
                         six.text_type(ex.exc_info[1]))

    def test_cluster_policy_update_parameter_invalid(self):
        cluster_id = self.cluster['id']
        policy_id = self.policy['id']
        values = {'enabled': True}
        db_api.cluster_policy_attach(self.ctx, cluster_id, policy_id, values)
        ex = self.assertRaises(rpc.ExpectedException,
                               self.eng.cluster_policy_update,
                               self.ctx, cluster_id, policy_id,
                               enabled='No')

        self.assertEqual(exception.InvalidParameter, ex.exc_info[0])
        self.assertEqual("Invalid value 'No' specified for 'enabled'",
                         six.text_type(ex.exc_info[1]))
