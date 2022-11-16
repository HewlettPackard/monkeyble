# Copyright 2022 Hewlett Packard Enterprise Development LP
import unittest
from unittest.mock import patch

from ansible.module_utils import basic

from plugins.module import monkeyble_module
from tests.units.utils.test_utils import set_module_args, exit_json, fail_json, AnsibleExitJson


class TestMonkeybleModule(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_argument_ok(self):
        with self.assertRaises(AnsibleExitJson) as result:
            set_module_args({
                'original_module_name': 'copy',
                'original_module_args': {
                    'datacenter': 'my_dc'
                },
                'task_name': "task1"
            })
            monkeyble_module.main()

    def test_result_with_changed_defined(self):
        with self.assertRaises(AnsibleExitJson) as result:
            set_module_args({
                'original_module_name': 'copy',
                'original_module_args': {
                    'datacenter': 'my_dc'
                },
                'task_name': "task1",
                'consider_changed': True
            })
            monkeyble_module.main()
        self.assertIn('changed', result.exception.args[0])
        self.assertEqual(True, result.exception.args[0]["changed"])

        with self.assertRaises(AnsibleExitJson) as result:
            set_module_args({
                'original_module_name': 'copy',
                'original_module_args': {
                    'datacenter': 'my_dc'
                },
                'task_name': "task1",
                'consider_changed': False
            })
            monkeyble_module.main()
        self.assertIn('changed', result.exception.args[0])
        self.assertEqual(False, result.exception.args[0]["changed"])

    def test_with_return_dict_defined(self):
        with self.assertRaises(AnsibleExitJson) as result:
            set_module_args({
                'original_module_name': 'copy',
                'original_module_args': {
                    'datacenter': 'my_dc'
                },
                'task_name': "task1",
                'result_dict': {'my_key': 'my_val'}

            })
            monkeyble_module.main()
        expected_dict = {'changed': False,
                         'my_key': 'my_val',
                         'msg': 'Monkeyble Mock module called. Original module: copy'}
        self.assertDictEqual(expected_dict, result.exception.args[0])
