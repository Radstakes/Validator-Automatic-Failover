from bip_utils import Bip39SeedGenerator, Bip32Slip10Ed25519
#Ed25519
from radix_engine_toolkit import *
from getpass import getpass

network_id = 0x02

print ("Enter a mnemonic string:")
pw = getpass()

MNEMONIC = pw
print('\n')


# Seed phrase created in Babylon wallet
seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()

slip10_ctx = Bip32Slip10Ed25519.FromSeedAndPath(
    seed_bytes, "m/44'/1022'/2'/525'/1460'/0'"
)

# Get private and public keys as hex
private_key_hex = slip10_ctx.PrivateKey().Raw().ToHex()
public_key_hex = slip10_ctx.PublicKey().RawUncompressed().ToHex()

# Convert to RET types
private_key_bytes: bytes = int(private_key_hex, 16).to_bytes(32, "big")
private_key: PrivateKey = PrivateKey.new_ed25519(list(private_key_bytes))
public_key: PublicKey = private_key.public_key()


#print(public_key)
#print(private_key)
print("Private Key Bytes (you'll need this later :)): ",private_key_bytes)

print('\n')
account: Address = derive_virtual_account_address_from_public_key(
        public_key, network_id
    )
print(f"Babylon Address of Keystore: {account.as_str()}")
print('\n')
