# from distutils.core import setup, Extension
from setuptools import setup, Extension

textypy_libtexty = Extension('textypy_libtexty',
    sources=[
        'src/Language.cpp',
        'src/hashing/hash_funcs.cpp',
        'src/language_detection/LanguageProfiles.cpp',
        'src/language_detection/GlobalLanguageProfiles.cpp',
        'src/language_detection/DetectionRunner.cpp',
        'src/language_detection/OwningLanguageDetector.cpp',
        'src/language_detection/GlobalLanguageDetector.cpp',
        'src/language_detection/NonOwningLanguageDetector.cpp',
        'src/stemming/BaseStemmer.cpp',
        'src/stemming/Utf8Stemmer.cpp',
        'src/string_views/Utf8View.cpp',
        'src/string_views/Utf8Iterator.cpp',
        'src/string_views/RandomAccessNGramView.cpp',
        'src/string_views/RandomAccessUtf8View.cpp',
        'src/string_views/TokenView.cpp',
        'src/string_views/ShingleView2.cpp',
        'src/util/misc.cpp',
        'src/util/ScopeGuard.cpp',
        'src/util/fs.cpp',
        'src/unicode/UnicodeBlock.cpp',
        'src/unicode/support.cpp',
        'src/python_interface.cpp',
        'external/smhasher/src/City.cpp',
        'external/smhasher/src/MurmurHash3.cpp',
        'external/libstemmer/src_c/stem_ISO_8859_1_danish.c',
        'external/libstemmer/src_c/stem_UTF_8_danish.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_dutch.c',
        'external/libstemmer/src_c/stem_UTF_8_dutch.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_english.c',
        'external/libstemmer/src_c/stem_UTF_8_english.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_finnish.c',
        'external/libstemmer/src_c/stem_UTF_8_finnish.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_french.c',
        'external/libstemmer/src_c/stem_UTF_8_french.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_german.c',
        'external/libstemmer/src_c/stem_UTF_8_german.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_hungarian.c',
        'external/libstemmer/src_c/stem_UTF_8_hungarian.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_italian.c',
        'external/libstemmer/src_c/stem_UTF_8_italian.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_norwegian.c',
        'external/libstemmer/src_c/stem_UTF_8_norwegian.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_porter.c',
        'external/libstemmer/src_c/stem_UTF_8_porter.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_portuguese.c',
        'external/libstemmer/src_c/stem_UTF_8_portuguese.c',
        'external/libstemmer/src_c/stem_ISO_8859_2_romanian.c',
        'external/libstemmer/src_c/stem_UTF_8_romanian.c',
        'external/libstemmer/src_c/stem_KOI8_R_russian.c',
        'external/libstemmer/src_c/stem_UTF_8_russian.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_spanish.c',
        'external/libstemmer/src_c/stem_UTF_8_spanish.c',
        'external/libstemmer/src_c/stem_ISO_8859_1_swedish.c',
        'external/libstemmer/src_c/stem_UTF_8_swedish.c',
        'external/libstemmer/src_c/stem_UTF_8_turkish.c',
        'external/libstemmer/runtime/api.c',
        'external/libstemmer/runtime/utilities.c',
        'external/libstemmer/libstemmer/libstemmer.c'
    ],
    include_dirs=[
        '/usr/local/include',
        'src',
        'external/smhasher/src',
        'external/utfcpp/source',
        'external/pybind11/include',
        'external/libstemmer/include',
        'external/json/src'
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
    package_data = {
        'something': 'textypy2/data/something'
    },
    include_package_data=True,
    version = '0.1.5',
    description = 'python interface for libtexty',
    maintainer = 'Scott Ivey',
    maintainer_email='scott.ivey@gmail.com',
    url='https://github.com/scivey/libtexty',
    ext_modules = [textypy_libtexty],
    packages=['textypy']
)
