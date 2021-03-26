from hashlib import sha256
from decimal import Decimal
from binascii import unhexlify, hexlify
import pprint
import unittest

from electrum_mona.lnaddr import shorten_amount, unshorten_amount, LnAddr, lnencode, lndecode, u5_to_bitarray, bitarray_to_u5
from electrum_mona.segwit_addr import bech32_encode, bech32_decode
from electrum_mona import segwit_addr
from electrum_mona.lnutil import UnknownEvenFeatureBits, derive_payment_secret_from_payment_preimage, LnFeatures

from . import ElectrumTestCase


RHASH=unhexlify('0001020304050607080900010203040506070809000102030405060708090102')
CONVERSION_RATE=1200
PRIVKEY=unhexlify('e126f68f7eafcc8b74f54d269fe206be715000f94dac067d1c04a8ca3b2db734')
PUBKEY=unhexlify('03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad')


class TestBolt11(ElectrumTestCase):
    maxDiff = None
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

        timestamp = 1615922274
        tests = [
            (LnAddr(date=timestamp, paymenthash=RHASH, tags=[('d', '')]),
             "lnmona1ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdqqyhhfge73xtqkqr3ca22rvu3hyxfmesxahwyxdh3tya02p7x7ah3qt6zz4s5yn25z6hh4urf8c3598sdl8zxjpph0fg35y0kfn8vq6vsqd340h9"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=Decimal('0.001'), tags=[('d', '1 cup coffee'), ('x', 60)]),
             "lnmona1m1ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5xysxxatsyp3k7enxv4jsxqzpu206axye9c7fz0sc6y6f2e97l48mgpxv3r6v5k8rt7ce082fl64vskpcxvypnmjeg5amxe79sylp900rxgv2k8el535c0y22807v4ggsqglal97"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=Decimal('1'), tags=[('h', longdescription)]),
             "lnmona11ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs2hgyzzwfazhwxpj3edw9rw3gmsmcl3ktrzdeh3nkldnhzc0g6gfpkg3sqzx2dhuzetqsq6weypkegn3sfcg2tqyv0eyf6u7yq8rqw3gp764v5x"),
            (LnAddr(date=timestamp, paymenthash=RHASH, currency='tmona', tags=[('f', 'mivTxWUqB6yxQdbLnAfcTSaVXouAhTUDfs'), ('h', longdescription)]),
             "lntmona1ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3y4dtfd4mcpuul3wmteaxatgldveymxxyhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsq06ue05mjfwgnra27g6tnhzywtj7qh5rhuutf77apa7dclddp4nz0zwjcvqm4j8fd2pm2u8rwultx232yvdxsmh5fueffjexfuzn40gpaz4tq5"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[
                ('r', [(unhexlify('029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'), unhexlify('0102030405060708'), 1, 20, 3),
                       (unhexlify('039e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'), unhexlify('030405060708090a'), 2, 30, 4)]),
                ('f', 'MRHx4jW2KAQeEDMuK7pGLUGWvPRQT1Epmj'),
                ('h', longdescription)]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqr9yq20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqqpqqqqq9qqqvpeuqafqxu92d8lr6fvg0r5gv0heeeqgcrqlnm6jhphu9y00rrhy4grqszsvpcgpy9qqqqqqgqqqqq7qqzqfpp3hmyccldvzvekns7z4cmvu0lsg7stk9r2hp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs0m55wzqx4wrwhx27e9q830ua7gf0q8ft8axr6td50ztezsh84ra4ql6za2yk8462x4c7n3agqvtc6rxaug7f8udpv7faq0czepz3q0gp5zm5qk"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('f', 'PHjTKtgYLTJ9D2Bzw2f6xBB41KBm2HeGfg'), ('h', longdescription)]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppjv3yl26xfe53hsyu0ycmwz4n3z2scf20ghp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs94ex52vmwdkq0rsxjr8r7k8k40egy745aqlws0yk7j793zv5tqfq4arqjlw7peu8r62hvpkcqjquuztgst47vpzqzt8ju8c36gqx2tgp3jmyzn"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('f', 'mona1quunc907zfyj7cyxhnp9584rj0wmdka2ec9w3af'), ('h', longdescription)]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppquunc907zfyj7cyxhnp9584rj0wmdka2ehp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsqvn67ssxdtqakqvxfy4lsen8sqw4pzd2j230lz7dx6chd737csyjcfe93dc4s099faaeg37us2dzt0pwfrtfnp429k40vfu06qpf28squq5wy0"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('f', 'mona1qp8f842ywwr9h5rdxyzggex7q3trvvvaarfssxccju52rj6htfzfsqr79j2'), ('h', longdescription)]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfp4qp8f842ywwr9h5rdxyzggex7q3trvvvaarfssxccju52rj6htfzfshp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsd45jh4k2e8jvhzpthqyc2sspr30k3pg67f4a973qumvw48t4gzl4tdr9qh7p04z5afghspsapvp3tahcq7rasw7dtv2vv46sm79479qpm9jdjl"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('n', PUBKEY), ('h', longdescription)]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqnp4q0n326hr8v9zprg8gsvezcch06gfaqqhde2aj730yg0durunfhv66hp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsdcmmg0p9qn003ls0r8dv2f9d7xh7lfx6lsha7h5azxzfdd292r4yuflmhs3dkkghmzaecedwzrvxktsnrhcfmsnx7r64chxw5phrwggq32hqsz"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 514)]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qzszz2jjnvrh9rg877px70r5cfrf0vqwzws0jxmcg3d4pqg0ml337s8qsmxjyedvssge254qjwucnjy3rtzr7gxzfatsy3ad5x4c0ll93acq3rwstg"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 8))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qzg2vwag8ax9f9wkmsz37nvq8qkq53tpznev8jjnkezq7u8qzzytad85zhxgk7hqgqkqrftazq8hfr6lv9q4j4vk2ld6ymrjtsnumetlhjqqe7cl7z"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 9))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qzs2p8uyuepjhdpyfsv6xuc0enx57upz4sdz0n38s7mfc07lpm5vvc9zdursykxpz8heddckdg2d6wsjltuf93rrewptuekp5s9w06wucacqgjaara"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 7) + (1 << 11))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qrzy2xw96qw57wvauu8skgsvlpnvqluwy4txpm7pw3q9r70lryezhvjrjj9f7tuage9une2hn26quv9fpm9wa4h672288m5ek4jk4gh2cm5sqlkg3yn"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 12))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qryq29tefcvke7zl35fjehvn0t3vnw2uae766g7gxuj23tk4vfsxjzk2n45vnms6ew2pvydlhy7vfxptnwcs0x7qjuct0feg4vryzl3trvlspfvn5v7"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 13))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qrgq2yctvzkmsa8w0elyd7gx5wp5lflsx8wsqw5l2ejytgd3q5qrwjkckvqsjamwq93eekje8qwzphsjh9hcy3lmpvrdlks8tmutuad3k9eqquhzhfz"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 9) + (1 << 14))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qrss2dccexrncjpgvjfy93t507h07l63qt7k7fp3zeptdqadv9jmulu6hfa6syjwqqrvjf3a9fu50ap0vtjtrmyrqzjg46are0apf6hq6ztqqfhkr7e"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 10 + (1 << 9) + (1 << 15))]),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qypqs29trq3u6ctz9qnm4hate5u74f0w6j4tcjj3wr79czn4n48egmze98kwk8wt6e6cj5890jpd8dvwfttua2qullslfyf04save5fnvgp9sqkusukq"),
            (LnAddr(date=timestamp, paymenthash=RHASH, amount=24, tags=[('h', longdescription), ('9', 33282)], payment_secret=b"\x11" * 32),
             "lnmona241ps9zprzpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygshp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9qypqsz29tu4q7pmhu58qywk2mfd5vpuscy308del7mq76pywkqtjz36f240cgcxrpuzzzzprw7gvnwvwn6vxnpm7dtg2t258f0zy0zl7ldnrcpvzyrkz"),
        ]

        # Roundtrip
        for lnaddr1, invoice_str1 in tests:
            invoice_str2 = lnencode(lnaddr1, PRIVKEY)
            self.assertEqual(invoice_str1, invoice_str2)
            lnaddr2 = lndecode(invoice_str2, expected_hrp=lnaddr1.currency)
            self.compare(lnaddr1, lnaddr2)

    def test_n_decoding(self):
        # We flip the signature recovery bit, which would normally give a different
        # pubkey.
        _, hrp, data = bech32_decode(
            lnencode(LnAddr(paymenthash=RHASH, amount=24, tags=[('d', '')]), PRIVKEY),
            ignore_long_length=True)
        databits = u5_to_bitarray(data)
        databits.invert(-1)
        lnaddr = lndecode(bech32_encode(segwit_addr.Encoding.BECH32, hrp, bitarray_to_u5(databits)), verbose=True)
        assert lnaddr.pubkey.serialize() != PUBKEY

        # But not if we supply expliciy `n` specifier!
        _, hrp, data = bech32_decode(
            lnencode(LnAddr(paymenthash=RHASH, amount=24, tags=[('d', ''), ('n', PUBKEY)]), PRIVKEY),
            ignore_long_length=True)
        databits = u5_to_bitarray(data)
        databits.invert(-1)
        lnaddr = lndecode(bech32_encode(segwit_addr.Encoding.BECH32, hrp, bitarray_to_u5(databits)), verbose=True)
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
        self.assertEqual(LnFeatures(514), lnaddr.get_features())

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
