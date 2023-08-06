Coinmate.io API wrapper
-----------------------

Basic CoinMate.io API wrapper, that support get the balance, withdrawal
and more ::

    from coinmate_api import coinmate
    cm_api = coinmate('privateApiKey', 'publicApiKey', 'client_id')
    print cm_api.get_eur_available()
    result = cm_api.withdraw_bitcoins(2,'1HB1by2ZkbFAwEAqC5zwoHcU1DroBysrPG')
    if not result['error']:
        print "Transaction ID:"
        print result['data']
    ticker_info = cm_api.get_ticker()


[Documentation](http://coinmate_doc.4simple.org/)
-------------

http://coinmate_doc.4simple.org/
