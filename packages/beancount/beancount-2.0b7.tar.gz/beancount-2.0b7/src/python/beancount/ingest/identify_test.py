__author__ = "Martin Blais <blais@furius.ca>"

from os import path
import re
import textwrap
import unittest
from unittest import mock

from beancount.utils import test_utils
from beancount.ingest.importer import ImporterProtocol
from beancount.ingest import identify
from beancount.ingest import scripts_utils


class _TestImporter(ImporterProtocol):

    def __init__(self, filename):
        self.filename = filename

    def identify(self, file):
        return file.name == self.filename



class TestScriptIdentifyFunctions(test_utils.TestTempdirMixin, unittest.TestCase):

    def test_find_imports(self):
        file1 = path.join(self.tempdir, 'file1.test')
        file2 = path.join(self.tempdir, 'file2.test')
        file3 = path.join(self.tempdir, 'file3.test')
        for filename in [file1, file2, file3]:
            open(filename, 'w')

        imp1a = _TestImporter(file1)
        imp1b = _TestImporter(file1)
        imp2  = _TestImporter(file2)

        config = [imp1a, imp1b, imp2]
        imports = list(identify.find_imports(config, self.tempdir))
        self.assertEqual([(file1, [imp1a, imp1b]),
                          (file2, [imp2]),
                          (file3, [])],
                         imports)

    @mock.patch.object(identify, 'FILE_TOO_LARGE_THRESHOLD', 128)
    def test_find_imports__file_too_large(self):
        file1 = path.join(self.tempdir, 'file1.test')
        file2 = path.join(self.tempdir, 'file2.test')
        with open(file1, 'w') as f:
            f.write('*' * 16)
        with open(file2, 'w') as f:
            f.write('*' * 256)

        imp = mock.MagicMock()
        imp.identify = mock.MagicMock(return_value=True)

        imports = list(identify.find_imports([imp], self.tempdir))
        self.assertEqual([(file1, [imp])], imports)


class TestScriptIdentify(scripts_utils.TestScriptsBase):

    def test_identify(self):
        with test_utils.capture('stdout', 'stderr') as (stdout, stderr):
            test_utils.run_with_args(identify.main,
                                     [path.join(self.tempdir, 'test.import'),
                                      path.join(self.tempdir, 'Downloads')])
        output = stdout.getvalue()
        self.assertTrue(re.match(textwrap.dedent("""\
            .*/Downloads/ofxdownload.ofx

              mybank-checking-ofx


            .*/Downloads/Subdir/bank.csv

              mybank-credit-csv


            .*/Downloads/Subdir/readme.txt


            $"""), output))
