import requests
import messaging
import pycoin_writer
import cointools as c
import reader as r

requests.packages.urllib3.disable_warnings()

version = 0
universe_width = 1920
universe_height = 1080
OP_RETURN_MAX_LENGTH = 80

def compress_coords(coords_set):
    n = 0
    m = 1
    for x in coords_set:
        for y in x:
            n += y * m
            m = m * (universe_width)
    n = c.base58encode(n)
    return n

def decompress_coords(n):
    n = int(c.base58decode(n), 16)
    d = []
    odd = True
    rr = []
    while n > 0:
        a = n % (universe_width)
        n = n - a
        n = n / (universe_width)
        if odd:
            rr = [a]
            odd = False
        else:
            rr.append(a)
            d.append(rr)
            odd = True
            rr = []
    assert len(d) % 2 == 0
    return d

def transfer_message(coords_set):
    return str(compress_coords(coords_set))

def get_safe_unspents(address, ownerlist):
    txs = r.get_address_txs(address)
    unsafe = ownerlist.keys()
    outputs = []
    for tx in txs:
        for output in tx['out']:
            if not output['spent'] and output['value'] > 0 and output['addr'] == address:
                h = str(tx['hash']) + str(":") + str(output['n'])
                if h in unsafe:
                    print str(h) + " is not a safe output to spend"
                else:
                    v = output['value']
                    q = {}
                    q['value'] = v
                    q['output'] = h
                    outputs.append(q)
    return q

def write_transfer_tx(sender, coords_set, recipient, sender_priv, fee=messaging.default_fee, sign=True):
    message = transfer_message(coords_set)

    tx = pycoin_writer.write_transfer(sender, sender_priv, recipient, message, fee=fee, avoid_inputs=[])
    return tx

def content_message(coords_set, content_url):
    d = "C/"+str(compress_coords(coords_set)) + '/' + str(content_url)
    assert len(d) <= OP_RETURN_MAX_LENGTH
    return d

def content_tx(from_address, coords_set, content_url, private_key, ownerlist, push=False, fee=messaging.default_fee):
    message = content_message(coords_set, content_url)
    print message
    print len(message)
    assert len(message) <= OP_RETURN_MAX_LENGTH
    destination = from_address
    tx = pycoin_writer.write_opreturn(from_address, private_key, message, \
        fee=fee, avoid_inputs=ownerlist.keys())
    if push:
        txhash = messaging.pushtx(tx)
        return txhash
    else:
        return tx
