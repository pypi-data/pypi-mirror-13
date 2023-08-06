import json
import StringIO
import time
import requests
from PIL import Image
import pixelwriter as p

requests.packages.urllib3.disable_warnings()

def get_block(block_height):
    blocks = json.loads(requests.get("https://blockchain.info/block-height/" + \
        str(block_height)+"?format=json").content)
    for block in blocks['blocks']:
        if block['main_chain']:
            return block

def txs_in_block(block_height):
    txs_data = requests.get("https://bitcoin.toshi.io/api/v0/blocks/{0}/transactions".\
        format(block_height)).content
    return json.loads(txs_data)['transactions']

def get_tx_toshi(txhash):
    url = "https://bitcoin.toshi.io/api/v0/transactions/{0}".format(txhash)
    tx_data = json.loads(requests.get(url).content)
    return tx_data

def get_tx_blockcypher(txhash):
    tries = 10
    interval = 3
    success = False
    n = 0
    url = "https://api.blockcypher.com/v1/btc/main/txs/{0}".format(txhash)
    while not success and n < tries:
        n += 1
        try:
            tx_data = json.loads(requests.get(url).content)
            assert 'outputs' in tx_data
            success = True
        except:
            print "COULD NOT PULL TXHASH {0} FROM BLOCKCYPHER.".format(txhash)
            print url
            time.sleep(interval)
    return tx_data

def get_address_txs_toshi(address):
    txs = json.loads(requests.get("https://bitcoin.toshi.io/api/v0/addresses/\
        {0}/transactions".format(address)).content)
    return txs

def where_was_output_spent(txhash, output_n):
    tx_data = get_tx_blockcypher(txhash)
    if 'outputs' in tx_data:
        if len(tx_data['outputs']) > output_n:
            if 'spent_by' in tx_data['outputs'][output_n]:
                return tx_data['outputs'][output_n]['spent_by']
    return None

def get_raw_tx(txhash):
    rawtx = requests.get("https://blockchain.info/rawtx/{0}?format=hex".\
        format(txhash)).content
    return rawtx

def get_tx(txhash):
    success = False
    n = 0
    tries = 10
    interval = 2
    while not success and n < tries:
        txdata = requests.get("https://blockchain.info/tx/{0}?format=json"\
            .format(txhash)).content
        try:
            rawtx = json.loads(txdata)
        except:
            print txdata
            time.sleep(interval)
        success = True
    return rawtx

def tx_info(txhash):
    success = False
    n = 0
    tries = 10
    interval = 5
    while not success and n < tries:
        n += 1
        try:
            d = json.loads(requests.get("https://blockexplorer.com/api/tx/{0}"\
                .format(txhash)).content)
            success = True
        except:
            print "ERROR GETTING TX INFO FOR "+str(txhash)
            success = False
            time.sleep(interval)
    return d

def read_tx(txhash, tx_data=None):
    if tx_data is None:
        jsontx = tx_info(txhash)
    else:
        jsontx = tx_data
    message = None

    recipients = [[n, x['scriptPubKey']['addresses'][0]] for n, x in \
        enumerate(jsontx['vout']) if 'addresses' in x['scriptPubKey']]
    inputs = []
    for n, x in enumerate(jsontx['vin']):
        ou = str(x['txid']) + ":" + str(x['vout'])
        inputs.append([n, ou])

    for output in jsontx['vout']:
        if output['scriptPubKey']['type'] == 'nulldata':
            #is opreturn
            hexm = output['scriptPubKey']['hex']
            hexm = hexm[4:len(hexm)]
            message = hexm.decode('hex')

    return message, recipients, inputs

def read_content_tx(txhash, tx_data=None):
    message_data = read_tx(txhash, tx_data)
    message = message_data[0]
    print message
    if not message is None:
        if len(message) > 0:
            if message[0] == "C": #is a content tx
                coords = message.split('/')[1]
                print "COORDS"
                print coords
                coords = p.decompress_coords(coords)
                q = message.split('/')
                url = '/'.join(q[2:len(q)])
                return coords, url
            else:
                return None, None
    else:
        return None, None

def get_address_txs(address):
    url = "https://blockchain.info/address/{0}?format=json".format(address)
    txs_data = requests.get(url).content
    return json.loads(txs_data)['txs']

def recipient_of_output(output):
    txhash = output.split(':')[0]
    output_n = int(output.split(':')[1])
    tx2 = get_tx_toshi(txhash)
    tx = tx_info(txhash)
    return tx['vout'][output_n]['scriptPubKey']['addresses'][0], tx2['block_height']

def read_content_txs_for_owner(output):  #NEED TO CHECK ONLY TXS COMING AFTER OUTPUT OCCURRED
    address, block_height = recipient_of_output(output)
    address_txs = get_address_txs(address)
    coords = None
    url = None
    d = []
    for tx in address_txs:
        txhash = tx['hash']
        block_height = tx['block_height']
        print txhash
        coords, url = read_content_tx(txhash)

        if not coords is None:
            print "Found Content within coords: " + str(coords) + " pointing to " + str(url)
            d.append([coords, url, block_height])
    return d

def extract_contents(content_url):
    try:
        data = json.loads(requests.get(content_url).content)
        link = data['link_url']
        image = data['image_url']
        return link, image
    except:
        print "CANNOT EXTRACT CONTENTS FROM " + str(content_url)
        return None, None

def relevant_data(content_data):
    return content_data

def read_contents(owner_output):
    data = read_content_txs_for_owner(owner_output)
    d = []
    for url in data:
        block_height = url[2]
        link, image_url = extract_contents(url[1])
        q = {}
        q['block_height'] = block_height
        q['link'] = link
        q['image_url'] = image_url
        q['coords'] = url[0]
        new_coords = (q['coords'][1][0] - q['coords'][0][0], q['coords'][1][1] - q['coords'][0][1])
        q['image'] = retrieve_image(image_url).resize(new_coords, Image.ANTIALIAS)
        d.append(q)
    return d

def retrieve_image(image_url):
    c = requests.get(image_url).content
    d = StringIO.StringIO(c)
    return Image.open(d)

def owners_contents(ownerlist):
    data = {}
    for owner in ownerlist:
        contents = read_contents(owner)
        data[owner] = contents
    return data
