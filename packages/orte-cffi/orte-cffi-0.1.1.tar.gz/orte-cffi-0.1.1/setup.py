import subprocess
import os
from setuptools import setup

def ompi_info_path(key):

    cmd = ['ompi_info', '--path', key, '--parseable']

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr= p.communicate()

    if p.returncode != 0:
        raise Exception(stderr)

    p_str, l_str, path = stdout.split(':')
    if p_str.strip() != 'path':
        raise Exception('Parse error')
    if l_str.strip() != key:
        raise Exception('Parse error')

    path = path.strip()

    if not os.path.isdir(path):
        raise Exception('Path "%s" is not an existing directory' % path)
    
    return path


def get_pkgconfig_dir():

    libdir = ompi_info_path('libdir')

    pkgdir = os.path.join(libdir, 'pkgconfig')
    if not os.path.isdir(pkgdir):
        raise Exception('Path "%s" is not an existing directory' % pkgdir)
    
    return pkgdir


def pkgconfig(libname, variables=None):

    cmd = ['pkg-config', '--cflags-only-I', libname]

    if variables:
        for k,v in variables.iteritems():
            cmd.append('--define-variable=%s=%s' % (k, v))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr= p.communicate()

    if p.returncode != 0:
        raise Exception(stderr)

    include_dirs = []
    library_dirs = []

    for item in stdout.split():
        if item.startswith("-L"):
            library_dirs.append(item[2:])
        elif item.startswith("-I"):
            include_dirs.append(item[2:])

    return {'include_dirs': include_dirs,
            'library_dirs': library_dirs}


# Get the pkgconfigdir from orte_info and export to environment
pkgconfig_dir = get_pkgconfig_dir()
os.environ['PKG_CONFIG_PATH'] = pkgconfig_dir

# Get the pkgincludedir from ompi_info
pkgincludedir = ompi_info_path('pkgincludedir')
pkgcfg = pkgconfig('orte', variables={'pkgincludedir': pkgincludedir})
include_dirs = pkgcfg['include_dirs']
library_dirs = pkgcfg['library_dirs']

setup(
    name = "orte-cffi",
    version = "0.1.1",
    author = "Mark Santcroos",
    author_email = "mark.santcroos@rutgers.edu",
    description = "CFFI-based Python wrapper for Open RTE",
    license = "New BSD",
    keywords = "mpi cffi",
    packages = ['src/orte-cffi'],
    url = "http://www.open-mpi.org",
    setup_requires = ["cffi>=1.5.0"],
    cffi_modules = ["src/orte-cffi/build.py:ffi"],
    install_requires = ["cffi>=1.5.0"],
    include_dirs = include_dirs,
    library_dirs = library_dirs
)
