from pycoin.services.blockchain_info import spendables_for_address
from pycoin.tx import script, Tx
from pycoin.tx.tx_utils import sign_tx
from pycoin.tx.TxOut import TxOut, standard_tx_out_script
from binascii import hexlify
from pycoin.serialize import b2h_rev
import messaging as m

def spendable_to_legible(spendable):
    return b2h_rev(spendable.previous_hash) + ":" + str(spendable.previous_index)

def write_transfer(sender, sender_priv, recipient, message, fee=m.default_fee, avoid_inputs=[]):
    message = hexlify(message.encode()).decode('utf8')
    spendables = spendables_for_address(sender)
    spendables = [s for s in spendables if not spendable_to_legible(s.tx_in()) in avoid_inputs]
    bitcoin_sum = sum([spendable.coin_value for spendable in spendables])
    inputs = [spendable.tx_in() for spendable in spendables]
    outputs = []
    if bitcoin_sum > fee + m.dust*2:
        remaining = bitcoin_sum - fee - m.dust*2
        dest_output_script = standard_tx_out_script(recipient)
        change_output_script = standard_tx_out_script(sender)
        btc_change_output_script = standard_tx_out_script(sender)
        op_return_output_script = script.tools.compile("OP_RETURN %s" % message)

        outputs.append(TxOut(m.dust, dest_output_script))
        outputs.append(TxOut(m.dust, change_output_script))
        outputs.append(TxOut(remaining, btc_change_output_script))
        outputs.append(TxOut(0, op_return_output_script))

        tx = Tx(version=1, txs_in=inputs, txs_out=outputs)
        tx.set_unspents(spendables)
        sign_tx(tx, wifs=[sender_priv])
        print tx.as_hex()
        return tx.as_hex()
    else:
        print "INADEQUATE FUNDS"

def write_opreturn(bitcoin_address, bitcoin_private_key, raw_message, \
    fee=m.default_fee, avoid_inputs=[]):
    message = hexlify(raw_message.encode()).decode('utf8')
    spendables = spendables_for_address(bitcoin_address)
    spendables = [s for s in spendables if not spendable_to_legible(s.tx_in()) in avoid_inputs]
    bitcoin_sum = sum([spendable.coin_value for spendable in spendables])
    inputs = [spendable.tx_in() for spendable in spendables]
    outputs = []
    if (bitcoin_sum > fee):
        change_output_script = standard_tx_out_script(bitcoin_address)
        print change_output_script
        outputs.append(TxOut(bitcoin_sum - fee, change_output_script))

        ## Build the OP_RETURN output with our message
        op_return_output_script = script.tools.compile("OP_RETURN %s" % message)
        outputs.append(TxOut(0, op_return_output_script))

        ## Create the transaction and sign it with the private key
        tx = Tx(version=1, txs_in=inputs, txs_out=outputs)
        tx.set_unspents(spendables)
        sign_tx(tx, wifs=[bitcoin_private_key])
        print tx.as_hex()
        return tx.as_hex()
    else:
        print "INADEQUATE FUNDS"
