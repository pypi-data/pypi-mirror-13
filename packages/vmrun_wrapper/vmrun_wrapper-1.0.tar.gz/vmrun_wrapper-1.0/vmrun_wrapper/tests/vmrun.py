import unittest
import os
from vmrun_wrapper.vmrun import cli


class TestCheckers(unittest.TestCase):

    def setUp(self):
        self.cli = cli()

        dir_slash = 'tmp/tests/vm/vm.vmwarevm/'
        os.makedirs(dir_slash)
        f = open(os.path.join(dir_slash, 'vm.vmx'))
        f.write()
        f.close()

        dir_valid = 'tmp/tests/vm/vm1.vmwarevm'
        os.makedirs(dir_valid)
        f = open(os.join(dir, 'vm1.vmx'))
        f.write()
        f.close()

        dir_invalid = 'tmp/tests/vm/vm.invalid'
        os.makedirs(dir)

    def test_remove_slash_vmx_path_is_valid(self):
        self.assertEqual(self.cli.vmx_path_is_valid(dir_slash), True)

    def test_with_vmwarevm_extension_vmx_path_is_valid(self):
        self.assertEqual(self.cli.vmx_path_is_valid(dir_valid), True)

    def test_invalid_extension_vmx_path_is_valid(self):
        self.assertEqual(self.cli.vmx_path_is_valid(dir_invalid), False)

if __name__ == "__main__":
    unittest.main()
