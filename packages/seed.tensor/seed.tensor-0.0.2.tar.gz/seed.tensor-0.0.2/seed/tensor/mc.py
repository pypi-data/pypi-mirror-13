"""
.. module:: mc
   :platform: Unix
   :synopsis: A source module for Mission Control site checks

.. moduleauthor:: Colin Alston <colin@praekelt.com>
"""
import time
import json

from zope.interface import implements

from twisted.internet import defer, reactor
from twisted.python import log
from twisted.enterprise import adbapi

from tensor.utils import HTTPRequest, Timeout, BodyReceiver
from tensor.interfaces import ITensorSource
from tensor.objects import Source


class MCSites(Source):
    implements(ITensorSource)

    def __init__(self, *a, **kw):
        super(MCSites, self).__init__(*a, **kw)

        self.db_host = self.config['db_host']
        self.db_name = self.config['db_name']
        self.db_user = self.config.get('db_username', 'postgres')
        self.db_pass = self.config.get('db_password', None)

    @defer.inlineCallbacks
    def _get_sites(self):
        "Retrieve sites from Mission Control"

        p = adbapi.ConnectionPool('psycopg2',
            database=self.db_name,
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass
        )

        q = yield p.runQuery(
            'SELECT p.id, p.country, a.name, p.frontend_custom_domain, '
            'p.marathon_health_check_path FROM unicoremc_project p, '
            'unicoremc_apptype a WHERE a.id=p.application_type_id AND '
            'p.marathon_instances>0;'
        )

        defer.returnValue([
            ('/%s-%s-%s' % (name, count.lower(), id), dom.split()[0], hc)
            for id, count, name, dom, hc in q
        ])

    @defer.inlineCallbacks
    def _get_response(self, request, id, domain):
        if request.length:
            d = defer.Deferred()
            request.deliverBody(BodyReceiver(d))
            b = yield d
            body = b.read()
        else:
            body = None

        s = False

        if request.code == 200:
            if body == '{}':
                # Using old style check
                r = "Site okay"
                s = True
            else:
                result = json.loads(body)
                if result.get('id') == id:
                    s = True
                    r = "%s %s" % (result['id'], result['version'])
                else:
                    r = "Invalid content %s != %s" % (id, result.get('id'))
        else:
            r = "Invalid response code %s" % request.code

        self.queueBack(self.createEvent(s and 'ok' or 'critical', r, 
            int(s) * 100, prefix="%s.uptime" % id.strip('/')))

    @defer.inlineCallbacks
    def _site_health(self, domain, path, id):
        url = "http://%s/%s" % (domain, path.lstrip('/'))

        request = HTTPRequest(timeout=30)

        request.response = lambda r: self._get_response(r, id, domain)

        try:
            yield request.getBody(url)
        except Exception, e:
            self.queueBack(self.createEvent('critical',
                'Connection error %s' % e, 0,
                prefix="%s.uptime" % id.strip('/')))

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    @defer.inlineCallbacks
    def get(self):
        try:
            sites = yield self._get_sites()
        except Exception, e:
            defer.returnValue(self.createEvent('critical',
                'Mission control DB unreachable %s' % e, 0, prefix='mc.uptime'))

        for blk in self.chunks(sites, 10):
            deferreds = [
                self._site_health(domain, hc, id) for id, domain, hc in blk]

            # Wait for this block
            results = yield defer.DeferredList(deferreds)

        defer.returnValue(self.createEvent('ok',
                'Mission control DB', 0, prefix='mc.uptime'))
