# Demo 3: Transfers with three banks, along with net settlement

import Token

bofa = Token.BankNoteService('bofa')
citi = Token.BankNoteService('citi')
wells = Token.BankNoteService('wells')
IS = Token.IdentityService()

aliceKeys = Token.generate_keys()
bobKeys = Token.generate_keys()
carolKeys = Token.generate_keys()

Token.switchContext('token')
alice = IS.create_member(aliceKeys)
bob = IS.create_member(bobKeys)
carol = IS.create_member(carolKeys)

Token.switchContext('bofa')
aliceAcc = bofa.create_account(alice, '467')
aliceAcc2 = bofa.create_account(alice, '334')

Token.switchContext('citi')
bobAcc = citi.create_account(bob, '950')

Token.switchContext('wells')
carolAcc = wells.create_account(carol, '238')

Token.switchContext('alice')
bofa.get_balance(aliceAcc)
t1 = bofa.create_token(aliceAcc, bob, 15, 'USD')
t2 = bofa.create_token(aliceAcc, carol, 20, 'USD')

Token.switchContext('bob')
citi.get_balance(bobAcc)
t3 = citi.create_token(bobAcc, alice, 30, 'USD')
t4 = citi.create_token(bobAcc, carol, 40, 'USD')

Token.switchContext('carol')
wells.get_balance(carolAcc)
t5 = wells.create_token(carolAcc, alice, 50, 'USD')
t6 = wells.create_token(carolAcc, bob, 60, 'USD')

Token.switchContext('alice')
banknote = citi.redeem_token(t3, 30, 'USD')
banknote2 = wells.redeem_token(t5, 50, 'USD')
bofa.deposit_banknote(aliceAcc, banknote)
bofa.deposit_banknote(aliceAcc, banknote2)

Token.switchContext('bob')
banknote = bofa.redeem_token(t1, 15, 'USD')
banknote2 = wells.redeem_token(t6, 60, 'USD')
citi.deposit_banknote(bobAcc, banknote)
citi.deposit_banknote(bobAcc, banknote2)

Token.switchContext('carol')
banknote = bofa.redeem_token(t2, 20, 'USD')
banknote2 = citi.redeem_token(t4, 40, 'USD')
wells.deposit_banknote(carolAcc, banknote)
wells.deposit_banknote(carolAcc, banknote2)

# Settle the differences between the holding accounts of each bank
Token.switchContext('token')
SS = Token.SettlementService()
SS.settle()
