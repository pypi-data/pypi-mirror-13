from distutils.core import setup, Extension

textypy = Extension('textypy',
    sources=[
        'src/hashing/hash_funcs.cpp',
        'src/string_views/ShingleView2.cpp',
        'src/string_views/TokenView.cpp',
        'src/string_views/Utf8View.cpp',
        'src/util/misc.cpp',
        'src/python_interface.cpp',
        'external/smhasher/src/City.cpp',
        'external/smhasher/src/MurmurHash3.cpp',
    ],
    include_dirs=[
        '/usr/local/include',
        'src',
        'external/smhasher/src',
        'external/utfcpp/source',
        'external/pybind11/include'
    ],
    headers=[
        'external/smhasher/src/City.h',
        'external/smhasher/src/MurmurHash3.h',
    ],
    library_dirs=[
        '/usr/local/lib'
    ],
    extra_compile_args=[
        '--std=c++11'
    ]
)

setup(
    name = 'textypy',
    version = '0.1.2',
    description = 'python interface for libtexty',
    maintainer = 'Scott Ivey',
    maintainer_email='scott.ivey@gmail.com',
    url='https://github.com/scivey/libtexty',
    ext_modules = [textypy]
)
