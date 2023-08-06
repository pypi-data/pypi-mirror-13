import json
import pybitcointools
import requests

dust = 601
default_fee = 10000

#Parts of this file are deprecated in favor of pycoin.

def make_raw_transaction_from_specific_inputs_arrays(fromaddress, \
    amounts_array, destinations_array, unspents, fee=default_fee):
    ins = []
    outs = []
    totalin = 0
    total_amounts = 0
    for uns in unspents:
        totalin = totalin + uns['value']
        ins.append(uns)
    for x in amounts_array:
        total_amounts += x
    if totalin >= total_amounts + fee:
        for n, x in enumerate(amounts_array):
            if x >= dust:
                d = destinations_array[n]
                outs.append({'value': x, 'address': d})
        extra = totalin - total_amounts - fee
        if extra >= dust:
            outs.append({'value': extra, 'address': fromaddress})
        tx = pybitcointools.mktx(ins, outs)

        return tx

def unspents(address):
    url = "https://bitcoin.toshi.io/api/v0/addresses/{0}/unspent_outputs".format(address)
    r = requests.get(url)
    unspents = json.loads(r.content)
    u = []
    for unspent in unspents:
        a = {}
        a['value'] = unspent['amount']
        a['output'] = unspent['transaction_hash'] + ":" + str(unspent['output_index'])
        u.append(a)
    return u

def make_raw_transaction_from_specific_inputs(fromaddress, amount, \
    destination, unspents, fee=default_fee):
    ins = []
    outs = []
    totalin = 0

    for uns in unspents:
        totalin = totalin+uns['value']
        ins.append(uns)

    if totalin >= amount + fee:
        if amount >= dust:
            outs.append({'value': amount, 'address': destination})

        extra = totalin-amount-fee
        if extra >= dust:
            outs.append({'value':extra, 'address':fromaddress})
        tx = pybitcointools.mktx(ins, outs)
        return tx
    else:
        print "INSUFFICIENT BITCOIN"

def make_tx(from_address, amount, destination, private_key, sign=True):
    tx = make_raw_transaction(from_address, amount, destination)
    if sign:
        tx = sign_tx(tx, private_key)
    return tx

def send(from_address, amount, destination, private_key):
    tx = make_tx(from_address, amount, destination, private_key)
    return pushtx(tx)

def make_raw_transaction(fromaddress, amount, destination):#ALL AMOUNTS IN SATOSHI
    unspent_outputs = unspents(fromaddress)
    return make_raw_transaction_from_specific_inputs(fromaddress, amount, destination, unspent_outputs)

def make_op_return_script(message):
    hex_message = message.encode('hex')
    hex_message_length = hex(len(message))
    r = 2
    f = ''
    while r < len(hex_message_length):
        f = f + hex_message_length[r]
        r = r + 1
        if len(f) < 2:
            f = '0' + f
            b = '6a' + f + hex_message
            return b

def add_op_return(unsigned_raw_tx, message):
    deserialized_tx = pybitcointools.deserialize(unsigned_raw_tx)
    newscript = make_op_return_script(message)

    newoutput = {}
    newoutput['value'] = 0
    newoutput['script'] = newscript

    deserialized_tx['outs'].append(newoutput)
    reserialized_tx = pybitcointools.serialize(deserialized_tx)
    return reserialized_tx

def sign_tx(unsigned_raw_tx, privatekey):
    tx = unsigned_raw_tx
    detx = pybitcointools.deserialize(tx)
    input_length = len(detx['ins'])

    for i in range(0, input_length):
        tx = pybitcointools.sign(tx, i, privatekey)
    return tx

def pushtx_blockexplorer(rawtx):
    url = "https://blockexplorer.com/api/tx/send"
    data = {}
    data['rawtx'] = rawtx
    print "PUSHING"
    print rawtx
    print ''
    response = requests.post(url, data=data)
    print "Push Response was "+str(response.content) + " FROM BLOCKEXPLORER API"
    jsonresponse = json.loads(response.content)
    if 'txid' in jsonresponse:
        return str(jsonresponse['txid'])
    else:
        return "None"

def pushtx(rawtx):
    url = "http://btc.blockr.io/api/v1/tx/push"
    data = {}
    data['hex'] = rawtx
    jsondata = json.dumps(data)
    print "PUSHING"
    print rawtx
    print ''
    response = requests.post(url, data=jsondata)
    print "Push Response was "+str(response.content) +" FROM BLOCKR"
    jsonresponse = json.loads(response.content)
    if 'transaction_hash' in jsonresponse:
        return str(jsonresponse['transaction_hash'])
    else:
        return str(pushtx_blockexplorer(rawtx))

def make_op_return_tx(fromaddress, private_key, destination, message, push=True):
    amount = 0
    tx = make_raw_transaction(fromaddress, amount, destination)
    tx = add_op_return(tx, message)
    tx = sign_tx(tx, private_key)
    if push:
        tx_hash = pushtx(tx)
        return tx_hash
    else:
        return tx

def make_unsigned_op_return_tx(fromaddress, destination, message):
    amount = 0
    tx = make_raw_transaction(fromaddress, amount, destination)
    tx = add_op_return(tx, message)
    return tx

def make_unsigned_op_return_tx_with_specific_inputs(fromaddress, destination,\
    message, specific_inputs, fee=default_fee):
    amount = 0
    tx = make_raw_transaction_from_specific_inputs(fromaddress, amount, destination, specific_inputs, fee=fee)
    tx = add_op_return(tx, message)
    return tx

def donate_and_send_message(fromaddress, destination, message, helper_address, helper_priv_key):
    helper_amount = default_fee
    helper_tx = make_raw_transaction(helper_address, helper_amount, fromaddress)
    helper_tx = sign_tx(helper_tx, helper_priv_key)
    helper_tx_hash = pushtx(helper_tx)
    print "PUSHED HELPER TX "+str(helper_tx_hash)

    specific_inputs = []
    q = {}
    q['output'] = helper_tx_hash+":0"
    q['value'] = helper_amount
    specific_inputs.append(q)
    message_tx = make_unsigned_op_return_tx_with_specific_inputs(fromaddress, destination, message, specific_inputs)
    return message_tx
