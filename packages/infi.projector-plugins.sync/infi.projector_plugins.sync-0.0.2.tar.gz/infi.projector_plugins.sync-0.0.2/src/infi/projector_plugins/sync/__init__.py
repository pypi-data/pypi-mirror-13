__import__("pkg_resources").declare_namespace(__name__)

from infi.projector.plugins import CommandPlugin
from infi.projector.helper import utils
from infi.projector.helper import assertions
from logging import getLogger

logger = getLogger(__name__)

USAGE = """
Usage:
    projector repository sync <remote-user> <remote-host> [<remote-path>] [--watch] [--verbose]

Options:
    repository sync                 Sync this repository with a remote target
    <remote-user>                   name of user on remote host with permissions to write to target path
    <remote-host>                   ip or name of host to sync to
    <remote-path>                   If missing, assuming target is at the default installation directory
    --watch                         Watch for changes
    --verbose                       Increase verbosity
"""


class SyncPlugin(CommandPlugin):
    def get_docopt_string(self):
        return USAGE

    def get_command_name(self):
        return 'repository'

    def get_methods(self):
        return [self.sync]

    def _get_default_remote_path(self):
        from infi.projector.helper.utils import open_buildout_configfile
        is_windows = self.arguments.get("<remote-user>") == "Administrator"
        basedir = "/cygdrive/c/Program Files/" if is_windows else "/opt"
        with open_buildout_configfile() as buildout:
            get = buildout.get
            if is_windows:
                return "/".join([basedir, get("project", "company"), get("project", "product_name")])
            else:
                return "/".join([basedir, get("project", "company").lower(),
                                 get("project", "product_name").replace(' ', '-').replace('_', '-').lower()])

    def sync(self):
        from infi.pysync import main
        assertions.assert_git_repository()
        args = ["--python"]
        if self.arguments.get("--watch"):
            args.extend(["--watch"])
        if self.arguments.get("--verbose"):
            args.extend(["--verbose"])
        patterns = [".cache", ".git", ".gitignore", ".installed.cfg", ".projector", "MANIFEST.in",
                    "bin", "bootstrap.py", "develop-eggs", "eggs", "parts", "build", "dist", "devlocal", "data", "setup.py",
                    "src/*egg-info", "src/**/__version__.py"]
        if not self.arguments.get("<remote-path>"):
            patterns.extend(["buildout.cfg", "setup.in"])
        args.extend(["--skip-source={}".format(item) for item in patterns])
        args.extend(["--skip-target={}".format(item) for item in patterns])
        default_remote_path = self._get_default_remote_path()
        args.extend(["{}@{}:{}".format(self.arguments.get("<remote-user>"), self.arguments.get("<remote-host>"),
                     self.arguments.get("<remote-path>") or default_remote_path)])
        logger.info("pysync {}".format(" ".join(args)))
        return main(args)
