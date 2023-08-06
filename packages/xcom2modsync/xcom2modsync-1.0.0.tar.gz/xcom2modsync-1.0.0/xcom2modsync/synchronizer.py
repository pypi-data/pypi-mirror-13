import os
import os.path
import glob
import shutil

from .exceptions import ModNotFound
from .constants import DEFAULT_XCOM2_WORKSHOP_PATH, DEFAULT_MODS_PATH, XCOM2_MOD_EXTENSION


class Synchronizer:

    def __init__(self, workshop_path=DEFAULT_XCOM2_WORKSHOP_PATH, mods_path=DEFAULT_MODS_PATH):
        """
        :param workshop_path: Path to Steam Workshop's root directory
        :param mods_path: Path to XCOM2's mods directory
        """
        self.source_path = os.path.expanduser(workshop_path)
        self.destination_path = os.path.expanduser(mods_path)

    def run(self):
        for mod in os.listdir(self.source_path):
            self._reinstall_mod(os.path.join(self.source_path, mod))

    def _reinstall_mod(self, mod_dir):
        try:
            name = self._mod_name(mod_dir).lower()
            target_path = os.path.join(self.destination_path, name)
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(mod_dir, target_path)
        except ModNotFound:
            # Not a mod directory, so just skip it
            pass

    @staticmethod
    def _mod_name(mod_dir):
        try:
            return glob.glob1(mod_dir, XCOM2_MOD_EXTENSION)[0][0:-(len(XCOM2_MOD_EXTENSION) - 1)]
        except IndexError:
            raise ModNotFound('No mod files found in [%s]' % mod_dir)
