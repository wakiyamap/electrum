import shutil
import tempfile
import os

from electrum_mona import constants, blockchain
from electrum_mona.simple_config import SimpleConfig
from electrum_mona.blockchain import Blockchain, deserialize_header, hash_header
from electrum_mona.util import bh2u, bfh, make_dir

from . import ElectrumTestCase


class TestBlockchain(ElectrumTestCase):

    HEADERS = {
        'A': deserialize_header(bfh("0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff7f2002000000"), 0),
        'B': deserialize_header(bfh("0000002006226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f186c8dfd970a4545f79916bc1d75c9d00432f57c89209bf3bb115b7612848f509c25f45bffff7f2000000000"), 1),
        'C': deserialize_header(bfh("00000020686bdfc6a3db73d5d93e8c9663a720a26ecb1ef20eb05af11b36cdbc57c19f7ebf2cbf153013a1c54abaf70e95198fcef2f3059cc6b4d0f7e876808e7d24d11cc825f45bffff7f2000000000"), 2),
        'D': deserialize_header(bfh("00000020122baa14f3ef54985ae546d1611559e3f487bd2a0f46e8dbb52fbacc9e237972e71019d7feecd9b8596eca9a67032c5f4641b23b5d731dc393e37de7f9c2f299e725f45bffff7f2000000000"), 3),
        'E': deserialize_header(bfh("00000020f8016f7ef3a17d557afe05d4ea7ab6bde1b2247b7643896c1b63d43a1598b747a3586da94c71753f27c075f57f44faf913c31177a0957bbda42e7699e3a2141aed25f45bffff7f2001000000"), 4),
        'F': deserialize_header(bfh("000000201d589c6643c1d121d73b0573e5ee58ab575b8fdf16d507e7e915c5fbfbbfd05e7aee1d692d1615c3bdf52c291032144ce9e3b258a473c17c745047f3431ff8e2ee25f45bffff7f2000000000"), 5),
        'O': deserialize_header(bfh("00000020b833ed46eea01d4c980f59feee44a66aa1162748b6801029565d1466790c405c3a141ce635cbb1cd2b3a4fcdd0a3380517845ba41736c82a79cab535d31128066526f45bffff7f2001000000"), 6),
        'P': deserialize_header(bfh("00000020abe8e119d1877c9dc0dc502d1a253fb9a67967c57732d2f71ee0280e8381ff0a9690c2fe7c1a4450c74dc908fe94dd96c3b0637d51475e9e06a78e944a0c7fe28126f45bffff7f2000000000"), 7),
        'Q': deserialize_header(bfh("000000202ce41d94eb70e1518bc1f72523f84a903f9705d967481e324876e1f8cf4d3452148be228a4c3f2061bafe7efdfc4a8d5a94759464b9b5c619994d45dfcaf49e1a126f45bffff7f2000000000"), 8),
        'R': deserialize_header(bfh("00000020552755b6c59f3d51e361d16281842a4e166007799665b5daed86a063dd89857415681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a462555822552221a626f45bffff7f2000000000"), 9),
        'S': deserialize_header(bfh("00000020a13a491cbefc93cd1bb1938f19957e22a134faf14c7dee951c45533e2c750f239dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548fab26f45bffff7f2000000000"), 10),
        'T': deserialize_header(bfh("00000020dbf3a9b55dfefbaf8b6e43a89cf833fa2e208bbc0c1c5d76c0d71b9e4a65337803b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe064b026f45bffff7f2002000000"), 11),
        'U': deserialize_header(bfh("000000203d0932b3b0c78eccb39a595a28ae4a7c966388648d7783fd1305ec8d40d4fe5fd67cb902a7d807cee7676cb543feec3e053aa824d5dfb528d5b94f9760313d9db726f45bffff7f2001000000"), 12),
        'G': deserialize_header(bfh("00000020b833ed46eea01d4c980f59feee44a66aa1162748b6801029565d1466790c405c3a141ce635cbb1cd2b3a4fcdd0a3380517845ba41736c82a79cab535d31128066928f45bffff7f2001000000"), 6),
        'H': deserialize_header(bfh("00000020e19e687f6e7f83ca394c114144dbbbc4f3f9c9450f66331a125413702a2e1a719690c2fe7c1a4450c74dc908fe94dd96c3b0637d51475e9e06a78e944a0c7fe26a28f45bffff7f2002000000"), 7),
        'I': deserialize_header(bfh("0000002009dcb3b158293c89d7cf7ceeb513add122ebc3880a850f47afbb2747f5e48c54148be228a4c3f2061bafe7efdfc4a8d5a94759464b9b5c619994d45dfcaf49e16a28f45bffff7f2000000000"), 8),
        'J': deserialize_header(bfh("000000206a65f3bdd3374a5a6c4538008ba0b0a560b8566291f9ef4280ab877627a1742815681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a462555822552221c928f45bffff7f2000000000"), 9),
        'K': deserialize_header(bfh("00000020bb3b421653548991998f96f8ba486b652fdb07ca16e9cee30ece033547cd1a6e9dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548fca28f45bffff7f2000000000"), 10),
        'L': deserialize_header(bfh("00000020c391d74d37c24a130f4bf4737932bdf9e206dd4fad22860ec5408978eb55d46303b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe064ca28f45bffff7f2000000000"), 11),
        'M': deserialize_header(bfh("000000206a65f3bdd3374a5a6c4538008ba0b0a560b8566291f9ef4280ab877627a1742815681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a4625558225522214229f45bffff7f2000000000"), 9),
        'N': deserialize_header(bfh("00000020383dab38b57f98aa9b4f0d5ff868bc674b4828d76766bf048296f4c45fff680a9dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548f4329f45bffff7f2003000000"), 10),
        'X': deserialize_header(bfh("0000002067f1857f54b7fef732cb4940f7d1b339472b3514660711a820330fd09d8fba6b03b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe0649b29f45bffff7f2002000000"), 11),
        'Y': deserialize_header(bfh("00000020db33c9768a9e5f7c37d0f09aad88d48165946c87d08f7d63793f07b5c08c527fd67cb902a7d807cee7676cb543feec3e053aa824d5dfb528d5b94f9760313d9d9b29f45bffff7f2000000000"), 12),
        'Z': deserialize_header(bfh("0000002047822b67940e337fda38be6f13390b3596e4dea2549250256879722073824e7f0f2596c29203f8a0f71ae94193092dc8f113be3dbee4579f1e649fa3d6dcc38c622ef45bffff7f2003000000"), 13),
    }
    # tree of headers:
    #                                            - M <- N <- X <- Y <- Z
    #                                          /
    #                             - G <- H <- I <- J <- K <- L
    #                           /
    # A <- B <- C <- D <- E <- F <- O <- P <- Q <- R <- S <- T <- U

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        constants.set_regtest()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        constants.set_mainnet()

    def setUp(self):
        super().setUp()
        self.data_dir = self.electrum_path
        make_dir(os.path.join(self.data_dir, 'forks'))
        self.config = SimpleConfig({'electrum_path': self.data_dir})
        blockchain.blockchains = {}

    def _append_header(self, chain: Blockchain, header: dict):
        chain.save_header(header)

    def test_get_height_of_last_common_block_with_chain(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

    def test_parents_after_forking(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

    def test_forking_and_swapping(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])

        self._append_header(chain_l, self.HEADERS['K'])

        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

#    def test_doing_multiple_swaps_after_single_new_header(self):
#        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
#            config=self.config, forkpoint=0, parent=None,
#            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
#        open(chain_u.path(), 'w+').close()

#        self._append_header(chain_u, self.HEADERS['A'])
#        self._append_header(chain_u, self.HEADERS['B'])
#        self._append_header(chain_u, self.HEADERS['C'])
#        self._append_header(chain_u, self.HEADERS['D'])
#        self._append_header(chain_u, self.HEADERS['E'])
#        self._append_header(chain_u, self.HEADERS['F'])
#        self._append_header(chain_u, self.HEADERS['O'])
#        self._append_header(chain_u, self.HEADERS['P'])
#        self._append_header(chain_u, self.HEADERS['Q'])
#        self._append_header(chain_u, self.HEADERS['R'])
#        self._append_header(chain_u, self.HEADERS['S'])

#        chain_l = chain_u.fork(self.HEADERS['G'])
#        self._append_header(chain_l, self.HEADERS['H'])
#        self._append_header(chain_l, self.HEADERS['I'])
#        self._append_header(chain_l, self.HEADERS['J'])
#        self._append_header(chain_l, self.HEADERS['K'])
#        # now chain_u is best chain, but it's tied with chain_l

#        chain_z = chain_l.fork(self.HEADERS['M'])
#        self._append_header(chain_z, self.HEADERS['N'])
#        self._append_header(chain_z, self.HEADERS['X'])

#        self.assertEqual(3, len(blockchain.blockchains))
#        self.assertEqual(2, len(os.listdir(os.path.join(self.data_dir, "forks"))))

#        # chain_z became best chain, do checks
#        self.assertEqual(0, chain_z.forkpoint)
#        self.assertEqual(None, chain_z.parent)
#        self.assertEqual(constants.net.GENESIS, chain_z._forkpoint_hash)
#        self.assertEqual(None, chain_z._prev_hash)
#        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_z.path())
#        self.assertEqual(12 * 80, os.stat(chain_z.path()).st_size)
#        self.assertEqual(9, chain_l.forkpoint)
#        self.assertEqual(chain_z, chain_l.parent)
#        self.assertEqual(hash_header(self.HEADERS['J']), chain_l._forkpoint_hash)
#        self.assertEqual(hash_header(self.HEADERS['I']), chain_l._prev_hash)
#        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_9_2874a1277687ab8042eff9916256b860a5b0a08b0038456c5a4a37d3bdf3656a_6e1acd473503ce0ee3cee916ca07db2f656b48baf8968f999189545316423bbb"), chain_l.path())
#        self.assertEqual(2 * 80, os.stat(chain_l.path()).st_size)
#        self.assertEqual(6, chain_u.forkpoint)
#        self.assertEqual(chain_z, chain_u.parent)
#        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
#        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
#        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_5c400c7966145d56291080b6482716a16aa644eefe590f984c1da0ee46ed33b8_aff81830e28e01ef7d23277c56779a6b93f251a2d50dcc09d7c87d119e1e8ab"), chain_u.path())
#        self.assertEqual(5 * 80, os.stat(chain_u.path()).st_size)

#        self.assertEqual(constants.net.GENESIS, chain_z.get_hash(0))
#        self.assertEqual(hash_header(self.HEADERS['F']), chain_z.get_hash(5))
#        self.assertEqual(hash_header(self.HEADERS['G']), chain_z.get_hash(6))
#        self.assertEqual(hash_header(self.HEADERS['I']), chain_z.get_hash(8))
#        self.assertEqual(hash_header(self.HEADERS['M']), chain_z.get_hash(9))
#        self.assertEqual(hash_header(self.HEADERS['X']), chain_z.get_hash(11))

#        for b in (chain_u, chain_l, chain_z):
#            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))

    def get_chains_that_contain_header_helper(self, header: dict):
        height = header['block_height']
        header_hash = hash_header(header)
        return blockchain.get_chains_that_contain_header(height, header_hash)

#    def test_get_chains_that_contain_header(self):
#        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
#            config=self.config, forkpoint=0, parent=None,
#            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
#        open(chain_u.path(), 'w+').close()
#        self._append_header(chain_u, self.HEADERS['A'])
#        self._append_header(chain_u, self.HEADERS['B'])
#        self._append_header(chain_u, self.HEADERS['C'])
#        self._append_header(chain_u, self.HEADERS['D'])
#        self._append_header(chain_u, self.HEADERS['E'])
#        self._append_header(chain_u, self.HEADERS['F'])
#        self._append_header(chain_u, self.HEADERS['O'])
#        self._append_header(chain_u, self.HEADERS['P'])
#        self._append_header(chain_u, self.HEADERS['Q'])

#        chain_l = chain_u.fork(self.HEADERS['G'])
#        self._append_header(chain_l, self.HEADERS['H'])
#        self._append_header(chain_l, self.HEADERS['I'])
#        self._append_header(chain_l, self.HEADERS['J'])
#        self._append_header(chain_l, self.HEADERS['K'])
#        self._append_header(chain_l, self.HEADERS['L'])

#        chain_z = chain_l.fork(self.HEADERS['M'])

#        self.assertEqual([chain_l, chain_z, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['A']))
#        self.assertEqual([chain_l, chain_z, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['C']))
#        self.assertEqual([chain_l, chain_z, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['F']))
#        self.assertEqual([chain_l, chain_z], self.get_chains_that_contain_header_helper(self.HEADERS['G']))
#        self.assertEqual([chain_l, chain_z], self.get_chains_that_contain_header_helper(self.HEADERS['I']))
#        self.assertEqual([chain_z], self.get_chains_that_contain_header_helper(self.HEADERS['M']))
#        self.assertEqual([chain_l], self.get_chains_that_contain_header_helper(self.HEADERS['K']))

#        self._append_header(chain_z, self.HEADERS['N'])
#        self._append_header(chain_z, self.HEADERS['X'])
#        self._append_header(chain_z, self.HEADERS['Y'])
#        self._append_header(chain_z, self.HEADERS['Z'])

#        self.assertEqual([chain_z, chain_l, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['A']))
#        self.assertEqual([chain_z, chain_l, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['C']))
#        self.assertEqual([chain_z, chain_l, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['F']))
#        self.assertEqual([chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['O']))
#        self.assertEqual([chain_z, chain_l], self.get_chains_that_contain_header_helper(self.HEADERS['I']))


class TestVerifyHeader(ElectrumTestCase):

    # Data for Bitcoin block header #100.
    valid_header = "0100000095194b8567fe2e8bbda931afd01a7acd399b9325cb54683e64129bcd00000000660802c98f18fd34fd16d61c63cf447568370124ac5f3be626c2e1c3c9f0052d19a76949ffff001d33f3c25d"
    target = Blockchain.bits_to_target(0x1d00ffff)
    prev_hash = "00000000cd9b12643e6854cb25939b39cd7a1ad0af31a9bd8b2efe67854b1995"

    def setUp(self):
        super().setUp()
        self.header = deserialize_header(bfh(self.valid_header), 100)

    def test_valid_header(self):
        #Blockchain.verify_header(self.header, self.prev_hash, self.target)
        return

    def test_expected_hash_mismatch(self):
        #with self.assertRaises(Exception):
        #    Blockchain.verify_header(self.header, self.prev_hash, self.target,
        #                             expected_header_hash="foo")
        return

    def test_prev_hash_mismatch(self):
        #with self.assertRaises(Exception):
        #    Blockchain.verify_header(self.header, "foo", self.target)
        return

    def test_target_mismatch(self):
        #with self.assertRaises(Exception):
        #    other_target = Blockchain.bits_to_target(0x1d00eeee)
        #    Blockchain.verify_header(self.header, self.prev_hash, other_target)
        return

    def test_insufficient_pow(self):
        #with self.assertRaises(Exception):
        #    self.header["nonce"] = 42
        #    Blockchain.verify_header(self.header, self.prev_hash, self.target)
        return

    def test_get_target(self):

        # before DGWv3 with checkpoint(height=2015)
        headers1 = {2015: {'version': 2, 'prev_block_hash': 'f9cba205f996e98f61f87e32ae57fc0a5befa6cd632dd257f3e239f390010622', 'merkle_root': 'af68c1f62b965172df1d81fba95f193cb8e42431bad79a4bfbcc370d301d5710', 'timestamp': 1388536705, 'bits': 503936911, 'nonce': 780010496, 'block_height': 2015}}
        bits = Blockchain.get_target(self, 2015, headers1)
        self.assertEqual(bits, 65339010432214603900175979833807329994044402934458085644623414103638016)

        # before DGWv3 without checkpoint(height=2016)
        headers2 = {2015: {'version': 2, 'prev_block_hash': 'f9cba205f996e98f61f87e32ae57fc0a5befa6cd632dd257f3e239f390010622', 'merkle_root': 'af68c1f62b965172df1d81fba95f193cb8e42431bad79a4bfbcc370d301d5710', 'timestamp': 1388536705, 'bits': 503936911, 'nonce': 780010496, 'block_height': 2015}}
        bits = Blockchain.get_target(self, 2016, headers2)
        self.assertEqual(bits, 0)

        # after DGWv3 with checkpoint(height=461663)
        headers3 = {461663: {'version': 3, 'prev_block_hash': '9c87f1e27717aec18617496970b9744dd855f997128fab6733e709fd95d97870', 'merkle_root': '7f22e9001ab92b14a1b057ce07c4f2acecb693f3a645004f36c2246b7ea86c3b', 'timestamp': 1444439492, 'bits': 469801026, 'nonce': 928239, 'block_height': 461663}}
        bits = Blockchain.get_target(self, 461663, headers3)
        self.assertEqual(bits, 62635231089126922960074598435273835921110428291665699134377033728)

        # after DGWv3 without checkpoint(height=461664)
        headers4 = {461663: {'version': 3, 'prev_block_hash': '9c87f1e27717aec18617496970b9744dd855f997128fab6733e709fd95d97870', 'merkle_root': '7f22e9001ab92b14a1b057ce07c4f2acecb693f3a645004f36c2246b7ea86c3b', 'timestamp': 1444439492, 'bits': 469801026, 'nonce': 928239, 'block_height': 461663}}
        bits = Blockchain.get_target(self, 461664, headers4)
        self.assertEqual(bits, 0)

        # after DGWv3 after checkpoint(2206543)
        headers5 = {2206513: {'version': 536870912, 'prev_block_hash': '79f9cf8a46f1c823db1005a5f879bbc5e0c3250c516986b80679a900a465b37f', 'merkle_root': 'df6f4798d813f2e2545c538c579a97b95c4af4f522ac49401483a19e0de8d47d', 'timestamp': 1609444650, 'bits': 436604928, 'nonce': 2204928177, 'block_height': 2206513}, 2206514: {'version': 536870912, 'prev_block_hash': 'a3a9fa4099bfb3b251490be1e9f5a509cad82dc44c217d9a7ff1ac44f6e1b2fb', 'merkle_root': '06a9bb6b66584de4d3f9d5bfc44fcd894f7df4419787263918702370fb9cf0d7', 'timestamp': 1609444702, 'bits': 436625476, 'nonce': 329943414, 'block_height': 2206514}, 2206515: {'version': 536870912, 'prev_block_hash': '109b0bd3ea80416d1a97c0340b277feac76f6ee0297f3dfba00ece9f53f836f7', 'merkle_root': '71b4078000d4c47602222ff594c525d6b975c82dd25b3fd7fa67d3bad86d8386', 'timestamp': 1609444825, 'bits': 436632771, 'nonce': 1451552657, 'block_height': 2206515}, 2206516: {'version': 536870912, 'prev_block_hash': '1fb8ed778b8e8102ee7ceea672dc06d7f6faccc47582e909530ce6e46d7374d4', 'merkle_root': '57796791a3ea547a780a6bb8c6cab38c9565069af5f0616f7e205cc4f71cab04', 'timestamp': 1609444842, 'bits': 436624710, 'nonce': 2528808502, 'block_height': 2206516}, 2206517: {'version': 536870912, 'prev_block_hash': '5d389d2b68474a5f19e6a92e2e92ce567e948ad5aa0bf4e459aa87f5a5fca637', 'merkle_root': '5cbc97c215a95e75fe4bcbd5789bfb8a86792a738247b68426938b40e1504a4b', 'timestamp': 1609444994, 'bits': 436607628, 'nonce': 3198985056, 'block_height': 2206517}, 2206518: {'version': 536870912, 'prev_block_hash': '84815942d62032fcb2c5bc3b8991c09dde040190f63b9d9ebe46b340b2cd3d6c', 'merkle_root': 'c0da13cb17bff5bc2a2331ad6d41ba30eba738efffdefd3c38183faa9234612c', 'timestamp': 1609445310, 'bits': 436632069, 'nonce': 1627859591, 'block_height': 2206518}, 2206519: {'version': 536870912, 'prev_block_hash': 'c45cc191df1a721c6fa95201cb5e731825160f254f3ca5ff1ca9760a5822ee8b', 'merkle_root': '37860a177a12504292339d5c2f0e6ada37a3602b1d1734e6ae9d4c41ea59f54d', 'timestamp': 1609445334, 'bits': 436631610, 'nonce': 2638329250, 'block_height': 2206519}, 2206520: {'version': 536870912, 'prev_block_hash': 'adf2460927e1e4aad0bf1523323e07b127c35345add7a747f31a7c91121ff63e', 'merkle_root': '9170108d7c0c9259592afa4de3d3e7050e08a735d124318c734e2abf8f6664a6', 'timestamp': 1609445589, 'bits': 436576387, 'nonce': 3625981221, 'block_height': 2206520}, 2206521: {'version': 536870912, 'prev_block_hash': 'a21753dbaf91b13f9201907987a94f24ec733c5c135c98a9e745802ddd99eeca', 'merkle_root': '14fc0e2c98fddfcc4dfc4a06ecfa25789cef80a3db7a3eb6fe1c1f7b5c58a09e', 'timestamp': 1609445713, 'bits': 436624231, 'nonce': 3913376559, 'block_height': 2206521}, 2206522: {'version': 536870912, 'prev_block_hash': 'c015a44dca079df75b4359cef86a56c0c83daafd99ee7f4e4e6a3b973e3cf68d', 'merkle_root': '846fff888522311773f8e799934ba37dff875e768540dcdf3096cff3faaa70d0', 'timestamp': 1609445772, 'bits': 436630768, 'nonce': 2444283459, 'block_height': 2206522}, 2206523: {'version': 536870912, 'prev_block_hash': '4a68c57457302e8dfcce11b2bfd687dfd676d7ee73b6de4f8c7c1ea7c7caa8d5', 'merkle_root': 'f89d5a02a3e60fa0d0a76548755ee10f657fe8cf14d20c195df661c0395dc2df', 'timestamp': 1609445813, 'bits': 436632462, 'nonce': 1189974575, 'block_height': 2206523}, 2206524: {'version': 536870912, 'prev_block_hash': 'f8fb4f308a3059f427ab617976f0f8f997f9f85c23ee1155204b30897ae32004', 'merkle_root': '1d4de9345567a065e1524fd56465f59eee2732fb3d4d29c41447ba2aa676dedc', 'timestamp': 1609445829, 'bits': 436624998, 'nonce': 3623875361, 'block_height': 2206524}, 2206525: {'version': 536870912, 'prev_block_hash': '1a397adbec8fbabcbb17194f4785f2e47f4335b76c04a30421dfaa422f04cd15', 'merkle_root': '428a9bc92c90cb7e924415f9d9677fc76edb82289b1145be99611200c3ee0a34', 'timestamp': 1609445845, 'bits': 436616917, 'nonce': 632717637, 'block_height': 2206525}, 2206526: {'version': 536870912, 'prev_block_hash': 'e3dc75e8dfa601bb91615cbb3d50b216f3d6c83f3f6e991d982d95aa88025ab4', 'merkle_root': '836f81e989916f694c674fcf8da11167b8a6f26e86b1e04d51514c22c430bd23', 'timestamp': 1609445997, 'bits': 436606062, 'nonce': 2130612094, 'block_height': 2206526}, 2206527: {'version': 536870912, 'prev_block_hash': '240eff2862051667cd689d214d896f8e78eec3a844a368be841ec00a6005eacf', 'merkle_root': '1c685361ea5fbac52a4b876c4c7bf5c60d94f6c31523319dd31e3f1c87f4d01e', 'timestamp': 1609446064, 'bits': 436621155, 'nonce': 3355082659, 'block_height': 2206527}, 2206528: {'version': 536870912, 'prev_block_hash': '17cf5b52259574e136520b7810928dcbf8e6d2725fca5271ecdb1288de78b79c', 'merkle_root': 'e53478cb75d397b9d168a23d9d6b18d241029ccce75966f2a1635d88d4f55507', 'timestamp': 1609446097, 'bits': 436622203, 'nonce': 2427283207, 'block_height': 2206528}, 2206529: {'version': 536870912, 'prev_block_hash': 'ceceb35eb792cd7728b779d8bde0c063948964608b2fb5fc08e28b97389f70b0', 'merkle_root': '00e724c066d68c04fa033cc228f4faf9139360f16e24f11ff8f6bcb5d09c2f56', 'timestamp': 1609446108, 'bits': 436617031, 'nonce': 12246852, 'block_height': 2206529}, 2206530: {'version': 536870912, 'prev_block_hash': '9fbeb81d66a9690389e6fa4af51fb5cb58b5e1985814a0e3c9282a0b743bc9c1', 'merkle_root': '900a55f729f0ffc485573f14a2eb6ad98e09f062d3b4f14d29ee86b674f80631', 'timestamp': 1609446465, 'bits': 436610673, 'nonce': 3113809169, 'block_height': 2206530}, 2206531: {'version': 536870912, 'prev_block_hash': '83e32b6cec70692839a31254d7e1e54cde9e4ebd609909aea911c1ccb6f3bcea', 'merkle_root': '8753aefb0807ce00d6dd08af39c9546d9d99b5058b71325fcee16e825ebad1d5', 'timestamp': 1609446495, 'bits': 436652811, 'nonce': 4034390885, 'block_height': 2206531}, 2206532: {'version': 536870912, 'prev_block_hash': '4972be8a70cc57ec5ac8797a70ddfe649e53399b956d9dc6f7c441980398a148', 'merkle_root': 'fba036cbf0ae13be324c0cadbb1f5394df5e31730d3f26446acbe71cfa8c8cad', 'timestamp': 1609446538, 'bits': 436651818, 'nonce': 3995783605, 'block_height': 2206532}, 2206533: {'version': 536870912, 'prev_block_hash': 'ee827023ec8ff367ca696f1ef15428a938f659eede017edb73c5e18926a4be45', 'merkle_root': '3a77f5c65e241bc0f98e7c769856ba8ceab5ee6acac2f6e4179d5c8cccf7a9e7', 'timestamp': 1609446687, 'bits': 436624837, 'nonce': 3037641522, 'block_height': 2206533}, 2206534: {'version': 536870912, 'prev_block_hash': '1ecbba9436fc30f6f754d3bf23dce7ea14b043c87b9f6ced3724687ae4c4e4a5', 'merkle_root': 'b35280e639c58d2fbd6c68259d6a36c36fa22079fd5c395c2671bedf3f7fb6e0', 'timestamp': 1609446816, 'bits': 436644078, 'nonce': 570649684, 'block_height': 2206534}, 2206535: {'version': 536870912, 'prev_block_hash': '4f244738562a8d5043647226bf365562b21c7969307adfae62c27f55efd15bb7', 'merkle_root': '9a5d1d4dfc02cd2deea1ad45fcf009e1c71aefdcf37b2e246e2984ef1de16900', 'timestamp': 1609446927, 'bits': 436667852, 'nonce': 3209124518, 'block_height': 2206535}, 2206536: {'version': 536870912, 'prev_block_hash': '8458f4914392ca79bed665183325028a9dc923a5bd9adcffb71504418df4c85b', 'merkle_root': 'c8a0b1dc4eaf05a864a3e4b18d80c0a01241c5467efc77abfb6dbe8a62c0d17f', 'timestamp': 1609446940, 'bits': 436678347, 'nonce': 1558666374, 'block_height': 2206536}, 2206537: {'version': 536870912, 'prev_block_hash': '950e1e6fde2374c4e6b5c6410de17aa06cc529e744f37dd0c32c64dd1d7bb746', 'merkle_root': 'aed89fdc09cdf3893d35a62df0182c943cc3a0309b4251d5f9923c85acc08c70', 'timestamp': 1609447234, 'bits': 436655004, 'nonce': 1640074009, 'block_height': 2206537}, 2206538: {'version': 536870912, 'prev_block_hash': '28bc9fdd7ab0d15f567645e174c7e3ea7027ef90611e730b5462a6282946d0b9', 'merkle_root': '72a363391d361998612c938f3ced45273d810eec5d23c1ba6154f4ed9725679b', 'timestamp': 1609447281, 'bits': 436703536, 'nonce': 4023305371, 'block_height': 2206538}, 2206539: {'version': 536870912, 'prev_block_hash': '7a558e121576bf037355022758126a6dcff6eb1196d1a6637f9b0d66631f178f', 'merkle_root': 'b5508485f20a33c62f5b54c0ae8e93a5fb448f6d59493fed8e7c44a0c80d83c8', 'timestamp': 1609447384, 'bits': 436694408, 'nonce': 739444754, 'block_height': 2206539}, 2206540: {'version': 536870912, 'prev_block_hash': '918ffd6a492a437afc25cc54921f9f62b7c8ba84529b5c4de36afc1693e7fe32', 'merkle_root': 'd5aeafdb55ea5e1ed86fc03b6789964bf2bc1f828782cd356d1a31ecb49b9887', 'timestamp': 1609447413, 'bits': 436713926, 'nonce': 1895755322, 'block_height': 2206540}, 2206541: {'version': 536870912, 'prev_block_hash': '02755cd1cec2f837100165b0106050b2eb4ed7869b19e2605a7c828e7d515452', 'merkle_root': '1ce0429268d986fdd324b6fbb3119126288bffd7adf71b50dc2abac011956d3f', 'timestamp': 1609447455, 'bits': 436694298, 'nonce': 2787690507, 'block_height': 2206541}, 2206542: {'version': 536870912, 'prev_block_hash': 'd227495a03fec3ae3ab4d33389f8ddff2924bf52b4e397fef064e47d2b80b3be', 'merkle_root': 'e59c530f17cd030c80090c5aff4a998890b92472d723843248f63ff04a3fd141', 'timestamp': 1609447500, 'bits': 436641834, 'nonce': 3636446255, 'block_height': 2206542}, 2206543: {'version': 536870912, 'prev_block_hash': '30594681b22092a3ba73b532accc7835f117984098164cd10bb9a8c4272e33f3', 'merkle_root': '66ad5a4a7c9037f69d47a1103a8a3ecc1103b75891b2ac0280567431cfccd549', 'timestamp': 1609447533, 'bits': 436644373, 'nonce': 850699273, 'block_height': 2206543}}
        bits = Blockchain.get_target(self, 2206543, headers5)
        self.assertEqual(bits, 10709251786800936527318757626382864578020150972591414166005562)
