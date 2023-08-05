# Demo 4: Using a callout to twitter to allow redemption

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
# callout for token that can be redeemed by bob if he tweets #token in 2 mins
url = 'http://callout.api.token.io:80/twitter/search/%23token?duration=2%20minute'
t1 = bofa.create_token(aliceAcc, bob, 10,'USD', 200, url)

Token.switchContext('bob')
citi.get_balance(bobAcc)
banknote = bofa.redeem_token(t1, 3, 'USD')    # redeem the token for banknote
