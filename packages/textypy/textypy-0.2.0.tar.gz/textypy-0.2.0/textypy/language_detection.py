from textypy_libtexty import detect_language

def initialize():
    from .common import in_data_dir
    from textypy_libtexty import init_global_language_profiles_from_file
    init_global_language_profiles_from_file(
        in_data_dir('language_profiles.json')
    )

def cleanup():
    from textypy_libtexty import destroy_global_language_profiles
    destroy_global_language_profiles()
