#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module piwigo.ws
"""

import requests
import types

BOOLEAN_REQUEST = { True: 'true', False: 'false'}

class WsNotExistException(Exception):
    
    def __init__(self, method):
        self._method = method

    def __str__(self):
        return "Ws %s not exist" % self._method

class WsErrorException(Exception):
    
    def __init__(self, strerr):
        self._strerr = strerr

    def __str__(self):
        return self._strerr

class WsPiwigoException(Exception):
    
    def __init__(self, err, message):
        self.err = err
        self.message = message

    def __str__(self):
        return "%s : %s" % (self.err, self.message)

class Piwigo:

    def __init__(self, url):
        self._cookies = None
        if url[-1] == '/': url = url[:-1]
        self._url = url
        self._urlws = '%s/ws.php?' % self._url
        self._cookies = None

    def __getattr__(self, name):
        return Ws(self, name)

    def setCookies(self, ws, req):
        try:
            if ws._method == 'pwg.session.login' and req.json()['stat'] == 'ok':
                self._cookies = req.cookies
            if ws._method == 'pwg.session.logout':
                self._cookies = None
        except:
            pass


class Ws:

    def __init__(self, pwg, name):
        self._pwg = pwg
        self._method = name
        self._post_only = False

    def _getMethodDetail(self):
        try:
            method_detail = self._pwg.reflection.getMethodDetails(methodName=self._method)
            return method_detail
        except WsPiwigoException as e:    
            raise WsNotExistException(self._method)

    def _getPostOnly(self):
         try:
            return self._getMethodDetail()['options']['post_only']
         except WsNotExistException as e:
            raise e
         except:
            return False

    def getParams(self):
        return {param['name'] : param for param in self._getMethodDetail()['params'] }
    
    def check(fn):
        def checking(self, **kw):
            if self._method != 'reflection.getMethodDetails':
                self._post_only = self._getPostOnly()
            return fn(self, **kw)
        return checking    

    @check
    def __call__(self, **kw):
        for i in kw:
            if type(kw[i]) == types.BooleanType : kw[i] = BOOLEAN_REQUEST[kw[i]]
        url = self._pwg._urlws
        kw["method"] = self._method
        kw["format"] = "json"
        params = kw
        data = {}
        files = {}
        if 'image' in kw:
            files = {'image': open(kw['image'], 'rb')}
            params = { i : params[i] for i in params if i != 'image'}
        else:
            files = {}
        if self._post_only:
            data = { i : params[i] for i in params if i != 'format'}
            params = { i : params[i] for i in params if i == 'format'}
            r = requests.post(url, params=params, data=data, files=files, cookies=self._pwg._cookies)  
        else:
            r = requests.get(url, params=params, data=data, files=files, cookies=self._pwg._cookies)  
        try:
            result = r.json()
            if result['stat'] == 'fail':
                raise WsPiwigoException(result['err'], result['message'])    
            self._pwg.setCookies(self,r)
            return result['result']
        except WsPiwigoException as e:
            raise e
        except:
            raise WsErrorException(r.text)

    def __getattr__(self, name):
        return Ws(self._pwg, '%s.%s' % (self._method, name))

    def __str__(self):
        try:
            return "%s : %s" % (self._method, self._getMethodDetail()['description'])
        except WsNotExistException as e:
            return "%s : not exist" % self._method
        return "error"
