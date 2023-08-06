# -*- coding: utf-8 -*-
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

"""cubicweb-piwik views/forms/actions/components for web ui"""

from logilab.common.decorators import monkeypatch
from cubicweb.web.views.basetemplates import HTMLPageFooter

orig_footer_content = HTMLPageFooter.footer_content


@monkeypatch(HTMLPageFooter)
def footer_content(self):
    orig_footer_content(self)
    config = self._cw.vreg.config
    idsite = config.get('piwik-idsite')
    domain = config.get('piwik-domain')
    if idsite is None or domain is None:
        return None
    piwik_code = u'''
<!-- Piwik -->
<script type="text/javascript">
  var _paq = _paq || [];
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {{
    var u="//{domain}/";
    _paq.push(['setTrackerUrl', u+'piwik.php']);
    _paq.push(['setSiteId', {idsite}]);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.type='text/javascript'; g.async=true;
    g.defer=true; g.src=u+'piwik.js'; s.parentNode.insertBefore(g,s);
    }})();
</script>
<noscript>
  <p>
    <img src="//{domain}/piwik.php?idsite={idsite}" style="border:0;" alt="" />
  </p>
</noscript>
<!-- End Piwik Code -->
    '''
    self.w(piwik_code.format(idsite=idsite,
                             domain=domain))
