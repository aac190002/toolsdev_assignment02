import logging
import pymel.core as pmc
from pymel.core.system import getFileList
from pymel.core.system import Path
import re


log = logging.getLogger(__name__)


class SceneFile(object):
    """Class used to represent a DCC software scene file

    The class will be a convenient object that we can use to manipulate our scene files.
    Examples features include the ability to predefine our naming conventions and automatically increase our version

    Attributes:
        dir (Path, optional): Directory to the scene file. Defaults to ''.
        descriptor (str, optional): Short descriptor of the scene file. Defaults to "main".
        version (int, optional): Version number. Defaults to 1
        ext (str, optional): Extension. Defaults to "ma"

    """

    def __init__(self, dir='', descriptor='main', version=1, ext="ma"):
        self._dir = Path(dir)
        self.descriptor = descriptor
        self.version = version
        self.ext = ext

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, val):
        self._dir = Path(val)

    def basename(self):
        """Return a scene file name.

        e.g. ship_001.ma, car_011.hip

        Returns:\
            str: The name of the scene file.

        """
        name_pattern = "{descriptor}_{version:03d}.{ext}"
        name = name_pattern.format(descriptor=self.descriptor,
                                   version=self.version,
                                   ext=self.ext)
        return name

    def path(self):
        """The function returns a path to scene file.

        This includes the drive letter, any directory path and the file name.

         Returns:
             Path: the path to the scene file.

        """
        return Path(self.dir) / self.basename()

    def save(self):
        """Saves the scene file.

        Returns:
            obj: 'Path': The path to the scene file if successful, None, otherwise.

        """
        try:
            pmc.system.saveAs(self.path())
        except RuntimeError:
            log.warning("Missing directories. Creating directories...")
            Path(self.dir).makedirs_p()
            pmc.system.saveAs(self.path())

    def _increment(self):
        """Updates the version number to the next available version.

        Returns:
            version: The new version number
        """
        # Get all the files (don't filter yet, will use regex)
        all_files = getFileList(folder=self.dir, filespec="*")

        # Filter for valid files names
        regex_pattern = "{descriptor}_[0-9]{{3}}\\.{ext}"
        regex_str = regex_pattern.format(descriptor=self.descriptor,
                                         ext=self.ext)
        regex = re.compile(regex_str)
        valid_files = filter(regex.match, all_files)

        if len(valid_files) == 0:
            log.warning("No other versions found. Setting version to 001...")
            max_version = 0
        else:
            # Extract version numbers, get highest number
            front_offset = len(self.descriptor) + 1
            back_offset = -1 * (len(self.ext) + 1)
            version_numbers = [int(filename[front_offset:back_offset]) for filename in valid_files]
            max_version = max(version_numbers)

            if max_version >= 999:
                log.warning("Reached max version number 999. Setting version to 1000...")

        self.version = max_version + 1

        return self.version
