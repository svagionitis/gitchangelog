
import os.path

from common import GitChangelogTestCase, w, cmd


class TestConfiguration(GitChangelogTestCase):

    def test_simple_run(self):
        out, err, errlvl = cmd('$tprog')
        self.assertEqual(
            errlvl, 0,
            msg="Should not fail on simple repo and without config file")
        self.assertEqual(
            err, "",
            msg="There should be no standard error outputed. "
            "Current stderr:\n%r" % err)
        self.assertContains(
            out, "0.0.2",
            msg="At leat one of the tags should be displayed in stdout... "
            "Current stdout:\n%s" % out)

    def test_overriding_options(self):
        """We must be able to define a small gitchangelog.rc that adjust only
        one variable of all the builtin defaults."""

        w("""

            cat <<EOF > .gitchangelog.rc

tag_filter_regexp = r'^v[0-9]+\.[0.9]$'

EOF
            git tag 'v7.0' HEAD^
            git tag 'v8.0' HEAD

        """)
        changelog = w('$tprog')
        self.assertContains(
            changelog, "v8.0",
            msg="At leat one of the tags should be displayed in changelog... "
            "content of changelog:\n%s" % changelog)

    def test_reuse_options(self):
        """We must be able to define a small gitchangelog.rc that adjust only
        one variable of all the builtin defaults."""

        w("""cat <<EOF > .gitchangelog.rc

ignore_regexps += [r'XXX', ]

EOF
        """)
        changelog = w('$tprog')
        self.assertNotContains(
            changelog, "XXX",
            msg="Should not contain commit with XXX in it... "
            "content of changelog:\n%s" % changelog)
        self.assertContains(
            changelog, "dd file ``e``",
            msg="Should contain at least a message of other commits... "
            "content of changelog:\n%s" % changelog)
        self.assertNotContains(
            changelog, "!minor",
            msg="Shouldn't contain !minor tagged commit neither... "
            "content of changelog:\n%s" % changelog)


class TestInitArgument(GitChangelogTestCase):

    def test_init_file(self):

        out, err, errlvl = cmd('$tprog init')
        self.assertEqual(
            errlvl, 0,
            msg="Should not fail to init on simple git repository")
        self.assertEqual(
            err, "",
            msg="There should be no standard error outputed. "
            "Current stdout:\n%r" % out)
        self.assertContains(
            out, "created",
            msg="Output message should mention that the file was created... "
            "Current stdout:\n%s" % out)
        self.assertTrue(
            os.path.exists('.gitchangelog.rc'),
            msg="File must have been created.")

    def test_init_file_already_exists(self):

        w("touch .gitchangelog.rc")
        out, err, errlvl = cmd('$tprog init')
        self.assertEqual(
            errlvl, 1,
            msg="Should fail to init on simple git repository")
        self.assertContains(
            err, "exists",
            msg="There should be a error msg mentioning the file exists. "
            "Current stderr:\n%r" % err)
        self.assertEqual(
            out, "",
            msg="No standard output message expected in case of error "
            "Current stdout:\n%s" % out)

    def test_outside_git_repository(self):

        out, err, errlvl = cmd('cd .. ; $tprog init')
        self.assertEqual(
            errlvl, 1,
            msg="Should fail to init outside a git repository.")
        self.assertContains(
            err, "repository",
            msg="There should be a error msg mentioning 'repository'. "
            "Current stderr:\n%r" % err)
        self.assertEqual(
            out, "",
            msg="No standard output message expected. "
            "Current stdout:\n%s" % out)

    def test_in_bare_repository(self):
        w("""

            cd ..
            git clone --bare repos test_bare

        """)
        out, err, errlvl = cmd('cd ../test_bare && $tprog init')
        self.assertEqual(
            errlvl, 1,
            msg="Should fail to init outside a git repository.")
        self.assertContains(
            err, "bare",
            msg="There should be a error msg mentioning 'bare'. "
            "Current stderr:\n%r" % err)
        self.assertEqual(
            out, "",
            msg="No standard output message expected. "
            "Current stdout:\n%s" % out)

    def test_in_sub_repository(self):
        w("""

            mkdir subdir
            cd subdir

        """)
        out, err, errlvl = cmd('$tprog init')
        self.assertEqual(
            errlvl, 0,
            msg="Should not fail in sub directory.")
        self.assertContains(
            out, "created",
            msg="There should  msg mentioning the file was 'created'. "
            "Current stdout:\n%r" % out)
        self.assertEqual(
            err, "",
            msg="No error message expected. "
            "Current stderr:\n%s" % err)
        self.assertTrue(
            os.path.exists('.gitchangelog.rc'),
            msg="File must have been created.")
