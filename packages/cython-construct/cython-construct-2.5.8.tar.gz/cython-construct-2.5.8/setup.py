#!/usr/bin/env python
import os
from multiprocessing import cpu_count
from setuptools import setup, Extension


HERE = os.path.dirname(__file__)

exec(open(os.path.join(HERE, "construct", "version.py")).read())


try:
    from Cython.Build import cythonize
    extensions = cythonize([
        Extension("construct.lib.py3compat", ["construct/lib/py3compat.pyx"]),
        Extension("construct.adapters", ["construct/adapters.pyx"]),
        Extension("construct.core", ["construct/core.pyx"], extra_compile_args=['-DCYTHON_TRACE=1']),
        Extension("construct.macros", ["construct/macros.pyx"]),
        Extension("construct.debug", ["construct/debug.pyx"]),
        Extension("construct.lib.binary", ["construct/lib/binary.pyx"]),
        Extension("construct.lib.bitstream", ["construct/lib/bitstream.pyx"]),
        Extension("construct.lib.container", ["construct/lib/container.pyx"]),
        Extension("construct.lib.expr", ["construct/lib/expr.pyx"]),
        Extension("construct.lib.hex", ["construct/lib/hex.pyx"]),
    ], force=True, emit_linenums=True, nthreads=cpu_count() * 2)

except ImportError:
    extensions = [
        Extension("construct.lib.py3compat", ["construct/lib/py3compat.c"]),
        Extension("construct.adapters", ["construct/adapters.c"]),
        Extension("construct.core", ["construct/core.c"], extra_compile_args=['-DCYTHON_TRACE=1']),
        Extension("construct.macros", ["construct/macros.c"]),
        Extension("construct.debug", ["construct/debug.c"]),
        Extension("construct.lib.binary", ["construct/lib/binary.c"]),
        Extension("construct.lib.bitstream", ["construct/lib/bitstream.c"]),
        Extension("construct.lib.container", ["construct/lib/container.c"]),
        Extension("construct.lib.expr", ["construct/lib/expr.c"]),
        Extension("construct.lib.hex", ["construct/lib/hex.c"]),
    ]

setup(
    name="cython-construct",
    ext_modules=extensions,
    version=version_string,
    packages=[
        'construct',
        'construct.lib',
        'construct.formats',
        'construct.formats.data',
        'construct.formats.executable',
        'construct.formats.filesystem',
        'construct.formats.graphics',
        'construct.protocols',
        'construct.protocols.application',
        'construct.protocols.layer2',
        'construct.protocols.layer3',
        'construct.protocols.layer4',
    ],
    license="MIT",
    description="A powerful declarative parser/builder for binary data",
    long_description=open(os.path.join(HERE, "README.rst")).read(),
    platforms=["POSIX", "Windows"],
    url="http://construct.readthedocs.org",
    author="Tomer Filiba, Corbin Simpson",
    author_email="tomerfiliba@gmail.com, MostAwesomeDude@gmail.com",
    provides=["construct"],
    keywords="construct, declarative, data structure, binary, parser, builder, pack, unpack",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
