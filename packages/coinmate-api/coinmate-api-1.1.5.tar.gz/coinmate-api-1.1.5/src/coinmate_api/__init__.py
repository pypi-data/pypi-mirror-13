# -*- coding: utf-8 -*-
"""
 CoinMate.io API implementation.
 Version 1.1.0
"""

from urllib2 import Request, urlopen
from urllib import urlencode
import hmac
import hashlib
import time
import json


class coinmate:
    """
    Coinmate.io API class.

    Usage ::

        from coinmate_api import coinmate
        cm_api = coinmate('privateApiKey', 'publicApiKey', 'client_id')
        tid = cm_api.withdraw_bitcoins(2,'1HB1by2ZkbFAwEAqC5zwoHcU1DroBysrPG')
    """

    API_URL = "https://coinmate.io/api/"

    def __init__(self, privateApiKey, publicApiKey, clientId, nonce=None):
        """
        API object constructor.

        Parameters
        ----------
        privateApiKey : string
           coinmate.io private API key.
        publicApiKey : string
           coinmate.io public API key.
        clientId : string
           coinmate.io client id.
        nonce : function
            A function that return a number that can be used only once.
            By default a function that return the number of miliseconds
            is used.
        """
        self.privateApiKey = str(privateApiKey)
        self.publicApiKey = str(publicApiKey)
        self.clientId = str(clientId)
        if not nonce:
            self.nonce = lambda: str(int(time.time() * 100000))

    def create_signature(self, nonce):
        """ This functions generate the signature."""
        signature = nonce + self.clientId + self.publicApiKey
        dig = hmac.new(
            self.privateApiKey,
            msg=signature,
            digestmod=hashlib.sha256
        ).hexdigest()
        signature = dig.encode('utf-8')
        return signature.upper()

    def __do_request(self, url, values=None, headers=None):
        """ Send the HTTP request to the API server."""
        if values:
            values = urlencode(values)
        if headers is None:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        request = Request(self.API_URL + url, data=values, headers=headers)
        return urlopen(request).read()

    def get_balance(self):
        """
        Get account balance info.

        Returns a dictionary with balances info like ::

            {
              "error": false,
              "errorMessage": null,
              "data": {
                "USD": {
                  "currency": "USD",
                  "balance": 20925.48295,
                  "reserved": 9.009,
                  "available": 20916.47395
                },
                "BTC": {
                  "currency": "BTC",
                  "balance": 9934.56163999,
                  "reserved": 8.008,
                  "available": 9926.55363999
                }
              }
            }
        """
        nonce = self.nonce()
        values = {
            'clientId': self.clientId,
            'nonce': nonce,
            'signature': self.create_signature(nonce)
        }
        resp = self.__do_request('balances', values)
        return json.loads(resp)

    def get_eur_balance(self):
        """
        Get EUR balance info.

        Returns a dictionary with EUR balance info like ::

            {
              "error": false,
              "errorMessage": null,
              "data": {
                "EUR": {
                  "currency": "EUR",
                  "balance": 20925.48295,
                  "reserved": 9.009,
                  "available": 20916.47395
                }
              }
            }
        """
        balance = self.get_balance()
        if balance['error']:
            return None
        else:
            return balance['data']['EUR']

    def get_eur_available(self):
        """ Get balance available in EUR account."""
        balance = self.get_balance()
        if balance['error']:
            return None
        else:
            return round(float(balance['data']['EUR']['available']), 2)

    def get_btc_balance(self):
        """
        Get BitCoins balance info.

        Returns A dictionary with BitCoins balance info like ::

            {
              "error": false,
              "errorMessage": null,
              "data": {
                "BTC": {
                  "currency": "BTC",
                  "balance": 20925.48295,
                  "reserved": 9.009,
                  "available": 20916.47395
                }
              }
            }
        """
        balance = self.get_balance()
        if balance['error']:
            return None
        else:
            return balance['data']['BTC']

    def get_btc_available(self):
        """ Get balance available in BitCoin account."""
        balance = self.get_balance()
        if balance['error']:
            return None
        else:
            return round(float(balance['data']['BTC']['available']), 8)

    def withdraw_bitcoins(self, amount, bitcoin_address):
        """
        Function for withdraw BitCoins.

        Parameters
        ----------
        amount : number
           Number of bitcoins to withdraw.
           The minimun amount for withdraw is 0.001 BTC.
        bitcoin_address : string
           address where to send bitcoins.


        Returns
        -------
        int
            coinmate.io bitcoin transaction ID
        """
        nonce = self.nonce()
        values = {'amount': round(amount, 8),
                  'address': str(bitcoin_address),
                  'clientId': self.clientId,
                  'nonce': nonce,
                  'signature': self.create_signature(nonce)
                  }
        resp = self.__do_request('bitcoinWithdrawal', values)
        return json.loads(resp)

    def get_ticker(self):
        """
        Represents basic details about current market situation.

        Returs a dictionary with API response like ::

            {
              "error": false,
              "errorMessage": null,
              "data": {
                "last": 10,
                "high": 1000,
                "low": 10,
                "amount": 224.19978132,
                "bid": 1000,
                "ask": 10
            }
        """
        url_sub = 'ticker?currencyPair=BTC_USD'
        resp = self.__do_request(url_sub)
        return json.loads(resp)

    def get_ticker_low(self):
        """ Returns lowest BTC rate within last 24 hours."""
        ticker = self.get_ticker()
        if not ticker['error']:
            return ticker['data']['low']

    def get_ticker_high(self):
        """ Returns highest BTC rate within last 24 hours."""
        ticker = self.get_ticker()
        if not ticker['error']:
            return ticker['data']['high']

    def get_ticker_last(self):
        """ Returns current BTC rate."""
        ticker = self.get_ticker()
        if not ticker['error']:
            return ticker['data']['last']
