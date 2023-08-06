"Card unit test"
import re

from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import CubicWebTC, MAILBOX
from cubicweb.ext.rest import rest_publish


class CardTests(CubicWebTC):

    def test_notifications(self):
        with self.admin_access.client_cnx() as cnx:
            cw_card = cnx.create_entity('Card', title=u'sample card', synopsis=u'this is a sample card')
            self.assertEqual(len(MAILBOX), 0)
            cnx.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(re.sub('#\d+', '#EID', MAILBOX[0].subject),
                          'New Card #EID (admin)')


class RestTC(CubicWebTC):
    def context(self, cnx):
        return cnx.execute('CWUser X WHERE X login "admin"').get_entity(0, 0)

    def test_card_role_create(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertEqual(rest_publish(self.context(cnx), ':card:`index`'),
                              '<p><a class="doesnotexist reference" href="http://testing.fr/cubicweb/card/index">index</a></p>\n')

    def test_card_role_create_subpage(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertEqual(rest_publish(self.context(cnx), ':card:`foo/bar`'),
                             '<p><a class="doesnotexist reference" href="http://testing.fr/cubicweb/card/foo/bar">foo/bar</a></p>\n')

    def test_card_role_link(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.create_entity('Card', wikiid=u'index', title=u'Site index page', synopsis=u'yo')
            self.assertEqual(rest_publish(self.context(cnx), ':card:`index`'),
                             '<p><a class="reference" href="http://testing.fr/cubicweb/card/index">index</a></p>\n')


if __name__ == '__main__':
    unittest_main()
