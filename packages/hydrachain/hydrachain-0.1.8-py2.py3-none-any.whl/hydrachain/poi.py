import ethereum.processblock as pb
import ethereum.config
import hydrachain.native_contracts as nc

from ethereum.slogging import get_logger

log = get_logger('poi')

# activated by configuring a contract address in accountregistry
ethereum.config.default_config['rootregistry'] = b''

_validate_transaction_orig = pb.validate_transaction
_apply_msg_orig = pb._apply_msg

def get_registry(block):

    class ChainMock(object):
        head_candidate = block

    address = block.env.config.get('rootregistry')
    if not address:
        return
    p = nc.chain_nac_proxy(ChainMock(), address, address)
    return p


def is_registered(address, block):
    return True

def is_compatible(sender, receiver , block):
    """
    Checks if sender and receiver are registered with compatible Registrars
    This implicitly checks that sender and receiver are registered.

    """
    return True


# override

def validate_transaction(block, tx):
    # check if caller is registered at all
    if is_compatible(tx.origin, tx.to, block):
        return orig_validate_transaction(block, tx)
    return False

pb.validate_transaction = validate_transaction

def _apply_msg(ext, msg, code):
    """
    msg.sender is caller
    msg.to is called
    ext.tx_origin is tx_origin
    ext._block is block
    """

    def _failed_apply_msg(msg):
        res, gas, dat = 1, msg.gas, []
        return res, gas, dat

    # check caller and called are compatible
    if not is_compatible(msg.sender, msg.to, ext._block):
        return _failed_apply_msg(msg)
    # check tx.origin and called are compatible
    if not is_compatible(ext.tx_origin, msg.to, ext._block):
        return _failed_apply_msg(msg)
    return _apply_msg_orig(ext, msg, code)


pb._apply_msg = _apply_msg


class AccountRegistry(nc.NativeContract):
    """
    maps accounts to Registrars

    registrars

    """
    address = utils.int_to_addr(8000)

    # map accounts to Registrars
    accounts = nc.Dict('address')

    # set of registered registrars
    subregistrars = nc.Dict('address')


    def init(ctx, parent='address', returns=STATUS):
        pass

    def set_admin(ctx, admin='address', returns=STATUS):
        pass

    def register_account(ctx, account='address', returns=STATUS):
        pass

    def remove_account(ctx, account='address', returns=STATUS):
        pass

    def register_subregistrar(ctx, registrar='address', returns=STATUS):
        pass

    def remove_subregistrar(ctx, registrar='address', returns=STATUS):
        pass







class Registrar(nc.NativeContract):

    def init(ctx, returns=STATUS):
        pass



