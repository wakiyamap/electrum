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

        # after DGWv3 after checkpoint(2041196)
        headers5 = {2041171: {'version': 536870912, 'prev_block_hash': '434a7dfbfcca0065c8f2ba6c4dca0d7d03a46b417411dcc120d94b07ddf52e7b', 'merkle_root': '8a596a2d547e1e56091beb2cd4e623fbb07102d6be1475b2e014d0b628507259', 'timestamp': 1593801117, 'bits': 436481665, 'nonce': 1743496880, 'block_height': 2041171}, 2041172: {'version': 536870912, 'prev_block_hash': 'd6b2ef885174325a2b1d58417ea130c2591be635de862ef24ad7432793f47441', 'merkle_root': '2c004b38a3c77b7f84c7c02b4b18de1e49211a86a84efca3c6975330ddb6b6f5', 'timestamp': 1593801160, 'bits': 436460739, 'nonce': 3581401239, 'block_height': 2041172}, 2041173: {'version': 536870912, 'prev_block_hash': '92af0c020abb87de989ddd569bef17a137fa9db4871514859eaf2057314f0821', 'merkle_root': '49eff882d7077d074dc345b5778407f91b5820735abc96bfdb9691ff23371c35', 'timestamp': 1593801199, 'bits': 436444198, 'nonce': 3329951871, 'block_height': 2041173}, 2041174: {'version': 536870912, 'prev_block_hash': '7a11206a1d5e43d5fc167094311c7559e666da7b3c760d2edb4fe9fa2b217a13', 'merkle_root': '0a110919bc1babcb67bfc44489275d287e0de2cba93f1c7413728f8a0f7bcd74', 'timestamp': 1593801279, 'bits': 436442310, 'nonce': 1727797376, 'block_height': 2041174}, 2041175: {'version': 536870912, 'prev_block_hash': 'faa2695bf6e93079e0f56fb9d42cfc127245d945f0bbe896f31e858c6b758a08', 'merkle_root': 'f240bc3a43f85a759abc51a1d3ca1dec26890c584dc01a5ba4e23355b0b2e031', 'timestamp': 1593801881, 'bits': 436439951, 'nonce': 1582910108, 'block_height': 2041175}, 2041176: {'version': 536870912, 'prev_block_hash': 'c605d43febc0fa96bca1aa6954b07c53341a38a8ac593bb966863565ad898aa7', 'merkle_root': '7e98aa670ad7a308f500afa6fc479a4242d0e149e0ed9028dc338829543932b4', 'timestamp': 1593801916, 'bits': 436514137, 'nonce': 3534411670, 'block_height': 2041176}, 2041177: {'version': 536870912, 'prev_block_hash': 'f8be68067855beac0c83ea81fa2cf3c3d9762f5880d6bd491836eb74a0cba029', 'merkle_root': '091932b736dd2740d5e18497aa7f20529fc668c6b4cb80332f76e986cdb0c90f', 'timestamp': 1593801934, 'bits': 436514147, 'nonce': 3643762728, 'block_height': 2041177}, 2041178: {'version': 536870912, 'prev_block_hash': '82c6e85d3f04e46c0d2cee639f270336ce4a5a8f8d705d8d588cfa22f09988ab', 'merkle_root': '31811783e61252f9cb34ed361643e24d53cc119f7a79c89ef647e952821258b4', 'timestamp': 1593801945, 'bits': 436506662, 'nonce': 3949576319, 'block_height': 2041178}, 2041179: {'version': 536870912, 'prev_block_hash': '867d26c9ad5bc5000167471f6a362366aebea2b088ff573cc711a6bd2cd7f9d5', 'merkle_root': 'b2f5a1bb3ed87a68e71898a5ecce57c7c775731e06c25fc8722d789e807db960', 'timestamp': 1593802003, 'bits': 436497614, 'nonce': 19476663, 'block_height': 2041179}, 2041180: {'version': 536870912, 'prev_block_hash': '6364958943dbcbaec05b9f936e0fb27bbef7ffe0e0a8270765ca5839ca9af2c9', 'merkle_root': 'bd69449bf37d0e2c68ea0503ac97775a911685568672f4dc39100042c1209a43', 'timestamp': 1593802046, 'bits': 436485451, 'nonce': 2712782926, 'block_height': 2041180}, 2041181: {'version': 536870912, 'prev_block_hash': '824d63360ee456b2b931589bf367aeaffec7b75dd742446cb988c0603d63fc6f', 'merkle_root': '2fed7bcebfd5c15bbbc052ffe6e9804a34dffd80ed711d5a5caa261b27264612', 'timestamp': 1593802052, 'bits': 436482450, 'nonce': 1226458892, 'block_height': 2041181}, 2041182: {'version': 536870912, 'prev_block_hash': '47bde237ec093cba3c73b3a2a83479ee47dff63cf82f98d061db8ca4a8eddac6', 'merkle_root': '3ac72176d7f6ddde78e1c8b2217d1a5f336d1242765c425ac14c02129c8a07d2', 'timestamp': 1593802092, 'bits': 436445473, 'nonce': 466506834, 'block_height': 2041182}, 2041183: {'version': 536870912, 'prev_block_hash': 'bfd4a858c5f48f14c237e16c3426184fe8f505683e3f1f7a52c93214566d39a5', 'merkle_root': '25e3f5572779cbe5a2eab11f4fe670f67e5c70377d60a9752e68c0087f965142', 'timestamp': 1593802176, 'bits': 436444975, 'nonce': 2715928887, 'block_height': 2041183}, 2041184: {'version': 536870912, 'prev_block_hash': 'b8ff5973cb096482ca7b687f74647796e2e5fb099d0ac1500fa1c1e8e0680e68', 'merkle_root': '8f211b790ad40e3451b70b1bf9313bcbd210008e344cae96cc0f27330f40e960', 'timestamp': 1593802218, 'bits': 436439930, 'nonce': 2582206894, 'block_height': 2041184}, 2041185: {'version': 536870912, 'prev_block_hash': '9068bd9309c10fa9c7282fa9ff05b687ff572f2f067a4caacbb6f1c11b51e6fc', 'merkle_root': '87db2e7b1255e34a816dd80f5d1d3be92986ccbd46118dfcb02862f9e805ab5b', 'timestamp': 1593802292, 'bits': 436429603, 'nonce': 1439646624, 'block_height': 2041185}, 2041186: {'version': 536870912, 'prev_block_hash': '21eeb845fc6e155a83862f8cd3813c984545adfcf6fe5ae608d6215c077bc633', 'merkle_root': '178bfaf9e7d671eece7ae9af0973ccbe86f63aca9e4538c7c3736d2896fd18ba', 'timestamp': 1593802295, 'bits': 436418149, 'nonce': 1480004439, 'block_height': 2041186}, 2041187: {'version': 536870912, 'prev_block_hash': '19a4adc778f41c0e224f51db7cdcf6fada007fbbc2c765fafae4b0c1686db20d', 'merkle_root': '8ac9068ea12272dcedd04dbfea921189f6de13de7778c4c88a685ea3721672ba', 'timestamp': 1593802508, 'bits': 436411061, 'nonce': 4042146187, 'block_height': 2041187}, 2041188: {'version': 536870912, 'prev_block_hash': 'ea1187c4c51143856eaebfe2734930720b91eee46fa04af76bdf1adf47da07e0', 'merkle_root': '0ffa65c1b8601a2d8010e7c5a7f6a3e1a2e221ec62d41eb3642bb64eeeba517e', 'timestamp': 1593802658, 'bits': 436423640, 'nonce': 3351417769, 'block_height': 2041188}, 2041189: {'version': 536870912, 'prev_block_hash': '7747ef4c8273b5cbe25d4c929552a9a27cf7ac9d6e049e0e9bfc66bd68268eab', 'merkle_root': '334ebd494644c5d244d650bddff6df16b673b12ac21cc5057570768adc4d2a80', 'timestamp': 1593802749, 'bits': 436433380, 'nonce': 3154212453, 'block_height': 2041189}, 2041190: {'version': 536870912, 'prev_block_hash': 'e76ff499246cb074b43b9fa7f0121e297dc4ba00a2a06287091e37f2a139f1f8', 'merkle_root': 'b3865c5697d5dae08cefa53668c5deb9d59a1228716fa26ac7acca69d25d0346', 'timestamp': 1593802864, 'bits': 436436814, 'nonce': 1476396096, 'block_height': 2041190}, 2041191: {'version': 536870912, 'prev_block_hash': '50f7983f3c0b77cdb73d1e632e4858c725cbe7b297e0934bd519ccf9ae6d3aa5', 'merkle_root': '5d559402ac8c315124f66d0c44f8b877bf4a591b1b1d175656ae183c86bd4341', 'timestamp': 1593802920, 'bits': 436441398, 'nonce': 1563286608, 'block_height': 2041191}, 2041192: {'version': 536870912, 'prev_block_hash': '34a7e2c5139ce0625a1a8713a1ad0547f071963867590d73d889579d4d94b51f', 'merkle_root': '06bfa74fed1fea66d79b24c4233cb5f4efcc971c83061fdcb21fe743034df682', 'timestamp': 1593802977, 'bits': 436437928, 'nonce': 1410343315, 'block_height': 2041192}, 2041193: {'version': 536870912, 'prev_block_hash': '96a58d077e8f43462e8b69dc399ac454d3012026e2ac9fa4d812aa1dadf19fe1', 'merkle_root': 'ef7dd0ce0cdc16be9474a4c29a5fdea7b76f23fcdb080add8c9df295b13b8970', 'timestamp': 1593803456, 'bits': 436439373, 'nonce': 3526226806, 'block_height': 2041193}, 2041194: {'version': 536870912, 'prev_block_hash': '98f86a2cb3fad84776b96686958967b236a892f242e1f94cb5a5382eab812053', 'merkle_root': '17ab70daa3322dd9c3edf8332f43d366e2e46791b181c85f6acea3cceae18891', 'timestamp': 1593803495, 'bits': 436488844, 'nonce': 2621837056, 'block_height': 2041194}, 2041195: {'version': 536870912, 'prev_block_hash': 'b2c08c5b854638dbd708955f0e78444c129f43820b2469da462bb502b4a8a5b6', 'merkle_root': '8cf9ad504f9e58120d234cb900e647d98f00373e263a8157a97f54f073d027a5', 'timestamp': 1593803534, 'bits': 436483214, 'nonce': 674434017, 'block_height': 2041195}}
        bits = Blockchain.get_target(self, 2041196, headers5)
        self.assertEqual(bits, 6741891227282744414704927191482180097961828903172103425159275)
