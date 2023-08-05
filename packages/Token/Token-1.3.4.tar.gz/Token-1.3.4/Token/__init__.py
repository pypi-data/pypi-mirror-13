from __future__ import absolute_import

# import models into sdk package
from .models.patch_account_request import PatchAccountRequest
from .models.create_charge_request import CreateChargeRequest
from .models.get_banknote_response import GetBanknoteResponse
from .models.get_payment_response import GetPaymentResponse
from .models.create_charge_response import CreateChargeResponse
from .models.get_charge_response import GetChargeResponse
from .models.create_token_response import CreateTokenResponse
from .models.create_payment_response import CreatePaymentResponse
from .models.get_payments_response_payment import GetPaymentsResponsePayment
from .models.get_tokens_response_token_terms import GetTokensResponseTokenTerms
from .models.redeem_banknote_response import RedeemBanknoteResponse
from .models.currency_code import CurrencyCode
from .models.get_account_response import GetAccountResponse
from .models.get_accounts_response import GetAccountsResponse
from .models.money import Money
from .models.get_tokens_response import GetTokensResponse
from .models.get_token_response import GetTokenResponse
from .models.create_token_request_terms import CreateTokenRequestTerms
from .models.patch_token_request_terms import PatchTokenRequestTerms
from .models.redeem_banknote_request import RedeemBanknoteRequest
from .models.get_banknotes_response_banknote import GetBanknotesResponseBanknote
from .models.get_receipt_response import GetReceiptResponse
from .models.get_token_response_terms import GetTokenResponseTerms
from .models.create_account_response import CreateAccountResponse
from .models.get_balance_response import GetBalanceResponse
from .models.create_payment_request import CreatePaymentRequest
from .models.patch_token_request import PatchTokenRequest
from .models.create_receipt_request import CreateReceiptRequest
from .models.get_charges_response import GetChargesResponse
from .models.math_context import MathContext
from .models.get_receipts_response_receipt import GetReceiptsResponseReceipt
from .models.get_banknotes_response import GetBanknotesResponse
from .models.create_token_request import CreateTokenRequest
from .models.create_account_request import CreateAccountRequest
from .models.get_payments_response import GetPaymentsResponse
from .models.get_charges_response_charge import GetChargesResponseCharge
from .models.get_charge_response_terms import GetChargeResponseTerms
from .models.create_receipt_response import CreateReceiptResponse
from .models.big_int import BigInt
from .models.get_receipts_response import GetReceiptsResponse
from .models.big_integer import BigInteger
from .models.get_accounts_response_account import GetAccountsResponseAccount
from .models.get_tokens_response_token import GetTokensResponseToken
from .models.get_charges_response_charge_terms import GetChargesResponseChargeTerms

# Identity service models
from .models.get_banks_response import GetBanksResponse
from .models.get_member_response import GetMemberResponse
from .models.create_device_response import CreateDeviceResponse
from .models.link_bank_request import LinkBankRequest
from .models.patch_member_request import PatchMemberRequest
from .models.finite_duration import FiniteDuration
from .models.create_member_request_device import CreateMemberRequestDevice
from .models.patch_device_request import PatchDeviceRequest
from .models.get_banks_response_bank import GetBanksResponseBank
from .models.create_member_request import CreateMemberRequest
from .models.create_device_request import CreateDeviceRequest
from .models.get_devices_response_device import GetDevicesResponseDevice
from .models.create_member_response import CreateMemberResponse
from .models.get_devices_response import GetDevicesResponse

# Settlement service models
from .models.system_check_response import SystemCheckResponse
from .models.currency_unit import CurrencyUnit
from .models.get_transfer_response import GetTransferResponse
from .models.create_settlement_request import CreateSettlementRequest
from .models.create_settlement_response_entry import CreateSettlementResponseEntry
from .models.create_settlement_response_transfer import CreateSettlementResponseTransfer
from .models.get_transfers_response import GetTransfersResponse
from .models.system_state_response_property import SystemStateResponseProperty
from .models.math_context import MathContext
from .models.create_transfer_request import CreateTransferRequest
from .models.money import Money
from .models.system_state_response import SystemStateResponse
from .models.create_transfer_response import CreateTransferResponse
from .models.create_settlement_response import CreateSettlementResponse
from .models.get_transfers_response_transfer import GetTransfersResponseTransfer

# src
from .apis.combined_banknote_api import BankNoteService as BNS
from .apis.combined_identity_api import IdentityService as IS
from .apis.combined_settlement_api import SettlementService as SS
from .src.Crypto import generate_keys

import os
script_path = os.path.dirname(os.path.abspath( __file__ ))

accounts = {"334":{
                "clientId":"bill.york",
                "bankAccountId":"334-564-9283"},
            "467":{
                "clientId":"mariano.sorgente",
                "bankAccountId":"467-342-9329"},
            "950": {
                "clientId":"acme.merchant",
                "bankAccountId":"95006098446"},
            "238": {
                "clientId": "steve.jobs",
                "bankAccountId": "238-347-3489"},
            "374":{
                "clientId":"steve.jobs",
                "bankAccountId": "374-344-8372"},
            }
context = None
env = 'prod'
debug = False

def demo(demo_num):
    try:
        f = open(os.path.join(script_path,'src/demo/demo' + str(demo_num) + '.py'))
        print(f.read())
    except IOError:
        print("Demo does not exist.")

def welcome_message():
    print("Welcome to the Token console. Type Token.help() for help.")

def help():
    print("+-------------------------------------------------------------+")
    print("| Welcome to the Token console. Here we can issue commands to |")
    print("| interact with the Token system.                             |")
    print("+-------------------------------------------------------------+")
    print("| ACCOUNTS                                                    |")
    print("| bofa checking account: '467'                                |")
    print("| bofa savings account: '334'                                 |")
    print("| citi AMCE merchant account: '950'                           |")
    print("| wells checking account: '238'                               |")
    print("| wells savings account: '374'                                |")
    print("+-------------------------------------------------------------+")
    print("| COMMANDS - Token                                            |")
    print("| Token.BankNoteService(bank_code)   // citi or bofa          |")
    print("| Token.IdentityService()                                     |")
    print("| Token.generate_keys()                                       |")
    print("| Token.switchContext(new_context)   // citi, alice, token,et |")
    print("| Token.switchEnvironment(new_env)   // dev, prod             |")
    print("| Token.demo(2)                      // show demo (1-6)       |")
    print("| Token.help()                       // print this            |")
    print("|                                                             |")
    print("| COMMANDS - Identity Service                                 |")
    print("| IS.create_member(keys)                                      |")
    print("| IS.get_member(keys)                                         |")
    print("|                                                             |")
    print("| COMMANDS - Banknote Service                                 |")
    print("| bofa.create_account(member, '6dfd')   // provide acc code   |")
    print("| bofa.get_balance(account)                                   |")
    print("| bofa.create_token(account, payee, amount, curr [, maxCount, |")
    print("|                   callout, descr])                          |")
    print("| bofa.create_payment(account, payee, amount, curr [, descr]) |")
    print("| bofa.redeem_token(token, amount, curr [, descr])            |")
    print("| bofa.deposit_banknote(account, banknote)                    |")
    print("|                                                             |")
    print("| COMMANDS - SettlementService                                |")
    print("| SS.settle()                       // trigger a settle       |")
    print("+-------------------------------------------------------------+")
    print("| You can use dir(object) to see what methods its has.        |")
    print("+-------------------------------------------------------------+")


def switchContext(c):
    global context
    context = c

def switchEnvironment(e):
    global env
    env = e

class BankNoteService(BNS):
    def __init__(self, bank_code='', api_client=None):
        super(BankNoteService, self).__init__(bank_code, env)

    def get_accounts(self, member_id):
        return super(BankNoteService, self).get_accounts(member_id)

    def get_balance(self, acc):
        if context != 'alice' and context != 'bob' and context != 'carol':
            print("Error: need member context.")
            return None
        accountId = acc.id
        return super(BankNoteService, self).get_balance(accountId)

    def create_token(self, acc, payee, amount, currency, maxCount= 100, callout=None, description="demo", request=None):
        if context != 'alice' and context != 'bob' and context != 'carol':
            print("Error: need member context.")
            return None
        if request is None:
            request ={
              "payeeMemberId": payee.member_id,
              "description": description,
              "terms": {
                "maxAmount": {
                  "value": str(amount),
                  "unit": currency
                },
                "maxCount": maxCount
              }
            }
            if callout is not None:
                request["callout"] = {
                    "name": "custom-callout",
                    "uri": callout
                }
        ret =super(BankNoteService, self).create_token(acc.id, request)
        if debug: print(ret)
        return ret

    def create_payment(self, acc, payee, amount, currency, description="demo", request=None):
        if context != 'alice' and context != 'bob' and context != 'carol':
            print("Error: need member context.")
            return None
        if request is None:
            request ={
                "payeeMemberId": payee.member_id,
                "description": description,
                "amount": {
                  "value": str(amount),
                  "unit": currency
                }
            }
        ret =super(BankNoteService, self).create_payment(acc.id, request)
        ret2 = super(BankNoteService, self).get_payment(ret.id)
        banknote = {}
        banknote['bank_code'] = self.bank_code
        banknote['banknote_id'] = ret2.banknote_id
        if debug: print(ret2)
        return banknote

    def redeem_token(self, token, amount, currency, description="demo", request=None):
        if context != 'alice' and context != 'bob' and context != 'carol':
            print("Error: need member context.")
            return None
        if request is None:
            request ={
                "amount": {
                  "value": str(amount),
                  "unit": currency
                },
                "description": description
            }
        ret = super(BankNoteService, self).create_charge(token.id, request)
        if debug: print(ret)
        print(ret)
        banknote = {'id':ret.id, 'banknote_id': ret.banknote_id, 'bank_code':self.bank_code}
        return banknote


    def deposit_banknote(self, acc, banknote, request=None):
        if context != 'alice' and context != 'bob' and context != 'carol':
            print("Error: need member context.")
            return None
        if request is None:
            request ={
              "description": "bofa",
              "payerBankCode": banknote['bank_code'],
              "payerBanknoteId": banknote['banknote_id']
            }
        ret = super(BankNoteService, self).create_receipt(acc.id, request)
        if debug: print(ret)
        return ret

    def create_account(self, user, clientId, request=None):
        if context != 'citi' and context != 'bofa' and context!='wells':
            print("Error: need bank context.")
            return None
        if clientId[:4] not in accounts:
            print("Error: entered an invalid account.")
            return None
        accInfo = accounts[clientId[:4]]
        if request is None:
          request = {"bankAccountId": accInfo["bankAccountId"],
          "memberId": user.member_id,
          "memberPublicKey": user.keys[0],
          "memberPinPublicKey": "123",
          "name": "user"}
        ret = super(BankNoteService, self).create_account(accInfo["clientId"], request)
        if debug: print(ret)
        return ret


class IdentityService(IS):
    def __init__(self, api_client=None):
        super(IdentityService, self).__init__(env, api_client)

    def create_member(self, keys, request=None):
        if context != 'token':
            print('Error: need token context.')
            return None
        if request is None:
            if len(keys) < 2: return None
            request ={"name": "Anon","publicKey": keys[0],
                      "pinPublicKey": "123",
                      "device": {
                        "name": "dev1",
                        "pushNotificationId": "123",
                        "publicKey": keys[1]
                      }
                    }
        user = super(IdentityService, self).post_member(request)
        if user is not None:
            user.keys = keys
        if debug: print(user)
        return user

class SettlementService(SS):
    def __init__(self, api_client=None):
        super(SettlementService, self).__init__(env, api_client)

    def settle(self, request=None):
        if context != 'token':
            print('Error: need token context.')
            return None
        if request is None:
            request = {"description":"python"}
        ret = super(SettlementService, self).post_settlement(request)
        if debug: print(ret)
        return ret

# import ApiClient
from .api_client import ApiClient

from .configuration import Configuration

configuration = Configuration()
welcome_message()
