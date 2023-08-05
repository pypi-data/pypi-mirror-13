import time


def wait_for_transaction(ipc_client, txn_hash, max_wait=60):
    start = time.time()
    while True:
        txn_receipt = ipc_client.get_transaction_receipt(txn_hash)
        if txn_receipt is not None:
            break
        elif time.time() > start + max_wait:
            raise ValueError("Could not get transaction receipt")
        time.sleep(2)
    return txn_receipt


def wait_for_block(ipc_client, block_number, max_wait=60):
    start = time.time()
    while time.time() < start + max_wait:
        latest_block_number = ipc_client.get_block_number()
        if latest_block_number >= block_number:
            break
        time.sleep(2)
    else:
        raise ValueError("Did not reach block")
    return ipc_client.get_block_by_number(block_number)


def get_max_gas(ipc_client):
    latest_block = ipc_client.get_block_by_number('latest')
    max_gas_hex = latest_block['gasLimit']
    max_gas = int(max_gas_hex, 16)
    return max_gas
