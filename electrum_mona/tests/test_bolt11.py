from hashlib import sha256
from decimal import Decimal
from binascii import unhexlify, hexlify
import pprint
import unittest

from electrum_mona.lnaddr import shorten_amount, unshorten_amount, LnAddr, lnencode, lndecode, u5_to_bitarray, bitarray_to_u5
from electrum_mona.segwit_addr import bech32_encode, bech32_decode
from electrum_mona.lnutil import UnknownEvenFeatureBits, derive_payment_secret_from_payment_preimage

from . import ElectrumTestCase


RHASH=unhexlify('0001020304050607080900010203040506070809000102030405060708090102')
CONVERSION_RATE=1200
PRIVKEY=unhexlify('e126f68f7eafcc8b74f54d269fe206be715000f94dac067d1c04a8ca3b2db734')
PUBKEY=unhexlify('03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad')


class TestBolt11(ElectrumTestCase):
    def test_shorten_amount(self):
        tests = {
            Decimal(10)/10**12: '10p',
            Decimal(1000)/10**12: '1n',
            Decimal(1200)/10**12: '1200p',
            Decimal(123)/10**6: '123u',
            Decimal(123)/1000: '123m',
            Decimal(3): '3',
        }

        for i, o in tests.items():
            assert shorten_amount(i) == o
            assert unshorten_amount(shorten_amount(i)) == i

    @staticmethod
    def compare(a, b):

        if len([t[1] for t in a.tags if t[0] == 'h']) == 1:
            h1 = sha256([t[1] for t in a.tags if t[0] == 'h'][0].encode('utf-8')).digest()
            h2 = [t[1] for t in b.tags if t[0] == 'h'][0]
            assert h1 == h2

        # Need to filter out these, since they are being modified during
        # encoding, i.e., hashed
        a.tags = [t for t in a.tags if t[0] != 'h' and t[0] != 'n']
        b.tags = [t for t in b.tags if t[0] != 'h' and t[0] != 'n']

        assert b.pubkey.serialize() == PUBKEY, (hexlify(b.pubkey.serialize()), hexlify(PUBKEY))
        assert b.signature != None

        # Unset these, they are generated during encoding/decoding
        b.pubkey = None
        b.signature = None

        assert a.__dict__ == b.__dict__, (pprint.pformat([a.__dict__, b.__dict__]))

    def test_roundtrip(self):
        longdescription = ('One piece of chocolate cake, one icecream cone, one'
                          ' pickle, one slice of swiss cheese, one slice of salami,'
                          ' one lollypop, one piece of cherry pie, one sausage, one'
                          ' cupcake, and one slice of watermelon')


        tests = [
            LnAddr(paymenthash=RHASH, tags=[('d', '')]),
            LnAddr(paymenthash=RHASH, amount=Decimal('0.001'), tags=[('d', '1 cup coffee'), ('x', 60)]),
            LnAddr(paymenthash=RHASH, amount=Decimal('1'), tags=[('h', longdescription)]),
            LnAddr(paymenthash=RHASH, currency='tmona', tags=[('f', 'mivTxWUqB6yxQdbLnAfcTSaVXouAhTUDfs'), ('h', longdescription)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[
                ('r', [(unhexlify('029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'), unhexlify('0102030405060708'), 1, 20, 3),
                       (unhexlify('039e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'), unhexlify('030405060708090a'), 2, 30, 4)]),
                ('f', 'MRHx4jW2KAQeEDMuK7pGLUGWvPRQT1Epmj'),
                ('h', longdescription)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('f', 'PHjTKtgYLTJ9D2Bzw2f6xBB41KBm2HeGfg'), ('h', longdescription)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('f', 'mona1quunc907zfyj7cyxhnp9584rj0wmdka2ec9w3af'), ('h', longdescription)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('f', 'mona1qp8f842ywwr9h5rdxyzggex7q3trvvvaarfssxccju52rj6htfzfsqr79j2'), ('h', longdescription)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('n', PUBKEY), ('h', longdescription)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 514)]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 8))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 9))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 7) + (1 << 11))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 12))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 13))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 9) + (1 << 14))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 9) + (1 << 15))]),
            LnAddr(paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 33282)], payment_secret=b"\x11" * 32),
        ]

        # Roundtrip
        for t in tests:
            o = lndecode(lnencode(t, PRIVKEY), expected_hrp=t.currency)
            self.compare(t, o)

    def test_n_decoding(self):
        # We flip the signature recovery bit, which would normally give a different
        # pubkey.
        hrp, data = bech32_decode(lnencode(LnAddr(paymenthash=RHASH, amount=24, tags=[('d', '')]), PRIVKEY), True)
        databits = u5_to_bitarray(data)
        databits.invert(-1)
        lnaddr = lndecode(bech32_encode(hrp, bitarray_to_u5(databits)), verbose=True)
        assert lnaddr.pubkey.serialize() != PUBKEY

        # But not if we supply expliciy `n` specifier!
        hrp, data = bech32_decode(lnencode(LnAddr(paymenthash=RHASH, amount=24,
                                                  tags=[('d', ''),
                                                        ('n', PUBKEY)]),
                                           PRIVKEY), True)
        databits = u5_to_bitarray(data)
        databits.invert(-1)
        lnaddr = lndecode(bech32_encode(hrp, bitarray_to_u5(databits)), verbose=True)
        assert lnaddr.pubkey.serialize() == PUBKEY

    def test_min_final_cltv_expiry_decoding(self):
        lnaddr = lndecode("lnsmona25m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5vdhkven9v5sxyetpdeescqzyssp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygsj7dv5y27jkfl9y2vxu8jddmgmk4av25j80vwesnwejd089805a5z6gupm4cn23h0k6gaj8nnakm3jz4ujvcwkljgm7jr2zgu3s9uz2gqgdx8jp",
                          expected_hrp="smona")
        self.assertEqual(144, lnaddr.get_min_final_cltv_expiry())

        lnaddr = lndecode("lntb15u1p0m6lzupp5zqjthgvaad9mewmdjuehwddyze9d8zyxcc43zhaddeegt37sndgsdq4xysyymr0vd4kzcmrd9hx7cqp7xqrrss9qy9qsqsp5vlhcs24hwm747w8f3uau2tlrdkvjaglffnsstwyamj84cxuhrn2s8tut3jqumepu42azyyjpgqa4w9w03204zp9h4clk499y2umstl6s29hqyj8vv4as6zt5567ux7l3f66m8pjhk65zjaq2esezk7ll2kcpljewkg",
                          expected_hrp="tb")
        self.assertEqual(30, lnaddr.get_min_final_cltv_expiry())

    def test_min_final_cltv_expiry_roundtrip(self):
        for cltv in (1, 15, 16, 31, 32, 33, 150, 511, 512, 513, 1023, 1024, 1025):
            lnaddr = LnAddr(paymenthash=RHASH, amount=Decimal('0.001'), tags=[('d', '1 cup coffee'), ('x', 60), ('c', cltv)])
            invoice = lnencode(lnaddr, PRIVKEY)
            self.assertEqual(cltv, lndecode(invoice).get_min_final_cltv_expiry())

    def test_features(self):
        lnaddr = lndecode("lnmona25m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5vdhkven9v5sxyetpdees9qzszsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygsw78e7nnjh75hssadjykhm85834l3q4juymunsryzewwhy43kaaeprmxnn4w8uvmpem60flrcpxr4sey558yrh2lwgdhv4z5a4lculqgqm5ng34")
        self.assertEqual(514, lnaddr.get_tag('9'))

        with self.assertRaises(UnknownEvenFeatureBits):
            lndecode("lnmona25m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5vdhkven9v5sxyetpdees9qw7rhsay5tm4cuw8sp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygsq99ctuk92pu45k27shadaafncl0jea0m6r82mxl037s4ujv423az7ucn734zydafexf2eft3wufyyck73qz39acv9nxc50nxkvjhnpgph9l9yw")

    def test_payment_secret(self):
        lnaddr = lndecode("lnmona25m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5vdhkven9v5sxyetpdees9q5sqqqqqqqqqqqqqqqpqsqsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygsguc039ze757wlyqcsr0wtqwpp05mtf9af77e65x2tv55q8cg09682rlyll2u8gdluztskrypzdhl468m6dl7dxzaujvfvlj906njlrcplhts8n")
        self.assertEqual((1 << 9) + (1 << 15) + (1 << 99), lnaddr.get_tag('9'))
        self.assertEqual(b"\x11" * 32, lnaddr.payment_secret)

    def test_derive_payment_secret_from_payment_preimage(self):
        preimage = bytes.fromhex("cc3fc000bdeff545acee53ada12ff96060834be263f77d645abbebc3a8d53b92")
        self.assertEqual("bfd660b559b3f452c6bb05b8d2906f520c151c107b733863ed0cc53fc77021a8",
                         derive_payment_secret_from_payment_preimage(preimage).hex())
