#!/usr/bin/env python

"""
version 0.2 2-6-2016
url to py obj converter

Heads up: Horrible code.

Author: Sander Ferdinand' <sanderf [AT] cedsys [DOT] nl>
License: MIT
"""
import cgi
import urllib2


class ParseUrl():
    def __init__(self, uri):
        self.scheme = ''
        self.subdomain = ''
        self.port = None
        self.auth = self.get_auth(uri)
        self.fulluri = self.get_fulluri(uri)
        self.base = self.get_base(self.fulluri)
        self.get_port(self.base)
        self.domain = self.get_domain(self.base)
        self.path = self.get_path(self.fulluri)
        self.reluri = self.get_reluri(self.fulluri)

        if len(self.base.split('.')) == 2 and not self.fulluri.startswith('ftp://'):
            self.fulluri = '%s%s' % (self.scheme, self.fulluri[len(self.scheme):])
            self.subdomain = ''

        if len(self.base.split('.')) == 3 and not self.fulluri.startswith('ftp://'):
            if not self.base.startswith('www.'):
                self.subdomain = self.base.split('.')[0]

        if not self.subdomain:
            self.subdomain = ''
        self.unquoted_uri = self.unquote_uri()

    def get_reluri(self, uri):
        uri = self.strip_scheme(uri)
        if uri.endswith('/'):
            uri = uri[:-1]

        if not '/' in uri:
            return self.scheme + uri + '/'
        if '/' in uri and not uri.endswith('/'):
            spl = uri.split('/')
            for a in ['.html', 'htm', '.php', '.aspx', '.asp']:
                if a in spl[len(spl)-1]:
                    return self.scheme + '/'.join(spl[:-1]) + '/'  # fml
            return self.scheme + '/'.join(spl) + '/'
        return '?!'

    def get_fulluri(self, uri):
        if self.auth:
            uri = uri.replace('%s@' % ':'.join(self.auth), '', 1)

        if uri.endswith('/'):
            uri = uri[:-1]

        for s in ['http://', 'https://', 'ftp://']:
            if uri.startswith(s):
                self.scheme = s
                return uri

        self.scheme = 'http://'
        return 'http://%s' % uri

    def get_base(self, uri):
        uri = self.strip_scheme(uri)
        uri = uri[:uri.find('/')] if '/' in uri else uri
        if '@' in uri:
            uri = uri.split('@')[-1]

        return uri

    def get_port(self, uri):
        if ':' in uri:
            port = uri.split(':')[-1]
            test = ':%s' % str(port)

            try:
                self.port = int(uri.split(':')[-1])
            except:
                pass

            self.base = uri.split(':', 1)[0]
            self.fulluri = self.fulluri.replace(test, '', 1)
        else:
            schemes = {
                'https': 443,
                'http': 80,
                'ftp': 21
            }

            scheme = self.scheme.split('://', 1)[0]

            if scheme in schemes:
                self.port = schemes[scheme]

    def get_auth(self, uri):
        for s in ['http://', 'https://', 'ftp://']:
            if uri.startswith(s):
                uri = uri[len(s):]

        if '@' in uri and ':' in uri:
            return '@'.join(uri.split('@')[:-1]).split(':', 1)

    def get_domain(self, uri):
        spl = uri.split('.')
        if len(spl) == 4:
            for s in spl:
                try:
                    int(s)
                    return uri
                except:
                    break
        return '.'.join(spl[-2:]) if len(spl) > 1 else uri

    def get_path(self, uri):
        uri = self.strip_scheme(uri)
        return uri[uri.find('/'):] if '/' in uri else None

    def strip_scheme(self, uri):
        if uri.startswith('http://'):
            return uri[7:]
        elif uri.startswith('https://'):
            return uri[8:]
        elif uri.startswith('ftp://'):
            return uri[6:]
        else:
            return uri

    def unquote_uri(self):
        return cgi.escape(urllib2.unquote(self.fulluri))