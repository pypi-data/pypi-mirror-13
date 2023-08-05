# cli/param defaults
find_meta = False
find_package_string = ''
search_string = ''
build_package_path = '.'
find_cache = False
repository_url = 'https://index.spacy.io'

try:
    import os
    import spacy
    data_path = os.path.abspath(os.path.join(os.path.dirname(spacy.__file__), 'data'))
except ImportError:
    data_path = None

# misc
CHUNK_SIZE = 1024 * 16
ARCHIVE_FILENAME = 'archive.gz'
META_FILENAME = 'meta.json'
COMPRESSLEVEL = 9
COOKIES_FILENAME = 'cookies.txt'
CACHE_DIRNAME = '__cache__'
