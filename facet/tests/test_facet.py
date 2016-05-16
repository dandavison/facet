import os
import shutil
import subprocess
import tempfile
from unittest import TestCase


class _TestFacetMixin:

    def setUp(self):
        self.facet_executable = (subprocess.check_output(['which', 'facet'])
                                 .strip())
        self.env = {
            'FACET_DIRECTORY': tempfile.mkdtemp(),
        }

        facets = [
            {
                'name': 'test-facet-1',
            },
            {
                'name': 'test-facet-2',
            },
        ]
        self._create_environment(facets=facets)

    def tearDown(self):
        shutil.rmtree(self.env['FACET_DIRECTORY'])

    def _create_environment(self, facets):
        os.mkdir('%s/facets' % self.env['FACET_DIRECTORY'])
        for facet in facets:
            self._create(facet['name'])

    def _create(self, name):
        return self._check_output(['create', name], input=b'\n\n\n')

    def _check_output(self, args, **kwargs):
        return (subprocess.check_output([self.facet_executable] + args,
                                        env=self.env,
                                        **kwargs)
                .decode('utf-8')
                .strip())


class TestFacet(_TestFacetMixin, TestCase):

    def test_ls(self):
        self.assertEqual(
            self._check_output(['ls']).split(),
            ['test-facet-1',
             'test-facet-2']
        )

    def test_workon_and_current(self):
        self._check_output(['workon', 'test-facet-1'])
        self.assertEqual(
            self._check_output(['current']),
            'test-facet-1',
        )
        self._check_output(['workon', 'test-facet-2'])
        self.assertEqual(
            self._check_output(['current']),
            'test-facet-2',
        )
