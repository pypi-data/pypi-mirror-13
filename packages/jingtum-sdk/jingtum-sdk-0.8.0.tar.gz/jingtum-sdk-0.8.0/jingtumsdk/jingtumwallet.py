# -*- coding:utf-8 -*-

from restapihelper import RestapiHelper
from logger import logger

class JingtumSDKException(Exception):
  pass

def init_api_server(server_host, server_port, is_https, version="v2"):
    global clienthelper, api_version
    try:
        clienthelper = RestapiHelper(server_host + ":" + str(server_port), is_https, version) 
        api_version = version
    except Exception, e:
            logger.error("init_api_server first:" + str(e))

def checkhelper(func):  
    def _func(*args, **args2): 
        global clienthelper 
        try:
            if clienthelper is None:
                print "Please init first"
            else: 
                back = func(*args, **args2)  
                return back  
        except NameError, e:
            logger.error("init_api_server first:" + func.__name__)
        
    return _func 


class JingtumWallet(object):
    """docstring for JingtumWallet"""
    def __init__(self, address=None, secret=None):
        global clienthelper
        self.address = address
        self.secret = secret
        try:
            self.clienthelper = clienthelper
        except NameError, e:
            logger.error("init_api_server first")

    @checkhelper
    def generate_wallet(self):
        _wallet_dict = {}
        try:
            _wallet_dict = self.clienthelper.generate_wallet() 
        except Exception, e:
            logger.error("generate_wallet:" + str(e))


        if _wallet_dict.has_key("wallet"):
            _dict = _wallet_dict["wallet"]
            if _dict.has_key("address") and _dict.has_key("secret"):
                self.address, self.secret = _dict["address"], _dict["secret"]

        return _wallet_dict

    @checkhelper
    def active_account(self, currency_type, currency_value, destination_address):
        _active_dict = {}
        try:
            _active_dict = self.clienthelper.account_payment(currency_type, currency_value, self.address, 
                destination_address, self.secret)   
        except Exception, e:
            logger.error("active_account:" + str(e))

        logger.debug("active_account:" + str(_active_dict))
        if _active_dict.has_key("success") and _active_dict["success"]:
            self.last_resource_id = _active_dict["client_resource_id"]
        return _active_dict

    @checkhelper
    def payment(self, currency_type, currency_value, destination_address, issuer=None, is_sync=False):
        _active_dict = {}
        try:
            _active_dict = self.clienthelper.account_payment(currency_type, currency_value, self.address, 
                destination_address, self.secret, issuer, is_sync)
        except Exception, e:
            logger.error("payment:" + str(e))

        logger.debug("payment------------------:" + str(_active_dict))
        return _active_dict

    @checkhelper
    def place_order(self, order_type, get_type, get_value, pay_type, pay_value, 
        get_counterparty=None, pay_counterparty=None, is_sync=False):
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.place_order(self.address, self.secret, order_type, get_type, get_value, pay_type, pay_value, 
                get_counterparty, pay_counterparty, is_sync)
        except Exception, e:
            logger.error("place_order:" + str(e)) 
        return _ret_dict

    @checkhelper
    def cancel_order(self, order_sequence, is_sync=False):
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.cancel_order(self.address, self.secret, order_sequence, is_sync)
        except Exception, e:
            logger.error("cancel_order:" + str(e)) 
        return _ret_dict

    @checkhelper
    def get_account_orders(self):
        parameters = self.get_sign_info()

        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_account_orders(self.address, parameters)
        except Exception, e:
            logger.error("get_account_orders:" + str(e)) 

        return _ret_dict

    @checkhelper
    def get_order_by_hash(self, hash_id):
        parameters = self.get_sign_info()
        
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_order_by_hash(self.address, hash_id, parameters)
        except Exception, e:
            logger.error("get_order_by_hash:" + str(e)) 
        return _ret_dict

    @checkhelper
    def get_order_book(self, base, counter):
        parameters = self.get_sign_info()
        
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_order_book(self.address, base, counter, parameters)
        except Exception, e:
            logger.error("get_order_book:" + str(e)) 
        return _ret_dict

    @checkhelper
    def get_balances(self, currency=None, counterparty=None):
        parameters = self.get_sign_info()
        
        _ret_list = []
        try:
            _ret_list = self.clienthelper.get_balances(self.address, currency, counterparty, parameters)
        except Exception, e:
            logger.error("get_balances:" + str(e)) 

        return _ret_list

    @checkhelper
    def get_paths(self, source_address, source_secret, destnation_address, value, currency,
        issuer=None, source_currencies=None):
        parameters = self.get_sign_info(source_address, source_secret)

        _ret_list = []
        try:
            _ret_list = self.clienthelper.get_paths(source_address, destnation_address, value, currency,
                issuer, source_currencies, parameters)
        except Exception, e:
            logger.error("get_paths:" + str(e)) 

        return _ret_list

    @checkhelper
    def get_payment(self, hash_or_uuid):
        parameters = self.get_sign_info()

        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_payment(self.address, hash_or_uuid, parameters)
        except Exception, e:
            logger.error("get_payment:" + str(e))  
        
        return _ret_dict

    @checkhelper
    def get_payments(self, source_account=None, destination_account=None, exclude_failed=None, 
        direction=None, results_per_page=None, page=None):
        parameters = self.get_sign_info()
        
        _ret_list = []
        try:
            _ret_list = self.clienthelper.get_payments(self.address, source_account, destination_account, exclude_failed, 
                direction, results_per_page, page, parameters)
        except Exception, e:
            logger.error("get_payments:" + str(e)) 

        return _ret_list

    @checkhelper
    def retrieve_order_transaction(self, hash_id):
        parameters = self.get_sign_info()
        
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.retrieve_order_transaction(self.address, hash_id, parameters)
        except Exception, e:
            logger.error("retrieve_order_transaction:" + str(e))  
        
        return _ret_dict

    @checkhelper
    def order_transaction_history(self, source_account=None, destination_account=None, exclude_failed=None, 
        direction=None, results_per_page=None, page=None):
        parameters = self.get_sign_info()
        
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.order_transaction_history(self.address, source_account, destination_account, exclude_failed, 
                direction, results_per_page, page, parameters)
        except Exception, e:
            logger.error("order_transaction_history:" + str(e))  
        
        return _ret_dict

    @checkhelper
    def add_relations(self, relations_type, counterparty, limit_currency, limit_issuer, limit_value, is_sync=False):
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.add_relations(self.address, self.secret, relations_type, counterparty, 
                limit_currency, limit_issuer, limit_value, is_sync)
        except Exception, e:
            logger.error("add_relations:" + str(e)) 
        
        return _ret_dict

    @checkhelper
    def get_relations(self, relations_type=None, counterparty=None, currency=None, maker=0):
        parameters = self.get_sign_info()
        
        _ret_dict = {}
        #try:
        _ret_dict = self.clienthelper.get_relations(self.address, relations_type, counterparty, currency, maker, parameters)
        #except Exception, e:
        #    print "get_relations error", e  
        
        return _ret_dict

    @checkhelper
    def get_counter_relations(self, counterparty, counterparty_secret, relations_type, currency, maker=0):
        parameters = self.get_sign_info(counterparty, counterparty_secret)
        
        _ret_dict = {}
        #try:
        _ret_dict = self.clienthelper.get_counter_relations(counterparty, relations_type, self.address, currency, maker, parameters)
        #except Exception, e:
        #    print "get_counter_relations error", e  
        
        return _ret_dict

    @checkhelper
    def delete_relations(self, relations_type, counterparty, issuer, currency=None):
        _ret_dict = {}
        #try:
        _ret_dict = self.clienthelper.delete_relations(self.address, self.secret, relations_type, counterparty, issuer, currency)
        #except Exception, e:
        #    print "get_counter_relations error", e 
        return _ret_dict 

    @checkhelper
    def post_trustline(self, limit, currency_type, counterparty="", is_sync=False):
        try:
            return self.clienthelper.post_trustline(self.address, self.secret, limit, currency_type, counterparty, is_sync)
        except Exception, e:
            logger.error("post_trustline:" + str(e)) 

    @checkhelper
    def get_trustlines(self, currency=None, counterparty=None, limit=None):
        parameters = self.get_sign_info()

        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_trustlines(self.address, currency, counterparty, limit, parameters)
        except Exception, e:
            logger.error("get_trustlines:" + str(e)) 
        
        return _ret_dict

    @checkhelper
    def get_notification(self, hash_id):
        parameters = self.get_sign_info()
        
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_notification(self.address, hash_id, parameters)
        except Exception, e:
            logger.error("get_notification:" + str(e)) 
        
        return _ret_dict  

    @checkhelper
    def get_connection_status(self):
        _ret_dict = {}
        try:
            _ret_dict = self.clienthelper.get_connection_status()
        except Exception, e:
            logger.error("get_connection_status:" + str(e)) 
        
        return _ret_dict 

    @checkhelper
    def get_sign_info(self, address=None, secret=None):
        global api_version
        if api_version == "v2":
            try:
                if address == None or secret == None:
                    address, secret = self.address, self.secret
                return self.clienthelper.get_sign_info(address, secret)
            except Exception, e:
                logger.error("get_sign_info:" + str(e)) 

        return None