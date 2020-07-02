"""
mayautils.py
Asmita Chitale
Assignment 02
ATCM 3311.0U1
06/26/2020
"""


import logging
import pymel.core as pmc
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

    def __init__(self, dir='', descriptor='main', version=1, ext="ma", current_scene=False):
        """Constructs SceneFile from the directory, descriptor, version, and extension

        Other Params:
            current_scene: Construct SceneFile from getting the current scene info instead if True, otherwise use
                provided parameters
        """
        if current_scene:
            scene_name = pmc.system.sceneName()

            if not scene_name:
                # If file has never been saved, assume the current workspace under 'scenes'
                dir = pmc.system.Workspace.getPath()/"scenes"
            else:
                # Get directory and extension from the path
                full_path = Path(scene_name)
                dir = full_path.dirname()
                ext = full_path.ext[1:]

                # Remove extension from base name and check for a version number
                back_offset = -1*(len(ext) + 1)
                base_name = full_path.basename()[:back_offset]
                regex_str = ".*_[0-9]{3}$"
                regex = re.compile(regex_str)

                if regex.match(base_name):
                    # The file already has a version number, use it
                    descriptor = base_name[:-4]
                    version = int(base_name[-3:])
                else:
                    # Otherwise the whole base name is the descriptor, use the default version number and save a copy
                    log.warning("No version number, setting version to 1")
                    descriptor = base_name

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
            obj: 'Path': The path to the scene file if successful, otherwise None.

        """
        try:
            try:
                pmc.system.saveAs(self.path())
            except RuntimeError:
                log.warning("Missing directories. Creating directories...")
                Path(self.dir).makedirs_p()
                pmc.system.saveAs(self.path())
            return self.path()
        except IOError:
            log.error("IOError occurred while saving.")
            return None

    def _increment(self):
        """Updates the version number to the next available version.

        Returns:
            version: The new version number

        """
        # Get all the files (don't filter yet, will use regex)
        all_files = pmc.system.getFileList(folder=self.dir, filespec="*")

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

    def increment_and_save(self):
        """Increments the version number and saves

        Returns:
            obj: 'Path': The path to the scene file if successful, otherwise None.

        """
        self._increment()
        return self.save()
