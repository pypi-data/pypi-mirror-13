

#import urllib.request
import urllib2
#import urllib.parse
import urlparse
#from urllib.error import HTTPError
from urllib2 import HTTPError
import json
import uuid
import urllib
import socket

from jingtumsdk.entities import AccountSettings
from jingtumsdk.entities import Amount
from jingtumsdk.entities import Balance
from jingtumsdk.entities import Payment
from jingtumsdk.entities import Trustline
from jingtumsdk.entities import Order
from logger import logger

from sign import ecdsa_sign, ecc_point_to_bytes_compressed, root_key_from_seed, parse_seed
from serialize import fmt_hex, to_bytes, from_bytes

import binascii
import hashlib
import time
from copy import deepcopy

#VERSION = 'v1'
SIGN_PREFIX = "Jingtum2016"

class JingtumRESTException(Exception):
  pass

class RestapiHelper:
  """The jingtum-rest client

  In the client the server address and a unique client UUID are stored
  A Client can be used only for a single payment, unless its UUID is reset
    
  :param netloc: The hostname of the jingtum rest server
  :param secure: If the connection to the server should be encripted
  :param resource_id: The UUID to be used for the requests
  """
  def set_resource_id(self, resource_id=None):
    """Set the local UUID
    
    :param resource_id: The UUID to be used. Defaults to a random one
    """
    self.uuid = resource_id or str(uuid.uuid4())

  def get_sign_info(self, address, secret):
    """
        get sign infomation if needs

    """
    timestamp = int(time.time() * 1000)

    stamp = "%s%s%s" % (SIGN_PREFIX, address, timestamp)
    hash_stamp = hashlib.sha512(stamp).hexdigest()
    msg = hash_stamp[:64]

    key = root_key_from_seed(parse_seed(secret))

    para = {
      "h": msg,
      "t": timestamp,
      "s": binascii.hexlify(ecdsa_sign(key, msg)),
      "k": fmt_hex(ecc_point_to_bytes_compressed(
          key.privkey.public_key.point, pad=False))
    }

    return para

  def __init__(self, netloc, secure=False, api_version="v1",
    resource_id=None):
    if netloc[-2:] == "80":
      netloc = netloc[:-3]
    self.netloc = netloc
    self.api_version = api_version
    self.scheme = 'https' if secure else 'http'
    self.set_resource_id(resource_id=resource_id)
  
  def _request(self, path, parameters=None, data=None, secret=None,
    complete_path=False, method=None):
    """Make an HTTP request to the server
  
    Encode the query parameters and the form data and make the GET or POST
    request
  
    :param path: The path of the HTTP resource
    :param parameters: The query parameters
    :param data: The data to be sent in JSON format
    :param secret: The secret key, which will be added to the data
    :param complete_path: Do not prepend the common path
  
    :returns: The response, stripped of the 'success' field
    
    :raises JingtumRESTException: An error returned by the rest server
    """
    if not complete_path:
      path = '/{version}/{path}'.format(version=self.api_version, path=path)
    if parameters:
      parameters = {k:v for k,v in parameters.items() if v is not None}
      for k, v in parameters.items():
        if type(v) is bool:
          parameters[k] = 'true' if v else 'false'
      #parameters = urllib.parse.urlencode(parameters)
      parameters = urllib.urlencode(parameters)
    pieces = (self.scheme, self.netloc, path, parameters, None)
    #url = urllib.parse.urlunsplit(pieces)
    url = urlparse.urlunsplit(pieces)
    logger.debug("in _request:" + str(url))
    #req = urllib.request.Request(url)
    req = urllib2.Request(url)
    if method is not None:
      req.get_method = lambda:method
    if data is not None:
      req.add_header("Content-Type","application/json;charset=utf-8")
      self.set_resource_id()
      data['client_resource_id'] = self.uuid
      data['secret'] = secret
      data = json.dumps(data).encode('utf-8')
    try:
      #response = urllib.request.urlopen(req, data)
      logger.debug("in _request:" + str(data))
      response = urllib2.urlopen(req, data, timeout=10)
      realsock = response.fp._sock.fp._sock
      res = json.loads(response.read().decode('utf-8'))
      realsock.close() 
      response.close()
    except HTTPError as e:
      #error_object = json.loads(e.read().decode('utf-8'))['message']
      error_object = e.read()
      raise JingtumRESTException(error_object)
    #####print "in _request", path, response
    if res['success']:
      #del response['success']
      return res
    else:
      raise JingtumRESTException(res['message'])
    
  def get_balances(self, address, currency=None, counterparty=None, parameters=None, **kwargs):
    """Get the balances of an account
    
    :param address: The account to be queried
    :param currency: The currency to limit the query to
    :param counterparty: The issuer of the IOU
      
    :returns: A generator of balances
    """
    d_parameters = deepcopy(parameters)
    if currency is not None:
      d_parameters["currency"] = currency
    if counterparty is not None:
      d_parameters["counterparty"] = counterparty

    url = 'accounts/{address}/balances'
    url = url.format(address=address)
    response = self._request(url, d_parameters, kwargs, method="GET")
    del d_parameters
    return response["balances"]
    # for balance in response['balances']:
    #   yield Balance(issuer=address, **balance)
  
  def get_account_settings(self, address, **kwargs):
    """Get the settings of the specified account
    
    :param address: The account to be queried
    
    :return: The requested settings
    :rtype: AccountSettings
    """
    url = 'accounts/{address}/settings'
    url = url.format(address=address)
    response = self._request(url)
    return AccountSettings(account=address, **response['settings'])
  
  def post_account_settings(self, address, secret, **kwargs):
    """Set the account settings
    
    One or more parameters can be specified at one time.
     
    :param secret: The key that will be used to sign the transaction
    :param address: The jingtum address of the account in question
    :param bool disable_master:
    :param bool disallow_xrp:
    :param bool password_spent:
    :param bool require_authorization:
    :param bool require_destination_tag:
    :param transaction_sequence:
    :param email_hash:
    :param wallet_locator:
    :param message_key:
    :param url:
    :param transfer_rate:
    :param signers:
    
    :return: The settings of the account after the change
    """
    url = 'accounts/{address}/settings'
    url = url.format(address=address)
    response = self._request(url, data=kwargs, secret=secret)
    return response['ledger'], response['hash'], response['settings']
  
  def post_payment(self, secret, payment, active_address, is_sync=False):
    """Send a payment
    
    To prevent double-spends, only one payment is possible with the same UUID.
    A second payment is possible if the UUID is reset using set_resource_id()
    
    :param secret: The key that will be used to sign the transaction
    :param payment: The proposed payment that will be sent to the network
    
    :return: The UUID used for this payment and the URL of the payment
    :rtype: (uuid, url)
    """
    if is_sync:
      url = 'accounts/{address}/payments?validated=true'
    else:
      url = 'accounts/{address}/payments'
    
    url = url.format(address=active_address)
    response = self._request(url, data={'payment': payment}, secret=secret)
    return response#['client_resource_id'], response['status_url']
  
  def get_paths(self, address, destination_account, value, currency,
    issuer=None, source_currencies=None, parameters=None):
    """Query for possible payment paths
    
    :param address: The source account
    :param destination_account: The destination account
    :param float value: The value of the payment
    :param currency: The currency of the payment
    :param issuer: The issuer of the IOU. If not specified, paths
        will be returned for all of the issuers from whom the
        destination_account accepts the given currency
    :param list source_currencies: Currencies in the form
        (currency_code, [issuer]). If no issuer is specified for a currency
        other than XRP, the results will be limited to the specified currencies
        but any issuer for that currency will do
    
    :return: A generator of possible payments, ready to be submitted
    """
    elements = filter(bool, (value, currency, issuer))
    destination_amount = '+'.join(map(str, elements))
    if source_currencies:
      source_currencies = join(' '.join(curr) for curr in source_currencies)
      parameters['source_currencies'] = source_currencies
    url = 'accounts/{source}/payments/paths/{target}/{amount}'
    url = url.format(
      source=address,
      target=destination_account,
      amount=destination_amount,
    )
    response = self._request(url, parameters, method="GET")
    return response['payments']
    # for payment in response['payments']:
    #   yield Payment(**payment)
  
  def get_payment(self, address, hash_or_uuid, parameters=None):
    """Get payment
    
    Retrieve the details of one or more payments from the skywelld server or,
    if the transaction failled off-network or is still pending,
    from the jingtum-rest instance's local database
    
    :param address: A jingtum account
    :param hash_or_uuid: The identifier of the payment
    
    :return: The requested payment
    """
    url = 'accounts/{address}/payments/{hash_or_uuid}'
    url = url.format(
      address=address,
      hash_or_uuid=hash_or_uuid
    )
    response = self._request(url, parameters)
    #return Payment(**response['payment'])
    return response

  def get_payments(self, address, source_account=None, destination_account=None, exclude_failed=None, 
        direction=None, results_per_page=None, page=None, parameters=None, **kwargs):
    """Retrieve historical payments
    
    :param address: A jingtum account
    :param source_account: Limit the results to payments initiated
        by a particular account
    :param destination_account: Limit the results to payments made
        to a particular account
    :param bool exclude_failed: Return only payment that were successfully
        validated and written into the jingtum Ledger
    :param int start_ledger: If earliest_first is set to true this will be the
        index number of the earliest ledger queried, or the most recent one
        if earliest_first is set to false. Defaults to the first ledger the
        skywelld has in its complete ledger
    :param int end_ledger: If earliest_first is set to true this will be the index
        number of the most recent ledger queried, or the earliest one if
        earliest_first is set to false. Defaults to the last ledger the skywelld
        has in its complete ledger
    :param bool earliest_first: Determines the order in which the results should
        be displayed. Defaults to True
    :param int results_per_page: Limits the number of payments displayed per page
        Defaults to 20
    :param int page: The page to be displayed. If there are fewer payments than
        results_per_page number displayed, this indicates that this is
        the last page
    
    :returns: A generator of pairs of payments and corresponding UUIDs.
      The UUIDs can be blank if the the payment was not submitted using
      the current rest server
    """
    d_parameters = deepcopy(parameters)
    if source_account is not None:
      d_parameters["source_account"] = source_account
    if destination_account is not None:
      d_parameters["destination_account"] = destination_account
    if exclude_failed is not None:
      d_parameters["exclude_failed"] = exclude_failed
    if direction is not None:
      d_parameters["direction"] = direction
    if results_per_page is not None:
      d_parameters["results_per_page"] = results_per_page
    if page is not None:
      d_parameters["page"] = page


    url = 'accounts/{address}/payments'
    url = url.format(address=address)
    response = self._request(url, d_parameters, kwargs, method="GET")
    del d_parameters
    return response['payments']
    # for payment in response['payments']:
    #   #yield Payment(**payment['payment']), payment['client_resource_id']
    #   yield payment

  def get_trustlines(self, address, currency=None, counterparty=None, limit=None, parameters=None, **kwargs):
    """Get an account's existing trustlines
    
    :param address: The account to be queried
    :param currency: Limit the search to this currency
    :param counterparty: Limit the search to this counterparty
    
    :return: A generator of trustlines
    """
    d_parameters = deepcopy(parameters)
      
    if currency is not None and counterparty is not None and limit is not None:
      d_parameters.upate({"limit": str(limit), "currency": currency_type, "counterparty": counterparty})
    url = 'accounts/{address}/trustlines'.format(address=address)
    response = self._request(url, d_parameters, kwargs, method="GET")
    del d_parameters
    return response['trustlines']
      
  def post_trustline(self, address, secret, limit, currency_type, counterparty="", is_sync=False, **kwargs):
    """Add or modify trustline
    
    :params address: The jingtum account that will be modified
    :param secret: The key that will be used to sign the transaction
    :param trustline: The new trustline
    :param bool allow_rippling: Enable rippling. Defaults to True
      
    :return: The modified trustline, the transaction hash and the ledger number
    :rtype: (Trustline, hash, int)
    """
    trustline = {"limit": str(limit), "currency": currency_type, "counterparty": counterparty}
        
    if is_sync:
      url = 'accounts/{address}/trustlines?validated=true'
    else:
      url = 'accounts/{address}/trustlines'
    url = url.format(address=address)
    response = self._request(url, data={'trustline': trustline}, secret=secret)
    return response
    # return (
    #   Trustline(**response['trustline']), 
    #   response['hash'],
    #   int(response['ledger']),
    # )

  
  def get_notification(self, address, hash, parameters=None, **kwargs):
    """Retrieve a notification corresponding to a transaction
    
    The notification is retrieved from either skywelld's historical database
    or jingtum-rest's local database if the transaction was submitted
    through this instance of jingtum-rest
    
    :param address: A jingtum account
    :param hash: Transaction identifier
    
    :return: The requested notification
    """
    url = 'accounts/{address}/notifications/{hash}'
    url = url.format(address=address, hash=hash)
    response = self._request(url, parameters, kwargs, method="GET")
    return response['notification']
  
  def get_connection_status(self):
    """Return the skywelld connection status
    
    :return: If the connection is active
    :rtype: bool
    """
    return self._request('server/connected')['connected']
  
  def get_server_info(self):
    """Get the jingtum-rest and skywelld information
    
    :return: A dictionary with multiple pieces of information
    """
    return self._request('server')

  
  def get_uuid(self):
    """Ask the rest server for a random UUID
    
    :return: uuid (uuid): The UUID provided by the server
    """
    return self._request('uuid')
  
  def get_transaction(self, hash):
    """Get a transaction by hash
    
    :return: The requested transaction
    """
    url = 'transactions/{hash}'
    url = url.format(hash=hash)
    response = self._request(url)
    return response['transaction']

  def generate_wallet(self):
    """
    
    :return: 
    """
    return self._request('wallet/new')

  def account_payment(self, currency_type, currency_value, issuer_address, active_address, issuer_pwd, issuer=None, is_sync=False):
    drop = Amount(currency_value, currency_type, issuer=issuer)
    payment = Payment(issuer_address, active_address, drop)
    return self.post_payment(issuer_pwd, payment, active_address, is_sync)

  def place_order(self, address, secret, order_type, get_type, get_value, pay_type, pay_value, 
        get_counterparty=None, pay_counterparty=None, is_sync=False):
    pay_amount = Amount(pay_value, pay_type, counterparty=pay_counterparty)
    get_amount = Amount(get_value, get_type, counterparty=get_counterparty)
    order = Order(order_type, pay_amount, get_amount)
    
    if is_sync:
      url = 'accounts/{address}/orders?validated=true'
    else:
      url = 'accounts/{address}/orders'
    url = url.format(address=address)
    response = self._request(url, data={'order': order}, secret=secret)
    return response

  def get_account_orders(self, address, parameters=None):
    url = 'accounts/{address}/orders'
    url = url.format(address=address)
    response = self._request(url, parameters, method="GET")
    return response['orders']

  def cancel_order(self, address, secret, order_sequence, is_sync=False):
    if is_sync:
      url = 'accounts/{address}/orders/{order}?validated=true'
    else:
      url = 'accounts/{address}/orders/{order}'
    url = url.format(address=address, order=order_sequence)
    response = self._request(url, data={}, secret=secret, method="DELETE")
    return response

  def get_order_by_hash(self, address, hash_id, parameters=None):
    url = 'accounts/{address}/orders/{hash_id}'
    url = url.format(address=address, hash_id=hash_id)
    response = self._request(url, parameters, method="GET")
    return response

  def get_order_book(self, address, base, counter, parameters=None):
    url = 'accounts/{address}/order_book/{base}/{counter}'
    url = url.format(address=address, base=base, counter=counter)
    response = self._request(url, parameters, method="GET")
    return response

  def retrieve_order_transaction(self, address, hash_id, parameters=None):
    url = 'accounts/{address}/transactions/{id}'
    url = url.format(address=address, id=hash_id)
    response = self._request(url, parameters, method="GET")
    return response

  def order_transaction_history(self, address, source_account=None, destination_account=None, exclude_failed=None, 
        direction=None, results_per_page=None, page=None, parameters=None):
    d_parameters = deepcopy(parameters)
    if source_account is not None:
      d_parameters["source_account"] = source_account
    if destination_account is not None:
      d_parameters["destination_account"] = destination_account
    if exclude_failed is not None:
      d_parameters["exclude_failed"] = exclude_failed
    if direction is not None:
      d_parameters["direction"] = direction
    if results_per_page is not None:
      d_parameters["results_per_page"] = results_per_page
    if page is not None:
      d_parameters["page"] = page

    url = 'accounts/{address}/transactions'
    url = url.format(address=address)
    response = self._request(url, d_parameters, method="GET")
    del d_parameters
    return response

  def add_relations(self, address, secret, relations_type, counterparty, 
    limit_currency, limit_issuer, limit_value, is_sync=False):
    if is_sync:
      url = 'accounts/{address}/relations?validated=true'
    else:
      url = 'accounts/{address}/relations'
    
    url = url.format(address=address)

    data = {
      'type': relations_type, 
      'counterparty': counterparty
    }
    #if limit_currency is not None and limit_issuer is not None:
    limit_amount = Amount(limit_value, limit_currency, issuer=limit_issuer, limit=limit_value)
    data["amount"] = limit_amount
    response = self._request(url, data=data, secret=secret)
    return response

  def get_relations(self, address, relations_type=None, counterparty=None, currency=None, 
    maker=0, parameters=None):
    url = 'accounts/{address}/relations'
    url = url.format(address=address)
    
    if relations_type is not None:
      parameters["type"] = relations_type
    if counterparty is not None:
      parameters["counterparty"] = counterparty
    if currency is not None:
      parameters["currency"] = currency
    if maker <> 0:
      parameters["maker"] = maker
    
    response = self._request(url, parameters)
    return response

  def get_counter_relations(self, counterparty, relations_type, address, currency, maker=0, parameters=None):
    url = 'counterparties/{counterparty}/co-relations'
    url = url.format(counterparty=counterparty)
    parameters.update({
      'type': relations_type, 
      'address': address,
      'currency': currency,
      'maker': maker
    })
    response = self._request(url, parameters)
    return response

  def delete_relations(self, address, secret, relations_type, counterparty, issuer, currency=None):
    url = 'accounts/{address}/relations'
    url = url.format(address=address)
    data = {
      'type': relations_type, 
      'counterparty': counterparty
    }
    if currency is not None:
      data["currency"] = currency + "+" + issuer
    datadump = json.dumps(data).encode('utf-8')
    response = self._request(url, data=data, secret=secret, method="DELETE")
    return response

  def test_wait_seconds(self, seconds):
    url = 'tests/waitInSeconds/{seconds}'
    url = url.format(seconds=seconds)
    response = self._request(url, method="POST")
    return response
    