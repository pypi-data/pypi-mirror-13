def goose_content_extract(raw_html, language=None):
    from textypy_libtexty import (
        goose_content_extract as cpp_extract,
        goose_content_extract_with_language as cpp_with_lang
    )
    if language is not None:
        return cpp_with_lang(raw_html, language)
    return cpp_extract(raw_html)
