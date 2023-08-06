# from distutils.core import setup, Extension
from setuptools import setup, Extension
from setuptools.extension import Library

GUMBO_SOURCES = [ 
    'external/gumbo-parser/src/attribute.c',
    'external/gumbo-parser/src/char_ref.c',
    'external/gumbo-parser/src/error.c',
    'external/gumbo-parser/src/parser.c',
    'external/gumbo-parser/src/string_buffer.c',
    'external/gumbo-parser/src/string_piece.c',
    'external/gumbo-parser/src/tag.c',
    'external/gumbo-parser/src/tokenizer.c',
    'external/gumbo-parser/src/utf8.c',
    'external/gumbo-parser/src/util.c',
    'external/gumbo-parser/src/vector.c'
]

STEMMER_SOURCES = [
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
]

TEXTY_SOURCES = [
    'src/cleaning/basic.cpp',
    'src/hashing/hash_funcs.cpp',
    'src/html/GumboOutputWrapper.cpp',
    'src/html/GumboVectorWrapper.cpp',
    'src/html/HtmlDom.cpp',
    'src/html/MetaTags.cpp',
    'src/html/Node.cpp',
    'src/html/Tag.cpp',
    'src/html/goose/GooseContentExtractor.cpp',
    'src/html/goose/GooseOptions.cpp',
    'src/html/goose/StupidStopwordCounter.cpp',
    'src/html/goose/TextCleaner.cpp',
    'src/html/goose/util.cpp',
    'src/Language.cpp',
    'src/language_detection/LanguageProfiles.cpp',
    'src/language_detection/GlobalLanguageProfiles.cpp',
    'src/language_detection/DetectionRunner.cpp',
    'src/language_detection/OwningLanguageDetector.cpp',
    'src/language_detection/GlobalLanguageDetector.cpp',
    'src/language_detection/NonOwningLanguageDetector.cpp',
    'src/search/RabinFingerprinter.cpp',
    'src/stemming/SbStemmerWrapper.cpp',
    'src/stemming/StemmerManager.cpp',
    'src/stemming/ThreadSafeStemmerManager.cpp',
    'src/stemming/Utf8Stemmer.cpp',
    'src/string_views/ByteStringWindow.cpp',
    'src/string_views/Utf8Iterator.cpp',
    'src/string_views/Utf8IndexIterator.cpp',
    'src/string_views/RandomAccessNGramView.cpp',
    'src/string_views/RandomAccessUtf8View.cpp',
    'src/string_views/TokenView.cpp',
    'src/string_views/ShingleView2.cpp',
    'src/stopwords/MultiLanguageStopwordFilter.cpp',
    'src/stopwords/StopwordFilter.cpp',
    'src/stopwords/english_stopwords.cpp',
    'src/stopwords/french_stopwords.cpp',
    'src/stopwords/german_stopwords.cpp',
    'src/stopwords/italian_stopwords.cpp',
    'src/stopwords/russian_stopwords.cpp',
    'src/stopwords/spanish_stopwords.cpp',
    'src/util/misc.cpp',
    'src/util/ScopeGuard.cpp',
    'src/util/fs.cpp',
    'src/unicode/UnicodeBlock.cpp',
    'src/unicode/support.cpp',
    'src/python_interface.cpp',
    'external/smhasher/src/City.cpp',
    'external/smhasher/src/MurmurHash3.cpp',
]

textypy_libtexty = Extension('textypy_libtexty',
    sources=TEXTY_SOURCES + GUMBO_SOURCES + STEMMER_SOURCES,
    include_dirs=[
        '/usr/local/include',
        'src',
        'external/smhasher/src',
        'external/utfcpp/source',
        'external/pybind11/include',
        'external/libstemmer/include',
        'external/json/src',
        'external/gumbo-parser/src'
    ],
    headers=[
        'external/smhasher/src/City.h',
        'external/smhasher/src/MurmurHash3.h',
    ],
    library_dirs=[
        '/usr/local/lib'
    ],
    extra_compile_args=[
        '--std=c++11', '--std=c11' # distutils is stupid
    ]
)

setup(
    name = 'textypy',
    package_data = {
        'something': 'textypy2/data/something'
    },
    include_package_data=True,
    version = '0.2.0',
    description = 'python interface for libtexty',
    maintainer = 'Scott Ivey',
    maintainer_email='scott.ivey@gmail.com',
    url='https://github.com/scivey/libtexty',
    ext_modules = [textypy_libtexty],
    packages=['textypy']
)
