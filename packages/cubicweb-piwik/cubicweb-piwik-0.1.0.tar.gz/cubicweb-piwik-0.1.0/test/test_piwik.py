# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-piwik automatic tests"""

from cubicweb.devtools.testlib import AutomaticWebTest, CubicWebTC
from logilab.common.testlib import TestCase, InnerTest, Tags

class AutomaticWebTest(AutomaticWebTest):
    '''provides `to_test_etypes` and/or `list_startup_views` implementation
    to limit test scope
    '''

    def to_test_etypes(self):
        '''only test views for entities of the returned types'''
        return set(('Blog', 'BlogEntry', 'MicroBlog', 'MicroBlogEntry', 'Card'))

    def test_one_each_config(self):
        self.auto_populate(1)
        self.config['piwik-idsite'] = 0
        self.config['piwik-domain'] = 'piwik.example.org'
        for rset in self.iter_automatic_rsets(limit=1):
            for testargs in self._test_everything_for(rset):
                if 'rdf' in testargs:
                    # XXX TODO don't skip this 
                    continue # skip it failing on sioc rdf output
                yield testargs

    def test_ten_each_config(self):
        self.auto_populate(10)
        self.config['piwik-idsite'] = 0
        self.config['piwik-domain'] = 'piwik.example.org'
        for rset in self.iter_automatic_rsets(limit=10):
            for testargs in self._test_everything_for(rset):
                if 'rdf' in testargs:
                    # XXX TODO don't skip this 
                    continue # skip it failing on sioc rdf output
                yield testargs

class PiwkiFooterTC(CubicWebTC):

    def test_piwik_code_is_present(self):
        self.config['piwik-idsite'] = 0
        self.config['piwik-domain'] = 'piwik.example.org'
        with self.admin_access.repo_cnx() as cnx:
            e = cnx.create_entity('BlogEntry', title=u'blah', content=u'blah')
            cnx.commit()
            e.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
        with self.new_access('anon').web_request() as req:
            entry = req.find('BlogEntry')
            #html = entry.view('primary')
            view = self.vreg['views'].select('primary', req, rset=entry)
            html = self.vreg['views'].main_template(req, 'main-template', rset=entry, view=view)
            self.assertIn('piwik', html)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
