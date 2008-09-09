import config
import sys, unittest, os
sys.path.insert(0, "../")
from duplicity import path

config.setup()

class RdiffdirTest(unittest.TestCase):
    """Test rdiffdir command line program"""
    def run_cmd(self, command): assert not os.system(command)
    def del_tmp(self):
        """Make new testfiles/output dir"""
        self.run_cmd("rm -rf testfiles/output")
        os.mkdir("testfiles/output")

    def run_rdiffdir(self, argstring):
        """Run rdiffdir with given arguments"""
        self.run_cmd("../rdiffdir " + argstring)

    def run_cycle(self, dirname_list):
        """Run diff/patch cycle on directories in dirname_list"""
        assert len(dirname_list) >= 2
        self.del_tmp()

        seq_path = path.Path("testfiles/output/sequence")
        new_path = path.Path(dirname_list[0])
        delta_path = path.Path("testfiles/output/delta.tar")
        sig_path = path.Path("testfiles/output/sig.tar")

        self.run_cmd("cp -a %s %s" % (new_path.name, seq_path.name))
        seq_path.setdata()
        self.run_rdiffdir("sig %s %s" % (seq_path.name, sig_path.name))
        sig_path.setdata()
        assert sig_path.exists()
        assert new_path.compare_recursive(seq_path, verbose = 1)

        for dirname in dirname_list[1:]:
            new_path = path.Path(dirname)

            # Make delta
            if delta_path.exists(): delta_path.delete()
            assert not delta_path.exists()
            self.run_rdiffdir("delta %s %s %s" %
                              (sig_path.name, new_path.name, delta_path.name))
            delta_path.setdata()
            assert delta_path.exists()

            # patch and compare
            self.run_rdiffdir("patch %s %s" % (seq_path.name, delta_path.name))
            seq_path.setdata()
            new_path.setdata()
            assert new_path.compare_recursive(seq_path, verbose = 1)

            # Make new signature
            sig_path.delete()
            assert not sig_path.exists()
            self.run_rdiffdir("sig %s %s" % (seq_path.name, sig_path.name))
            sig_path.setdata()
            assert sig_path.isreg()

    def test_dirx(self):
        """Test cycle on testfiles/dirx"""
        self.run_cycle(['testfiles/empty_dir',
                        'testfiles/dir1',
                        'testfiles/dir2',
                        'testfiles/dir3',
                        'testfiles/empty_dir'])


if __name__ == "__main__":
    unittest.main()
