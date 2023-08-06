#                                              
#                                              
#           .        .--.   _..._              
#         .'|        |__| .'     '.   .--./)   
#     .| <  |        .--..   .-.   . /.''\\    
#   .' |_ | |        |  ||  '   '  || |  | |   
# .'     || | .'''-. |  ||  |   |  | \`-' /    
#'--.  .-'| |/.'''. \|  ||  |   |  | /("'`     
#   |  |  |  /    | ||  ||  |   |  | \ '---.   
#   |  |  | |     | ||__||  |   |  |  /'""'.\  
#   |  '.'| |     | |    |  |   |  | ||     || 
#   |   / | '.    | '.   |  |   |  | \'. __//  
#   `'-'  '---'   '---'  '--'   '--'  `'---' 
#"thing" database - github/ItsLukeJames

#Imports
import base64
from Crypto.Cipher import AES
import hashlib
import ast
BLOCK_SIZE = 32
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def encrypt(string, secret):
    encoded = EncodeAES(AES.new(secret), string)
    return encoded

def decrypt(string, secret):
    decoded = DecodeAES(AES.new(secret),string)
    return decoded



def start(file="db.thing", secret="gkgkjlekgjlrkejglkrfb,mfdnemfn,d"):
    f = open(file, "r")
    encrypted = f.read()
    unencrypted = decrypt(encrypted, secret)
    return ast.literal_eval(unencrypted)
    
def save(dict, file="db.thing", secret="gkgkjlekgjlrkejglkrfb,mfdnemfn,d"):
    string = str(dict)
    encrypted = encrypt(string, secret)
    f = open(file, "w")
    f.write(encrypted)
    f.close()
    return dict
    
    
    
