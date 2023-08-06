import hashlib
import os
import shutil
import sys
import tarfile

import maxminddb
import requests

__doc__ = 'Function to keep a maxmind database file up to date'
__version__ = '0.1.1'
__url__ = 'https://github.com/yola/maxmind-updater'


def _hash_file(filename):
    if not os.path.exists(filename):
        return ''

    block_size = 65536
    hasher = hashlib.md5()

    with open(filename, 'rb') as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            hasher.update(buf)
    return hasher.hexdigest()


def update_db(db_path, license_key, edition_id):
    db_dir_path = os.path.abspath(os.path.dirname(db_path))
    db_archive_path = '%s.tar.gz' % db_path

    def maxmind_download(suffix, **kwargs):
        return requests.get('https://download.maxmind.com/app/geoip_download',
                            params={'license_key': license_key,
                                    'edition_id': edition_id,
                                    'suffix': suffix,
                                    },
                            **kwargs)

    expected_md5 = maxmind_download('tar.gz.md5').content
    curr_md5 = _hash_file(db_archive_path)
    if expected_md5 == curr_md5 and os.path.exists(db_path):
        return

    with open(db_archive_path, 'wb') as local_zip:
        for chunk in maxmind_download('tar.gz', stream=True
                                      ).iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                local_zip.write(chunk)

    with tarfile.open(db_archive_path) as tar_file:
        # We only want the mmdb file. Maxmind kindly includes things
        # we don't want.
        extract_members = [member for member in tar_file.getmembers()
                           if member.name.endswith('.mmdb')]
        assert len(extract_members) == 1
        tar_file.extractall(path=db_dir_path, members=extract_members)
        # extractall keeps the subfolder structure. Account for this by
        # appending the path to the db_dir_path where it was extracted.
        new_db_path = os.path.join(db_dir_path, extract_members[0].path)
    try:
        db = maxminddb.open_database(new_db_path)
        db.get('8.8.8.8')
        db.get('2001:420::')
    except Exception:
        sys.stderr.write('Retrieved invalid GeoIP database - '
                         'check MaxMind account details.\n')
        raise
    if not os.path.exists(db_dir_path):
        os.makedirs(db_dir_path)
    shutil.move(new_db_path, db_path)
    os.rmdir(os.path.dirname(new_db_path))
