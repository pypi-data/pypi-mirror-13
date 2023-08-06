# coding: utf-8

import sys
from io import StringIO

from cubicweb.devtools import testlib
from cubicweb.devtools import PostgresApptestConfiguration, startpgcluster, stoppgcluster
from cubicweb.cwconfig import CubicWebConfiguration

from cubes.skos import ccplugin


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class ImportSkosDataCommandTC(testlib.CubicWebTC):
    configcls = PostgresApptestConfiguration

    def setup_database(self):
        super(ImportSkosDataCommandTC, self).setup_database()
        self.orig_config_for = CubicWebConfiguration.config_for
        config_for = lambda appid: self.config
        CubicWebConfiguration.config_for = staticmethod(config_for)

    def tearDown(self):
        CubicWebConfiguration.config_for = self.orig_config_for
        super(ImportSkosDataCommandTC, self).tearDown()

    def run(self, *args):
        cmd = [self.appid, self.datapath('skos.rdf')] + list(args)
        sys.stdout = StringIO()
        try:
            ccplugin.ImportSkosData(None).main_run(cmd)
        finally:
            sys.stdout = sys.__stdout__

    def _test_base(self):
        with self.admin_access.repo_cnx() as cnx:
            scheme = cnx.find('ConceptScheme').one()
            self.assertEqual(scheme.title, u"Thésaurus de test")
            concept = cnx.find('Concept', cwuri='http://mystery.com/ark:/kra/543').one()
            self.assertEqual(concept.labels, {u'fr': u'économie'})

    def test_nooption(self):
        self.run()
        self._test_base()

    def test_nohook(self):
        self.run('--cw-store', 'nohook')
        self._test_base()

    def test_massive(self):
        self.run('-s', 'massive')
        self._test_base()
