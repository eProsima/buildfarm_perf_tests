# Copyright 2018 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest

from launch import LaunchDescription, LaunchService
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessIO
from launch_ros.actions import Node
from launch_testing import ActiveIoHandler


def _create_node(comm='ROS2', topic='Array1k', max_runtime=10, log_file=None):
    return Node(
        package='performance_test', node_executable='perf_test', output='log',
        arguments=[
            '-c', comm, '-t', topic, '--max_runtime', str(max_runtime)
        ] + (['-l', log_file] if log_file else []),
    )


class TestRMWPerformance(unittest.TestCase):

    def test_perforamnce(self):
        proc_output = ActiveIoHandler()

        node = _create_node()
        ld = LaunchDescription([
            node,
            RegisterEventHandler(
                OnProcessIO(
                    on_stdout=proc_output.append,
                ),
            ),
        ])
        ls = LaunchService()
        ls.include_launch_description(ld)
        assert 0 == ls.run()

        text_lines = [l for t in proc_output for l in t.text.decode().splitlines()]
        line_start = text_lines.index('---EXPERIMENT-START---')
        line_end = text_lines.index('Maximum runtime reached. Exiting.')
        if line_end < 0:
            line_end = len(text_lines)
        assert line_start >= 0

        print('\n'.join(text_lines[:line_start]))
        print('PWD: %s' % (os.environ['PWD']))
        print('CWD: %s' % (os.getcwd()))

        csv_path = os.path.join(os.environ['PWD'], 'performance_text_results.csv')

        with open(csv_path, 'w') as f:
            for line in text_lines[line_start + 1:line_end]:
                f.write(line)
                f.write('\n')