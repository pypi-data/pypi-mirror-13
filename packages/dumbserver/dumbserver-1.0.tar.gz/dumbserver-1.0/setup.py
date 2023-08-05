from distutils import log
from setuptools import setup

try:
    from setuptools.command import egg_info
    egg_info.write_toplevel_names
except (ImportError, AttributeError):
    pass
else:
    def _top_level_package(name):
        return name.split('.', 1)[0]

    def _hacked_write_toplevel_names(cmd, basename, filename):
        pkgs = dict.fromkeys(
            [_top_level_package(k)
                for k in cmd.distribution.iter_distribution_names()
                if _top_level_package(k) != "twisted"
            ]
        )
        cmd.write_file("top-level names", filename, '\n'.join(pkgs) + '\n')

    egg_info.write_toplevel_names = _hacked_write_toplevel_names

setup(name='dumbserver',
      version='1.0',
      description='Mock several REST services in one go!',
      url='https://github.com/varunmulloli/dumbserver',
      download_url = 'https://github.com/varunmulloli/dumbserver/tarball/1.0',
      author='Varun Mulloli',
      author_email='mulloli@me.com',
      license='MIT',
      packages=['dumbserver','twisted.plugins'],
      install_requires=['PyYAML','treelib','Twisted'],
      keywords=['mockserver', 'mock server', 'service', 'http', "REST"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Framework :: Twisted",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: Unix",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Quality Assurance",
          "Topic :: Software Development :: Testing"
      ]
)

try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))