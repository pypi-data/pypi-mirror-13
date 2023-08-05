# Demo 2: Transfers with enforced rules, and multiple redemptions

import Token

bofa = Token.BankNoteService('bofa')
citi = Token.BankNoteService('citi')
IS = Token.IdentityService()

aliceKeys = Token.generate_keys()
bobKeys = Token.generate_keys()

Token.switchContext('token')
alice = IS.create_member(aliceKeys)
bob = IS.create_member(bobKeys)

Token.switchContext('bofa')
aliceAcc = bofa.create_account(alice, '467')
aliceAcc2 = bofa.create_account(alice, '334')

Token.switchContext('citi')
bobAcc = citi.create_account(bob, '950')

Token.switchContext('alice')
bofa.get_balance(aliceAcc)
# Now create a token that can be redeemed by bob, at most 2 times, for $10
t1 = bofa.create_token(aliceAcc, bob, 10, 'USD', 2)

Token.switchContext('bob')
citi.get_balance(bobAcc)
banknote = bofa.redeem_token(t1, 1, 'USD')
banknote2 = bofa.redeem_token(t1, 1000, 'USD') # try to redeem for $1000
banknote3 = bofa.redeem_token(t1, 1, 'USD')    # reedeem for $1 again
banknote4 = bofa.redeem_token(t1, 1, 'USD')    # a third time, won't work
citi.deposit_banknote(bobAcc, banknote)        # Deposit the banknote
citi.deposit_banknote(bobAcc, banknote)        # try to deposit banknote again
citi.deposit_banknote(bobAcc, banknote3)       # Deposit the other banknote
t2 = citi.create_token(bobAcc, alice, 2000, 'USD', 5)

# Send some money from bob to alice
Token.switchContext('alice')
banknote = citi.redeem_token(t2, 10, 'USD')
banknote2 = citi.redeem_token(t2, 10, 'USD')
bofa.deposit_banknote(aliceAcc, banknote)
bofa.deposit_banknote(aliceAcc2, banknote2)
