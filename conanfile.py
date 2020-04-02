from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import shutil


class ELFUtilsConan(ConanFile):
    name = "elfutils"
    version = "0.173"
    description = "A collection of utilities and libraries to read, create and modify ELF binary files"
    url = "https://github.com/bincrafters/conan-elfutils"
    homepage = "https://sourceware.org/elfutils"
    license = "MIT"
    exports = ["elfutils.patch"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {'fPIC': 'True'}
    autotools = None
    _source_subfolder = "source_subfolder"
    requires = (
        "bzip2/1.0.6",
        "zlib/1.2.11",
        "xz_utils/5.2.4"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get("{}/ftp/{}/{}-{}.tar.bz2".format(self.homepage, self.version, self.name, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.patch(base_path=self._source_subfolder, patch_file='elfutils.patch')

    def configure_autotools(self):
        if not self.autotools:
            args = ['--enable-silent-rules', '--with-zlib', '--with-bzlib', '--with-lzma']
            self.autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self.autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self.autotools

    def build(self):
        autotools = self.configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        autotools = self.configure_autotools()
        autotools.install()
        shutil.rmtree(os.path.join(self.package_folder, "share"))
        shutil.rmtree(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
