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
from oslo_config import cfg

from senlin.db.sqlalchemy import api as db_api
from senlin.engine.actions import base as action
from senlin.engine import dispatcher
from senlin.engine import scheduler
from senlin.engine import senlin_lock as lockm
from senlin.tests.unit.common import base
from senlin.tests.unit.common import utils


class SenlinLockTest(base.SenlinTestCase):

    def setUp(self):
        super(SenlinLockTest, self).setUp()

        self.ctx = utils.dummy_context()
        self.stub_action = self.patchobject(lockm, 'action_on_dead_engine',
                                            return_value=False)

    @mock.patch.object(db_api, "cluster_lock_acquire")
    def test_cluster_lock_acquire_already_owner(self, mock_acquire):
        mock_acquire.return_value = ['ACTION_XYZ']

        res = lockm.cluster_lock_acquire(self.ctx, 'CLUSTER_A', 'ACTION_XYZ')

        self.assertTrue(res)
        mock_acquire.assert_called_once_with('CLUSTER_A', 'ACTION_XYZ',
                                             lockm.CLUSTER_SCOPE)

    @mock.patch.object(action.Action, 'load')
    @mock.patch.object(db_api, "cluster_lock_acquire")
    @mock.patch.object(db_api, "cluster_lock_steal")
    def test_cluster_lock_acquire_dead_owner(self, mock_steal, mock_acquire,
                                             mock_action_load):
        # self.stub_action.return_value = True
        # mock_acquire.side_effect = ['ACTION_ABC']
        # mock_steal.side_effect = ['ACTION_XYZ']
        # act = mock.Mock()
        # mock_action_load.return_value = act

        # res = lockm.cluster_lock_acquire(self.ctx, 'CLUSTER_A', 'ACTION_XYZ')

        # self.assertTrue(res)
        # mock_acquire.assert_called_once_with('CLUSTER_A', 'ACTION_XYZ',
        #                                      lockm.CLUSTER_SCOPE)
        # mock_steal.assert_called_once_with('CLUSTER_A', 'ACTION_XYZ')
        # act.set_status.assert_called_once_with(
        #     result=action.Action.RES_ERROR,
        #     reason='Engine died when executing this action.'
        # )
        pass

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "cluster_lock_acquire")
    def test_cluster_lock_acquire_with_retry(self, mock_acquire, mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 5, enforce_type=True)
        mock_acquire.side_effect = ['ACTION_ABC', 'ACTION_ABC', 'ACTION_XYZ']

        res = lockm.cluster_lock_acquire(self.ctx, 'CLUSTER_A', 'ACTION_XYZ')

        self.assertTrue(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        acquire_calls = [
            mock.call('CLUSTER_A', 'ACTION_XYZ', lockm.CLUSTER_SCOPE)
        ]
        mock_acquire.assert_has_calls(acquire_calls * 3)

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "cluster_lock_acquire")
    def test_cluster_lock_acquire_max_retries(self, mock_acquire, mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 2, enforce_type=True)
        mock_acquire.side_effect = [
            'ACTION_ABC', 'ACTION_ABC', 'ACTION_ABC', 'ACTION_XYZ'
        ]

        res = lockm.cluster_lock_acquire(self.ctx, 'CLUSTER_A', 'ACTION_XYZ')

        self.assertFalse(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        self.assertEqual(2, mock_sleep.call_count)
        acquire_calls = [
            mock.call('CLUSTER_A', 'ACTION_XYZ', lockm.CLUSTER_SCOPE)
        ]
        mock_acquire.assert_has_calls(acquire_calls * 3)

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "cluster_lock_acquire")
    @mock.patch.object(db_api, "cluster_lock_steal")
    def test_cluster_lock_acquire_forced(self, mock_steal, mock_acquire,
                                         mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 2, enforce_type=True)
        mock_acquire.side_effect = ['ACTION_ABC', 'ACTION_ABC', 'ACTION_ABC']
        mock_steal.return_value = ['ACTION_XY']

        res = lockm.cluster_lock_acquire(self.ctx, 'CLUSTER_A',
                                         'ACTION_XY', forced=True)

        self.assertTrue(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        self.assertEqual(2, mock_sleep.call_count)
        acquire_calls = [
            mock.call('CLUSTER_A', 'ACTION_XY', lockm.CLUSTER_SCOPE)
        ]
        mock_acquire.assert_has_calls(acquire_calls * 3)
        mock_steal.assert_called_once_with('CLUSTER_A', 'ACTION_XY')

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "cluster_lock_acquire")
    @mock.patch.object(db_api, "cluster_lock_steal")
    def test_cluster_lock_acquire_steal_failed(self, mock_steal, mock_acquire,
                                               mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 2, enforce_type=True)
        mock_acquire.side_effect = ['ACTION_ABC', 'ACTION_ABC', 'ACTION_ABC']
        mock_steal.return_value = []

        res = lockm.cluster_lock_acquire(self.ctx, 'CLUSTER_A',
                                         'ACTION_XY', forced=True)

        self.assertFalse(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        self.assertEqual(2, mock_sleep.call_count)
        acquire_calls = [
            mock.call('CLUSTER_A', 'ACTION_XY', lockm.CLUSTER_SCOPE)
        ]
        mock_acquire.assert_has_calls(acquire_calls * 3)
        mock_steal.assert_called_once_with('CLUSTER_A', 'ACTION_XY')

    @mock.patch.object(db_api, "cluster_lock_release")
    def test_cluster_lock_release(self, mock_release):
        actual = lockm.cluster_lock_release('C', 'A', 'S')

        self.assertEqual(mock_release.return_value, actual)
        mock_release.assert_called_once_with('C', 'A', 'S')

    @mock.patch.object(db_api, "node_lock_acquire")
    def test_node_lock_acquire_already_owner(self, mock_acquire):
        mock_acquire.return_value = 'ACTION_XYZ'

        res = lockm.node_lock_acquire(self.ctx, 'NODE_A', 'ACTION_XYZ')

        self.assertTrue(res)
        mock_acquire.assert_called_once_with('NODE_A', 'ACTION_XYZ')

    @mock.patch.object(action.Action, 'load')
    @mock.patch.object(db_api, "node_lock_acquire")
    @mock.patch.object(db_api, "node_lock_steal")
    def test_node_lock_acquire_dead_owner(self, mock_steal, mock_acquire,
                                          mock_action_load):
        # self.stub_action.return_value = True
        # mock_acquire.side_effect = 'ACTION_ABC'
        # mock_steal.return_value = 'ACTION_XYZ'
        # act = mock.Mock()
        # mock_action_load.return_value = act

        # res = lockm.node_lock_acquire(self.ctx, 'NODE_A', 'ACTION_XYZ')

        # self.assertTrue(res)
        # mock_acquire.assert_called_once_with('NODE_A', 'ACTION_XYZ')
        # mock_steal.assert_called_once_with('NODE_A', 'ACTION_XYZ')
        # act.set_status.assert_called_once_with(
        #     result=action.Action.RES_ERROR,
        #     reason='Engine died when executing this action.'
        # )
        pass

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "node_lock_acquire")
    def test_node_lock_acquire_with_retry(self, mock_acquire, mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 5, enforce_type=True)
        mock_acquire.side_effect = ['ACTION_ABC', 'ACTION_ABC', 'ACTION_XYZ']

        res = lockm.node_lock_acquire(self.ctx, 'NODE_A', 'ACTION_XYZ')
        self.assertTrue(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        acquire_calls = [mock.call('NODE_A', 'ACTION_XYZ')]
        mock_acquire.assert_has_calls(acquire_calls * 3)

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "node_lock_acquire")
    def test_node_lock_acquire_max_retries(self, mock_acquire, mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 2, enforce_type=True)
        mock_acquire.side_effect = [
            'ACTION_ABC', 'ACTION_ABC', 'ACTION_ABC', 'ACTION_XYZ'
        ]

        res = lockm.node_lock_acquire(self.ctx, 'NODE_A', 'ACTION_XYZ')

        self.assertFalse(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        self.assertEqual(2, mock_sleep.call_count)
        acquire_calls = [mock.call('NODE_A', 'ACTION_XYZ')]
        mock_acquire.assert_has_calls(acquire_calls * 3)

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "node_lock_acquire")
    @mock.patch.object(db_api, "node_lock_steal")
    def test_node_lock_acquire_forced(self, mock_steal, mock_acquire,
                                      mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 2, enforce_type=True)
        mock_acquire.side_effect = ['ACTION_ABC', 'ACTION_ABC', 'ACTION_ABC']
        mock_steal.return_value = 'ACTION_XY'

        res = lockm.node_lock_acquire(self.ctx, 'NODE_A',
                                      'ACTION_XY', forced=True)

        self.assertTrue(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        self.assertEqual(2, mock_sleep.call_count)
        acquire_calls = [mock.call('NODE_A', 'ACTION_XY')]
        mock_acquire.assert_has_calls(acquire_calls * 3)
        mock_steal.assert_called_once_with('NODE_A', 'ACTION_XY')

    @mock.patch.object(scheduler, 'sleep')
    @mock.patch.object(db_api, "node_lock_acquire")
    @mock.patch.object(db_api, "node_lock_steal")
    def test_node_lock_acquire_steal_failed(self, mock_steal, mock_acquire,
                                            mock_sleep):
        cfg.CONF.set_override('lock_retry_times', 2, enforce_type=True)
        mock_acquire.side_effect = ['ACTION_ABC', 'ACTION_ABC', 'ACTION_ABC']
        mock_steal.return_value = None

        res = lockm.node_lock_acquire(self.ctx, 'NODE_A',
                                      'ACTION_XY', forced=True)

        self.assertFalse(res)
        sleep_calls = [mock.call(cfg.CONF.lock_retry_interval)]
        mock_sleep.assert_has_calls(sleep_calls * 2)
        self.assertEqual(2, mock_sleep.call_count)
        acquire_calls = [mock.call('NODE_A', 'ACTION_XY')]
        mock_acquire.assert_has_calls(acquire_calls * 3)
        mock_steal.assert_called_once_with('NODE_A', 'ACTION_XY')

    @mock.patch.object(db_api, "node_lock_release")
    def test_node_lock_release(self, mock_release):
        actual = lockm.node_lock_release('C', 'A')
        self.assertEqual(mock_release.return_value, actual)
        mock_release.assert_called_once_with('C', 'A')


class SenlinLockActionCheckTest(base.SenlinTestCase):

    def setUp(self):
        super(SenlinLockActionCheckTest, self).setUp()

        self.ctx = utils.dummy_context()

    @mock.patch.object(dispatcher, 'notify')
    @mock.patch.object(db_api, 'action_get')
    def test_action_on_live_engine(self, mock_action, mock_notify):
        mock_notify.return_value = True
        ret = mock.MagicMock()
        ret.owner = 'fake_engine_id'
        mock_action.return_value = ret
        self.assertIs(False,
                      lockm.action_on_dead_engine(self.ctx, 'fake_action'))
        mock_notify.assert_called_once_with('listening', 'fake_engine_id')

    @mock.patch.object(dispatcher, 'notify')
    @mock.patch.object(db_api, 'action_get')
    def test_action_on_dead_engine(self, mock_action, mock_notify):
        mock_notify.return_value = False
        ret = mock.MagicMock()
        ret.owner = 'fake_engine_id'
        mock_action.return_value = ret
        self.assertTrue(lockm.action_on_dead_engine(self.ctx, 'fake_action'))
        mock_notify.assert_called_once_with('listening', 'fake_engine_id')
