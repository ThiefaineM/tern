'''
Copyright (c) 2017-2018 VMware, Inc. All Rights Reserved.
SPDX-License-Identifier: BSD-2-Clause
'''
import os

from .origins import Origins
from utils import rootfs

class ImageLayer(object):
    '''A representation of a container filesystem layer
    attributes:
        diff_id: the sha256 of the layer filesystem
        fs_hash: the hashed contents of the layer filesystem - default to empty
        string if there is no tarball of the layer filesystem
        packages: list of objects of type Package (package.py)
        origins: list of NoticeOrigin objects (origins.py)
        tar_file: the path to the layer filesystem tarball
        created_by: sometimes the metadata will contain a created_by
        key containing the command that created the filesystem layer
        import_image: if the layer is imported from another image
        this is a pointer to that image. In Python terms it is just the
        name of the Image object or any object that uses this layer
        Based on how container image layers are created, this is usually the
        last layer of the image that was imported
        import_str: The string from a build tool (like a Dockerfile) that
        created this layer by importing it from another image
    methods:
        add_package: adds a package to the layer
        remove_package: removes a package from the layer
        to_dict: returns a dict representation of the instance
        get_package_names: returns a list of package names
        gen_fs_hash: calculate the filesystem hash'''
    def __init__(self, diff_id, tar_file=None, created_by=None):
        self.__diff_id = diff_id
        self.__fs_hash = ''
        self.__tar_file = tar_file
        self.__created_by = created_by
        self.__packages = []
        self.__origins = Origins()
        self.__import_image = None
        self.__import_str = ''

    @property
    def diff_id(self):
        return self.__diff_id

    @property
    def packages(self):
        return self.__packages

    @property
    def fs_hash(self):
        return self.__fs_hash

    @property
    def origins(self):
        return self.__origins

    @property
    def tar_file(self):
        return self.__tar_file

    @property
    def created_by(self):
        return self.__created_by

    @created_by.setter
    def created_by(self, create_string):
        self.__created_by = create_string

    @property
    def import_image(self):
        return self.__import_image

    @import_image.setter
    def import_image(self, import_image):
        self.__import_image = import_image

    @property
    def import_str(self):
        return self.__import_str

    @import_str.setter
    def import_str(self, import_str):
        self.__import_str = import_str

    def add_package(self, package):
        if package.name not in self.get_package_names():
            self.__packages.append(package)

    def remove_package(self, package_name):
        rem_index = 0
        success = False
        for index in range(0, len(self.__packages)):
            if self.packages[index].name == package_name:
                rem_index = index
                success = True
                break
        if success:
            self.__packages.remove(self.__packages[rem_index])
        return success

    def to_dict(self):
        layer_dict = {}
        pkg_list = []
        for pkg in self.__packages:
            pkg_list.append(pkg.to_dict())
        layer_dict.update({self.fs_hash: {'packages': pkg_list,
                                          'tar_file': self.tar_file,
                                          'created_by': self.created_by
                                          }})
        return layer_dict

    def get_package_names(self):
        '''Get the list of package names in this layer'''
        pkg_list = []
        for pkg in self.packages:
            pkg_list.append(pkg.name)
        return pkg_list

    def gen_fs_hash(self):
        '''Get the filesystem hash if the image class was created with a
        tar_file'''
        if self.__tar_file:
            fs_dir = rootfs.get_untar_dir(self.__tar_file)
            tar_file = rootfs.get_layer_tar_path(self.__tar_file)
            # remove the fs directory if it already exists
            if os.path.isdir(fs_dir):
                rootfs.root_command(rootfs.remove, fs_dir)
            rootfs.extract_layer_tar(tar_file, fs_dir)
            self.__fs_hash = rootfs.calc_fs_hash(fs_dir)
