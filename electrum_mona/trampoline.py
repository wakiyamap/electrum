import os
import bitstring
import random

from .logging import get_logger, Logger
from .lnutil import LnFeatures
from .lnonion import calc_hops_data_for_payment, new_onion_packet
from .lnrouter import RouteEdge, TrampolineEdge, LNPaymentRoute, is_route_sane_to_use
from .lnutil import NoPathFound, LNPeerAddr
from . import constants


_logger = get_logger(__name__)

# trampoline nodes are supposed to advertise their fee and cltv in node_update message
TRAMPOLINE_FEES = [
    {
        'fee_base_msat': 0,
        'fee_proportional_millionths': 0,
        'cltv_expiry_delta': 960,
    },
    {
        'fee_base_msat': 1000,
        'fee_proportional_millionths': 100,
        'cltv_expiry_delta': 960,
    },
    {
        'fee_base_msat': 3000,
        'fee_proportional_millionths': 100,
        'cltv_expiry_delta': 960,
    },
    {
        'fee_base_msat': 5000,
        'fee_proportional_millionths': 500,
        'cltv_expiry_delta': 960,
    },
    {
        'fee_base_msat': 7000,
        'fee_proportional_millionths': 1000,
        'cltv_expiry_delta': 960,
    },
    {
        'fee_base_msat': 12000,
        'fee_proportional_millionths': 3000,
        'cltv_expiry_delta': 960,
    },
    {
        'fee_base_msat': 100000,
        'fee_proportional_millionths': 3000,
        'cltv_expiry_delta': 960,
    },
]

# hardcoded list
# TODO for some pubkeys, there are multiple network addresses we could try
TRAMPOLINE_NODES_MAINNET = {
    'x tamafo': LNPeerAddr(host='electrumx.tamami-foundation.org', port=9735, pubkey=bytes.fromhex('02af0e7b05a3fd83d1ecfcf9fd1416e6a7052fcd4d6a82aa4632a0de3f20787a15')),
    'x1 ninja': LNPeerAddr(host='electrumx1.monacoin.ninja', port=9736, pubkey=bytes.fromhex('03bb4962b8abf8a30574881631a4f1529c50dc1bfb64a173e05a05b84f15d4f9a2')),
}

TRAMPOLINE_NODES_TESTNET = {
    'x tamafo': LNPeerAddr(host='testnet-eclair.tamami-foundation.org', port=9735, pubkey=bytes.fromhex('0289141da174653124929121ab010631158ada2f18dbe3f33e4959f277b33a5049')),
}

TRAMPOLINE_NODES_SIGNET = {
    'wakiyamap.dev': LNPeerAddr(host='signet-electrumx.wakiyamap.dev', port=9735, pubkey=bytes.fromhex('02dadf6c28f3284d591cd2a4189d1530c1ff82c07059ebea150a33ab76e7364b4a')),
}

def hardcoded_trampoline_nodes():
    if constants.net.NET_NAME == "mainnet":
        return TRAMPOLINE_NODES_MAINNET
    if constants.net.NET_NAME == "testnet":
        return TRAMPOLINE_NODES_TESTNET
    if constants.net.NET_NAME == "signet":
        return TRAMPOLINE_NODES_SIGNET
    return {}

def trampolines_by_id():
    return dict([(x.pubkey, x) for x in hardcoded_trampoline_nodes().values()])

is_hardcoded_trampoline = lambda node_id: node_id in trampolines_by_id().keys()

def encode_routing_info(r_tags):
    result = bitstring.BitArray()
    for route in r_tags:
        result.append(bitstring.pack('uint:8', len(route)))
        for step in route:
            pubkey, channel, feebase, feerate, cltv = step
            result.append(bitstring.BitArray(pubkey) + bitstring.BitArray(channel) + bitstring.pack('intbe:32', feebase) + bitstring.pack('intbe:32', feerate) + bitstring.pack('intbe:16', cltv))
    return result.tobytes()


def create_trampoline_route(
        *,
        amount_msat:int,
        min_cltv_expiry:int,
        invoice_pubkey:bytes,
        invoice_features:int,
        my_pubkey: bytes,
        trampoline_node_id,
        r_tags,
        trampoline_fee_level: int,
        use_two_trampolines: bool) -> LNPaymentRoute:

    invoice_features = LnFeatures(invoice_features)
    if invoice_features.supports(LnFeatures.OPTION_TRAMPOLINE_ROUTING_OPT)\
        or invoice_features.supports(LnFeatures.OPTION_TRAMPOLINE_ROUTING_OPT_ECLAIR):
        is_legacy = False
    else:
        is_legacy = True

    # fee level. the same fee is used for all trampolines
    if trampoline_fee_level < len(TRAMPOLINE_FEES):
        params = TRAMPOLINE_FEES[trampoline_fee_level]
    else:
        raise NoPathFound()
    # temporary fix: until ACINQ uses a proper feature bit to detect
    # Phoenix, they might try to open channels when payments fail
    if trampoline_node_id == TRAMPOLINE_NODES_MAINNET['x1 ninja'].pubkey:
        is_legacy = True
        use_two_trampolines = False
    # add optional second trampoline
    trampoline2 = None
    if is_legacy and use_two_trampolines:
        trampoline2_list = list(trampolines_by_id().keys())
        random.shuffle(trampoline2_list)
        for node_id in trampoline2_list:
            if node_id != trampoline_node_id:
                trampoline2 = node_id
                break
    # node_features is only used to determine is_tlv
    trampoline_features = LnFeatures.VAR_ONION_OPT
    # hop to trampoline
    route = []
    # trampoline hop
    route.append(
        TrampolineEdge(
            start_node=my_pubkey,
            end_node=trampoline_node_id,
            fee_base_msat=params['fee_base_msat'],
            fee_proportional_millionths=params['fee_proportional_millionths'],
            cltv_expiry_delta=params['cltv_expiry_delta'],
            node_features=trampoline_features))
    if trampoline2:
        route.append(
            TrampolineEdge(
                start_node=trampoline_node_id,
                end_node=trampoline2,
                fee_base_msat=params['fee_base_msat'],
                fee_proportional_millionths=params['fee_proportional_millionths'],
                cltv_expiry_delta=params['cltv_expiry_delta'],
                node_features=trampoline_features))
    # add routing info
    if is_legacy:
        invoice_routing_info = encode_routing_info(r_tags)
        route[-1].invoice_routing_info = invoice_routing_info
        route[-1].invoice_features = invoice_features
        route[-1].outgoing_node_id = invoice_pubkey
    else:
        last_trampoline = route[-1].end_node
        r_tags = [x for x in r_tags if len(x) == 1]
        random.shuffle(r_tags)
        for r_tag in r_tags:
            pubkey, scid, feebase, feerate, cltv = r_tag[0]
            if pubkey == trampoline_node_id:
                break
        else:
            pubkey, scid, feebase, feerate, cltv = r_tag[0]
            if route[-1].node_id != pubkey:
                route.append(
                    TrampolineEdge(
                        start_node=route[-1].node_id,
                        end_node=pubkey,
                        fee_base_msat=feebase,
                        fee_proportional_millionths=feerate,
                        cltv_expiry_delta=cltv,
                        node_features=trampoline_features))

    # Final edge (not part of the route if payment is legacy, but eclair requires an encrypted blob)
    route.append(
        TrampolineEdge(
            start_node=route[-1].end_node,
            end_node=invoice_pubkey,
            fee_base_msat=0,
            fee_proportional_millionths=0,
            cltv_expiry_delta=0,
            node_features=trampoline_features))
    # check that we can pay amount and fees
    for edge in route[::-1]:
        amount_msat += edge.fee_for_edge(amount_msat)
    if not is_route_sane_to_use(route, amount_msat, min_cltv_expiry):
        raise NoPathFound()
    _logger.info(f'created route with trampoline: fee_level={trampoline_fee_level}, is legacy: {is_legacy}')
    _logger.info(f'first trampoline: {trampoline_node_id.hex()}')
    _logger.info(f'second trampoline: {trampoline2.hex() if trampoline2 else None}')
    _logger.info(f'params: {params}')
    return route


def create_trampoline_onion(*, route, amount_msat, final_cltv, total_msat, payment_hash, payment_secret):
    # all edges are trampoline
    hops_data, amount_msat, cltv = calc_hops_data_for_payment(
        route,
        amount_msat,
        final_cltv,
        total_msat=total_msat,
        payment_secret=payment_secret)
    # detect trampoline hops.
    payment_path_pubkeys = [x.node_id for x in route]
    num_hops = len(payment_path_pubkeys)
    for i in range(num_hops):
        route_edge = route[i]
        assert route_edge.is_trampoline()
        payload = hops_data[i].payload
        if i < num_hops - 1:
            payload.pop('short_channel_id')
            next_edge = route[i+1]
            assert next_edge.is_trampoline()
            hops_data[i].payload["outgoing_node_id"] = {"outgoing_node_id":next_edge.node_id}
        # only for final
        if i == num_hops - 1:
            payload["payment_data"] = {
                "payment_secret":payment_secret,
                "total_msat": total_msat
            }
        # legacy
        if i == num_hops - 2 and route_edge.invoice_features:
            payload["invoice_features"] = {"invoice_features":route_edge.invoice_features}
            payload["invoice_routing_info"] = {"invoice_routing_info":route_edge.invoice_routing_info}
            payload["payment_data"] = {
                "payment_secret":payment_secret,
                "total_msat": total_msat
            }
        _logger.info(f'payload {i} {payload}')
    trampoline_session_key = os.urandom(32)
    trampoline_onion = new_onion_packet(payment_path_pubkeys, trampoline_session_key, hops_data, associated_data=payment_hash, trampoline=True)
    return trampoline_onion, amount_msat, cltv


def create_trampoline_route_and_onion(
        *,
        amount_msat,
        total_msat,
        min_cltv_expiry,
        invoice_pubkey,
        invoice_features,
        my_pubkey: bytes,
        node_id,
        r_tags,
        payment_hash,
        payment_secret,
        local_height:int,
        trampoline_fee_level: int,
        use_two_trampolines: bool):
    # create route for the trampoline_onion
    trampoline_route = create_trampoline_route(
        amount_msat=amount_msat,
        min_cltv_expiry=min_cltv_expiry,
        my_pubkey=my_pubkey,
        invoice_pubkey=invoice_pubkey,
        invoice_features=invoice_features,
        trampoline_node_id=node_id,
        r_tags=r_tags,
        trampoline_fee_level=trampoline_fee_level,
        use_two_trampolines=use_two_trampolines)
    # compute onion and fees
    final_cltv = local_height + min_cltv_expiry
    trampoline_onion, amount_with_fees, bucket_cltv = create_trampoline_onion(
        route=trampoline_route,
        amount_msat=amount_msat,
        final_cltv=final_cltv,
        total_msat=total_msat,
        payment_hash=payment_hash,
        payment_secret=payment_secret)
    bucket_cltv_delta = bucket_cltv - local_height
    bucket_cltv_delta += trampoline_route[0].cltv_expiry_delta
    # trampoline fee for this very trampoline
    trampoline_fee = trampoline_route[0].fee_for_edge(amount_with_fees)
    amount_with_fees += trampoline_fee
    return trampoline_onion, amount_with_fees, bucket_cltv_delta
