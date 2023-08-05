# Demo 1: Basic inter bank transfer through a token and banknote.

import Token

bofa = Token.BankNoteService('bofa')
citi = Token.BankNoteService('citi')
IS = Token.IdentityService()

# Generate a private and public key for each user
aliceKeys = Token.generate_keys()
bobKeys = Token.generate_keys()

# Create the members at the identity service
Token.switchContext('token')
alice = IS.create_member(aliceKeys)
bob = IS.create_member(bobKeys)

# Add a bank account for each member, at their respective banks
Token.switchContext('bofa')
aliceAcc = bofa.create_account(alice, '467')

Token.switchContext('citi')
bobAcc = citi.create_account(bob, '950')

Token.switchContext('alice')
bofa.get_balance(aliceAcc)
# Now create a token that can be redeemed by bob for up to $10
t1 = bofa.create_token(aliceAcc, bob, 10, 'USD')

Token.switchContext('bob')
citi.get_balance(bobAcc)
banknote = bofa.redeem_token(t1, 3, 'USD')    # redeem the token for banknote
bofa.get_balance(aliceAcc)
citi.get_balance(bobAcc)
citi.deposit_banknote(bobAcc, banknote)       # Deposit the banknote
citi.get_balance(bobAcc)                      # Now bob's balance increases
