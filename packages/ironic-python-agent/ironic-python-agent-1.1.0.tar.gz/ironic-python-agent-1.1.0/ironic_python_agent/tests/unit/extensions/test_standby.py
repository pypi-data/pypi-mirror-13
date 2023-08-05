# Copyright 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import mock
from oslo_concurrency import processutils
from oslotest import base as test_base
import six

from ironic_python_agent import errors
from ironic_python_agent.extensions import standby

if six.PY2:
    OPEN_FUNCTION_NAME = '__builtin__.open'
else:
    OPEN_FUNCTION_NAME = 'builtins.open'


def _build_fake_image_info():
    return {
        'id': 'fake_id',
        'urls': [
            'http://example.org',
        ],
        'checksum': 'abc123'
    }


class TestStandbyExtension(test_base.BaseTestCase):
    def setUp(self):
        super(TestStandbyExtension, self).setUp()
        self.agent_extension = standby.StandbyExtension()

    def test_validate_image_info_success(self):
        standby._validate_image_info(None, _build_fake_image_info())

    def test_validate_image_info_missing_field(self):
        for field in ['id', 'urls', 'checksum']:
            invalid_info = _build_fake_image_info()
            del invalid_info[field]

            self.assertRaises(errors.InvalidCommandParamsError,
                              standby._validate_image_info,
                              invalid_info)

    def test_validate_image_info_invalid_urls(self):
        invalid_info = _build_fake_image_info()
        invalid_info['urls'] = 'this_is_not_a_list'

        self.assertRaises(errors.InvalidCommandParamsError,
                          standby._validate_image_info,
                          invalid_info)

    def test_validate_image_info_empty_urls(self):
        invalid_info = _build_fake_image_info()
        invalid_info['urls'] = []

        self.assertRaises(errors.InvalidCommandParamsError,
                          standby._validate_image_info,
                          invalid_info)

    def test_validate_image_info_invalid_checksum(self):
        invalid_info = _build_fake_image_info()
        invalid_info['checksum'] = {'not': 'a string'}

        self.assertRaises(errors.InvalidCommandParamsError,
                          standby._validate_image_info,
                          invalid_info)

    def test_validate_image_info_empty_checksum(self):
        invalid_info = _build_fake_image_info()
        invalid_info['checksum'] = ''

        self.assertRaises(errors.InvalidCommandParamsError,
                          standby._validate_image_info,
                          invalid_info)

    def test_cache_image_invalid_image_list(self):
        self.assertRaises(errors.InvalidCommandParamsError,
                          self.agent_extension.cache_image,
                          image_info={'foo': 'bar'})

    def test_image_location(self):
        image_info = _build_fake_image_info()
        location = standby._image_location(image_info)
        self.assertEqual(location, '/tmp/fake_id')

    @mock.patch(OPEN_FUNCTION_NAME, autospec=True)
    @mock.patch('ironic_python_agent.utils.execute', autospec=True)
    def test_write_image(self, execute_mock, open_mock):
        image_info = _build_fake_image_info()
        device = '/dev/sda'
        location = standby._image_location(image_info)
        script = standby._path_to_script('shell/write_image.sh')
        command = ['/bin/bash', script, location, device]
        execute_mock.return_value = ('', '')

        standby._write_image(image_info, device)
        execute_mock.assert_called_once_with(*command, check_exit_code=[0])

        execute_mock.reset_mock()
        execute_mock.return_value = ('', '')
        execute_mock.side_effect = processutils.ProcessExecutionError

        self.assertRaises(errors.ImageWriteError,
                          standby._write_image,
                          image_info,
                          device)

        execute_mock.assert_called_once_with(*command, check_exit_code=[0])

    def test_configdrive_is_url(self):
        self.assertTrue(standby._configdrive_is_url('http://some/url'))
        self.assertTrue(standby._configdrive_is_url('https://some/url'))
        self.assertFalse(standby._configdrive_is_url('ftp://some/url'))
        self.assertFalse(standby._configdrive_is_url('binary-blob'))

    @mock.patch.object(standby, '_write_configdrive_to_file')
    @mock.patch('requests.get', autospec=True)
    def test_download_configdrive_to_file(self, get_mock, write_mock):
        url = 'http://swift/configdrive'
        get_mock.return_value.content = 'data'
        standby._download_configdrive_to_file(url, 'filename')
        get_mock.assert_called_once_with(url)
        write_mock.assert_called_once_with('data', 'filename')

    @mock.patch('gzip.GzipFile', autospec=True)
    @mock.patch(OPEN_FUNCTION_NAME, autospec=True)
    @mock.patch('base64.b64decode', autospec=True)
    def test_write_configdrive_to_file(self, b64_mock, open_mock, gzip_mock):
        open_mock.return_value.__enter__ = lambda s: s
        open_mock.return_value.__exit__ = mock.Mock()
        write_mock = open_mock.return_value.write
        gzip_read_mock = gzip_mock.return_value.read
        gzip_read_mock.return_value = 'ungzipped'
        b64_mock.return_value = 'configdrive_data'
        filename = standby._configdrive_location()

        standby._write_configdrive_to_file('b64data', filename)
        open_mock.assert_called_once_with(filename, 'wb')
        gzip_read_mock.assert_called_once_with()
        write_mock.assert_called_once_with('ungzipped')

    @mock.patch('os.stat', autospec=True)
    @mock.patch(('ironic_python_agent.extensions.standby.'
                 '_write_configdrive_to_file'),
                autospec=True)
    @mock.patch(OPEN_FUNCTION_NAME, autospec=True)
    @mock.patch('ironic_python_agent.utils.execute', autospec=True)
    def test_write_configdrive_to_partition(self, execute_mock, open_mock,
                                            configdrive_mock, stat_mock):
        device = '/dev/sda'
        configdrive = standby._configdrive_location()
        script = standby._path_to_script('shell/copy_configdrive_to_disk.sh')
        command = ['/bin/bash', script, configdrive, device]
        execute_mock.return_value = ('', '')
        stat_mock.return_value.st_size = 5

        standby._write_configdrive_to_partition(configdrive, device)
        execute_mock.assert_called_once_with(*command, check_exit_code=[0])

        execute_mock.reset_mock()
        execute_mock.return_value = ('', '')
        execute_mock.side_effect = processutils.ProcessExecutionError

        self.assertRaises(errors.ConfigDriveWriteError,
                          standby._write_configdrive_to_partition,
                          configdrive,
                          device)

        execute_mock.assert_called_once_with(*command, check_exit_code=[0])

    @mock.patch('os.stat', autospec=True)
    @mock.patch(('ironic_python_agent.extensions.standby.'
                 '_write_configdrive_to_file'),
                autospec=True)
    @mock.patch(OPEN_FUNCTION_NAME, autospec=True)
    @mock.patch('ironic_python_agent.utils.execute', autospec=True)
    def test_write_configdrive_too_large(self, execute_mock, open_mock,
                                         configdrive_mock, stat_mock):
        device = '/dev/sda'
        configdrive = standby._configdrive_location()
        stat_mock.return_value.st_size = 65 * 1024 * 1024

        self.assertRaises(errors.ConfigDriveTooLargeError,
                          standby._write_configdrive_to_partition,
                          configdrive,
                          device)

    @mock.patch('hashlib.md5')
    @mock.patch(OPEN_FUNCTION_NAME)
    @mock.patch('requests.get')
    def test_download_image(self, requests_mock, open_mock, md5_mock):
        image_info = _build_fake_image_info()
        response = requests_mock.return_value
        response.status_code = 200
        response.iter_content.return_value = ['some', 'content']
        file_mock = mock.Mock()
        open_mock.return_value.__enter__.return_value = file_mock
        file_mock.read.return_value = None
        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.return_value = image_info['checksum']

        standby._download_image(image_info)
        requests_mock.assert_called_once_with(image_info['urls'][0],
                                              stream=True, proxies={})
        write = file_mock.write
        write.assert_any_call('some')
        write.assert_any_call('content')
        self.assertEqual(write.call_count, 2)

    @mock.patch('hashlib.md5')
    @mock.patch(OPEN_FUNCTION_NAME)
    @mock.patch('requests.get')
    @mock.patch.dict(os.environ, {})
    def test_download_image_proxy(
            self, requests_mock, open_mock, md5_mock):
        image_info = _build_fake_image_info()
        proxies = {'http': 'http://a.b.com',
                   'https': 'https://secure.a.b.com'}
        no_proxy = '.example.org,.b.com'
        image_info['proxies'] = proxies
        image_info['no_proxy'] = no_proxy
        response = requests_mock.return_value
        response.status_code = 200
        response.iter_content.return_value = ['some', 'content']
        file_mock = mock.Mock()
        open_mock.return_value.__enter__.return_value = file_mock
        file_mock.read.return_value = None
        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.return_value = image_info['checksum']

        standby._download_image(image_info)
        self.assertEqual(no_proxy, os.environ['no_proxy'])
        requests_mock.assert_called_once_with(image_info['urls'][0],
                                              stream=True, proxies=proxies)
        write = file_mock.write
        write.assert_any_call('some')
        write.assert_any_call('content')
        self.assertEqual(write.call_count, 2)

    @mock.patch('requests.get', autospec=True)
    def test_download_image_bad_status(self, requests_mock):
        image_info = _build_fake_image_info()
        response = requests_mock.return_value
        response.status_code = 404
        self.assertRaises(errors.ImageDownloadError,
                          standby._download_image,
                          image_info)

    @mock.patch('hashlib.md5', autospec=True)
    @mock.patch(OPEN_FUNCTION_NAME, autospec=True)
    @mock.patch('requests.get', autospec=True)
    def test_download_image_verify_fails(self, requests_mock, open_mock,
                                         md5_mock):
        image_info = _build_fake_image_info()
        response = requests_mock.return_value
        response.status_code = 200
        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.return_value = 'invalid-checksum'
        self.assertRaises(errors.ImageChecksumError,
                          standby._download_image,
                          image_info)

    def test_verify_image_success(self):
        image_info = _build_fake_image_info()
        image_location = '/foo/bar'
        checksum = image_info['checksum']
        standby._verify_image(image_info, image_location, checksum)

    def test_verify_image_failure(self):
        image_info = _build_fake_image_info()
        image_location = '/foo/bar'
        checksum = 'invalid-checksum'
        self.assertRaises(errors.ImageChecksumError,
                          standby._verify_image,
                          image_info, image_location, checksum)

    @mock.patch('ironic_python_agent.hardware.dispatch_to_managers',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._write_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._download_image',
                autospec=True)
    def test_cache_image(self, download_mock, write_mock,
                         dispatch_mock):
        image_info = _build_fake_image_info()
        download_mock.return_value = None
        write_mock.return_value = None
        dispatch_mock.return_value = 'manager'
        async_result = self.agent_extension.cache_image(image_info=image_info)
        async_result.join()
        download_mock.assert_called_once_with(image_info)
        write_mock.assert_called_once_with(image_info, 'manager')
        dispatch_mock.assert_called_once_with('get_os_install_device')
        self.assertEqual(self.agent_extension.cached_image_id,
                         image_info['id'])
        self.assertEqual('SUCCEEDED', async_result.command_status)
        self.assertTrue('result' in async_result.command_result.keys())
        cmd_result = ('cache_image: image ({0}) cached to device {1}'
                      ).format(image_info['id'], 'manager')
        self.assertEqual(cmd_result, async_result.command_result['result'])

    @mock.patch('ironic_python_agent.hardware.dispatch_to_managers',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._write_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._download_image',
                autospec=True)
    def test_cache_image_force(self, download_mock, write_mock,
                               dispatch_mock):
        image_info = _build_fake_image_info()
        self.agent_extension.cached_image_id = image_info['id']
        download_mock.return_value = None
        write_mock.return_value = None
        dispatch_mock.return_value = 'manager'
        async_result = self.agent_extension.cache_image(
            image_info=image_info, force=True
        )
        async_result.join()
        download_mock.assert_called_once_with(image_info)
        write_mock.assert_called_once_with(image_info, 'manager')
        dispatch_mock.assert_called_once_with('get_os_install_device')
        self.assertEqual(self.agent_extension.cached_image_id,
                         image_info['id'])
        self.assertEqual('SUCCEEDED', async_result.command_status)
        self.assertTrue('result' in async_result.command_result.keys())
        cmd_result = ('cache_image: image ({0}) cached to device {1}'
                      ).format(image_info['id'], 'manager')
        self.assertEqual(cmd_result, async_result.command_result['result'])

    @mock.patch('ironic_python_agent.hardware.dispatch_to_managers',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._write_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._download_image',
                autospec=True)
    def test_cache_image_cached(self, download_mock, write_mock,
                                dispatch_mock):
        image_info = _build_fake_image_info()
        self.agent_extension.cached_image_id = image_info['id']
        download_mock.return_value = None
        write_mock.return_value = None
        dispatch_mock.return_value = 'manager'
        async_result = self.agent_extension.cache_image(image_info=image_info)
        async_result.join()
        self.assertFalse(download_mock.called)
        self.assertFalse(write_mock.called)
        dispatch_mock.assert_called_once_with('get_os_install_device')
        self.assertEqual(self.agent_extension.cached_image_id,
                         image_info['id'])
        self.assertEqual('SUCCEEDED', async_result.command_status)
        self.assertTrue('result' in async_result.command_result.keys())
        cmd_result = ('cache_image: image ({0}) already present on device {1}'
                      ).format(image_info['id'], 'manager')
        self.assertEqual(cmd_result, async_result.command_result['result'])

    @mock.patch(('ironic_python_agent.extensions.standby.'
                 '_write_configdrive_to_partition'),
                autospec=True)
    @mock.patch('ironic_python_agent.hardware.dispatch_to_managers',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._write_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._download_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._configdrive_location',
                autospec=True)
    def test_prepare_image(self,
                           location_mock,
                           download_mock,
                           write_mock,
                           dispatch_mock,
                           configdrive_copy_mock):
        image_info = _build_fake_image_info()
        location_mock.return_value = '/tmp/configdrive'
        download_mock.return_value = None
        write_mock.return_value = None
        dispatch_mock.return_value = 'manager'
        configdrive_copy_mock.return_value = None

        async_result = self.agent_extension.prepare_image(
            image_info=image_info,
            configdrive='configdrive_data'
        )
        async_result.join()

        download_mock.assert_called_once_with(image_info)
        write_mock.assert_called_once_with(image_info, 'manager')
        dispatch_mock.assert_called_once_with('get_os_install_device')
        configdrive_copy_mock.assert_called_once_with('configdrive_data',
                                                      'manager')

        self.assertEqual('SUCCEEDED', async_result.command_status)
        self.assertTrue('result' in async_result.command_result.keys())
        cmd_result = ('prepare_image: image ({0}) written to device {1}'
                      ).format(image_info['id'], 'manager')
        self.assertEqual(cmd_result, async_result.command_result['result'])

        download_mock.reset_mock()
        write_mock.reset_mock()
        configdrive_copy_mock.reset_mock()
        # image is now cached, make sure download/write doesn't happen
        async_result = self.agent_extension.prepare_image(
            image_info=image_info,
            configdrive='configdrive_data'
        )
        async_result.join()

        self.assertEqual(download_mock.call_count, 0)
        self.assertEqual(write_mock.call_count, 0)
        configdrive_copy_mock.assert_called_once_with('configdrive_data',
                                                      'manager')

        self.assertEqual('SUCCEEDED', async_result.command_status)
        self.assertTrue('result' in async_result.command_result.keys())
        cmd_result = ('prepare_image: image ({0}) written to device {1}'
                      ).format(image_info['id'], 'manager')
        self.assertEqual(cmd_result, async_result.command_result['result'])

    @mock.patch(('ironic_python_agent.extensions.standby.'
                 '_write_configdrive_to_partition'),
                autospec=True)
    @mock.patch('ironic_python_agent.hardware.dispatch_to_managers',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._write_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._download_image',
                autospec=True)
    def test_prepare_image_no_configdrive(self,
                                          download_mock,
                                          write_mock,
                                          dispatch_mock,
                                          configdrive_copy_mock):
        image_info = _build_fake_image_info()
        download_mock.return_value = None
        write_mock.return_value = None
        dispatch_mock.return_value = 'manager'
        configdrive_copy_mock.return_value = None

        async_result = self.agent_extension.prepare_image(
            image_info=image_info,
            configdrive=None
        )
        async_result.join()

        download_mock.assert_called_once_with(image_info)
        write_mock.assert_called_once_with(image_info, 'manager')
        dispatch_mock.assert_called_once_with('get_os_install_device')

        self.assertEqual(configdrive_copy_mock.call_count, 0)
        self.assertEqual('SUCCEEDED', async_result.command_status)
        self.assertTrue('result' in async_result.command_result.keys())
        cmd_result = ('prepare_image: image ({0}) written to device {1}'
                      ).format(image_info['id'], 'manager')
        self.assertEqual(cmd_result, async_result.command_result['result'])

    @mock.patch(('ironic_python_agent.extensions.standby.'
                 '_write_configdrive_to_partition'),
                autospec=True)
    @mock.patch('ironic_python_agent.hardware.dispatch_to_managers',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby.StandbyExtension'
                '._cache_and_write_image', autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby.StandbyExtension'
                '._stream_raw_image_onto_device', autospec=True)
    def _test_prepare_image_raw(self, image_info, stream_mock,
                                cache_write_mock, dispatch_mock,
                                configdrive_copy_mock):
        dispatch_mock.return_value = '/dev/foo'
        configdrive_copy_mock.return_value = None

        async_result = self.agent_extension.prepare_image(
            image_info=image_info,
            configdrive=None
        )
        async_result.join()

        dispatch_mock.assert_called_once_with('get_os_install_device')
        self.assertFalse(configdrive_copy_mock.called)

        # Assert we've streamed the image or not
        if image_info['stream_raw_images']:
            stream_mock.assert_called_once_with(mock.ANY, image_info,
                                                '/dev/foo')
            self.assertFalse(cache_write_mock.called)
        else:
            cache_write_mock.assert_called_once_with(mock.ANY, image_info,
                                                     '/dev/foo')
            self.assertFalse(stream_mock.called)

    def test_prepare_image_raw_stream_true(self):
        image_info = _build_fake_image_info()
        image_info['disk_format'] = 'raw'
        image_info['stream_raw_images'] = True
        self._test_prepare_image_raw(image_info)

    def test_prepare_image_raw_and_stream_false(self):
        image_info = _build_fake_image_info()
        image_info['disk_format'] = 'raw'
        image_info['stream_raw_images'] = False
        self._test_prepare_image_raw(image_info)

    @mock.patch('ironic_python_agent.utils.execute', autospec=True)
    def test_run_image(self, execute_mock):
        script = standby._path_to_script('shell/shutdown.sh')
        command = ['/bin/bash', script, '-r']
        execute_mock.return_value = ('', '')

        success_result = self.agent_extension.run_image()
        success_result.join()

        execute_mock.assert_called_once_with(*command, check_exit_code=[0])
        self.assertEqual('SUCCEEDED', success_result.command_status)

        execute_mock.reset_mock()
        execute_mock.return_value = ('', '')
        execute_mock.side_effect = processutils.ProcessExecutionError

        failed_result = self.agent_extension.run_image()
        failed_result.join()

        execute_mock.assert_called_once_with(*command, check_exit_code=[0])
        self.assertEqual('FAILED', failed_result.command_status)

    def test_path_to_script(self):
        script = standby._path_to_script('shell/reboot.sh')
        self.assertTrue(script.endswith('extensions/../shell/reboot.sh'))

    @mock.patch('ironic_python_agent.utils.execute', autospec=True)
    def test_power_off(self, execute_mock):
        script = standby._path_to_script('shell/shutdown.sh')
        command = ['/bin/bash', script, '-h']
        execute_mock.return_value = ('', '')

        success_result = self.agent_extension.power_off()
        success_result.join()

        execute_mock.assert_called_once_with(*command, check_exit_code=[0])
        self.assertEqual('SUCCEEDED', success_result.command_status)

        execute_mock.reset_mock()
        execute_mock.return_value = ('', '')
        execute_mock.side_effect = processutils.ProcessExecutionError

        failed_result = self.agent_extension.power_off()
        failed_result.join()

        execute_mock.assert_called_once_with(*command, check_exit_code=[0])
        self.assertEqual('FAILED', failed_result.command_status)

    @mock.patch('ironic_python_agent.extensions.standby._write_image',
                autospec=True)
    @mock.patch('ironic_python_agent.extensions.standby._download_image',
                autospec=True)
    def test_cache_and_write_image(self, download_mock, write_mock):
        image_info = _build_fake_image_info()
        device = '/dev/foo'
        self.agent_extension._cache_and_write_image(image_info, device)
        download_mock.assert_called_once_with(image_info)
        write_mock.assert_called_once_with(image_info, device)

    @mock.patch('hashlib.md5')
    @mock.patch(OPEN_FUNCTION_NAME)
    @mock.patch('requests.get')
    def test_stream_raw_image_onto_device(self, requests_mock, open_mock,
                                          md5_mock):
        image_info = _build_fake_image_info()
        response = requests_mock.return_value
        response.status_code = 200
        response.iter_content.return_value = ['some', 'content']
        file_mock = mock.Mock()
        open_mock.return_value.__enter__.return_value = file_mock
        file_mock.read.return_value = None
        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.return_value = image_info['checksum']

        self.agent_extension._stream_raw_image_onto_device(image_info,
                                                           '/dev/foo')
        requests_mock.assert_called_once_with(image_info['urls'][0],
                                              stream=True, proxies={})
        expected_calls = [mock.call('some'), mock.call('content')]
        file_mock.write.assert_has_calls(expected_calls)

    @mock.patch('hashlib.md5')
    @mock.patch(OPEN_FUNCTION_NAME)
    @mock.patch('requests.get')
    def test_stream_raw_image_onto_device_write_error(self, requests_mock,
                                                      open_mock, md5_mock):
        image_info = _build_fake_image_info()
        response = requests_mock.return_value
        response.status_code = 200
        response.iter_content.return_value = ['some', 'content']
        file_mock = mock.Mock()
        open_mock.return_value.__enter__.return_value = file_mock
        file_mock.write.side_effect = Exception('Surprise!!!1!')
        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.return_value = image_info['checksum']

        self.assertRaises(errors.ImageDownloadError,
                          self.agent_extension._stream_raw_image_onto_device,
                          image_info, '/dev/foo')
        requests_mock.assert_called_once_with(image_info['urls'][0],
                                              stream=True, proxies={})
        # Assert write was only called once and failed!
        file_mock.write.assert_called_once_with('some')


class TestImageDownload(test_base.BaseTestCase):

    @mock.patch('hashlib.md5', autospec=True)
    @mock.patch('requests.get', autospec=True)
    def test_download_image(self, requests_mock, md5_mock):
        content = ['SpongeBob', 'SquarePants']
        response = requests_mock.return_value
        response.status_code = 200
        response.iter_content.return_value = content

        image_info = _build_fake_image_info()
        md5_mock.return_value.hexdigest.return_value = image_info['checksum']
        image_download = standby.ImageDownload(image_info)

        self.assertEqual(content, list(image_download))
        requests_mock.assert_called_once_with(image_info['urls'][0],
                                              stream=True, proxies={})
        self.assertEqual(image_info['checksum'], image_download.md5sum())
