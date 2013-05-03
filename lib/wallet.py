import traceback

try:
    from _detwallet import pubkey_to_address, DeterministicWallet

    wallet = DeterministicWallet()
    mpk = "7b3891225d7208968a0a334692bb5adb212bc4dde4ec815d9754b12475e7282d2b7c81b9248dc861b63cf1f012a7d4c2f840c8e3c61823e2e73ed201acb21ba9".decode(
        "hex")
    wallet.set_master_public_key(mpk)

    def get_address(key_id):
        return pubkey_to_address(wallet.generate_public_key(key_id))
except ImportError:
    traceback.print_exc()
    def get_address(key_id):
        return "lol"


if __name__ == '__main__':
    print get_address(0)
