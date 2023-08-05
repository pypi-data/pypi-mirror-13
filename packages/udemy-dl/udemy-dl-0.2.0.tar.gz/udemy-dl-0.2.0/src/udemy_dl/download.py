import os
import sys
import wget
import subprocess
import requests

class DLException(Exception):
    """Raise if some lectured failed to download."""
    pass

def download(link, filename):
    """Download files to given destination file-name."""
    try:
        if 'pdf' in link:
            filename = filename.rstrip('mp4')+'pdf'
        elif 'mp3' in link:
            filename = filename.rstrip('mp4')+'mp3'

        if 'youtube.com' in link:
            youtube_dl(link, filename)
        else:
            try:
                curl_dl(link, filename)
            except OSError:
                if not os.path.exists(filename):
                    wget.download(link, filename)
                else:
                    raise DLException('Failed to download this lecture')
    except TypeError:
        print("Skipped. Url wasn't parsed properly.")


def curl_dl(link, filename):
    """Use curl as the downloader."""
    command = ['curl', '-C', '-', link, '-o', filename]

    cert_path = requests.certs.where()
    if cert_path:
        command.extend(['--cacert', cert_path])
    else:
        command.extend(['--insecure'])
    subprocess.call(command)


def dl_progress(num_blocks, block_size, total_size):
    """Show a decent download progress indication."""
    progress = num_blocks * block_size * 100 / total_size
    if num_blocks != 0:
        sys.stdout.write(4 * '\b')
    sys.stdout.write('{0:3d}%'.format((progress)))


def youtube_dl(link, filename):
    """Use youtube-dl as the downloader if videos are in youtube.com."""
    try:
        subprocess.call(['youtube-dl', '-o', filename, link])
    except OSError:
        raise DLException('Install youtube-dl to download this lecture')

