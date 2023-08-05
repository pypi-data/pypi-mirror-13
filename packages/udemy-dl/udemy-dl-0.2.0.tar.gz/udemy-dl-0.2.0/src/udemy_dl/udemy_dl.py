#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import requests.sessions
import argparse
import getpass
import sys
import re
import os
import json
from .download import download, DLException
from ._version import __version__



class Session:
    """Starting session with proper headers to access udemy site"""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
               'X-Requested-With': 'XMLHttpRequest',
               'Host': 'www.udemy.com',
               'Referer': 'https://www.udemy.com/join/login-popup'}

    def __init__(self):
        self.session = requests.sessions.Session()
        
    def set_auth_headers(self, access_token, client_id):
        """ Setting up authentication headers. """
        self.headers['X-Udemy-Bearer-Token'] = access_token
        self.headers['X-Udemy-Client-Id'] = client_id
        self.headers['Authorization'] = "Bearer " + access_token
        self.headers['X-Udemy-Authorization'] = "Bearer " + access_token

    def get(self, url):
        """ Retreiving content of a given url. """
        return self.session.get(url, headers=self.headers)

    def post(self, url, data):
        """ HTTP post given data with requests object. """
        return self.session.post(url, data, headers=self.headers)


session = Session()


def get_csrf_token():
    """ Extractig CSRF Token from login page """
    response = session.get('https://www.udemy.com/join/login-popup')
    match = re.search("name=\'csrfmiddlewaretoken\' value=\'(.*)\'", response.text)
    return match.group(1)

def login(username, password):
    """ Login with popu-page. """
    login_url = 'https://www.udemy.com/join/login-popup/?displayType=ajax&display_type=popup&showSkipButton=1&returnUrlAfterLogin=https%3A%2F%2Fwww.udemy.com%2F&next=https%3A%2F%2Fwww.udemy.com%2F&locale=en_US'
    csrf_token = get_csrf_token()
    payload = {'isSubmitted': 1, 'email': username, 'password': password,
               'displayType': 'ajax', 'csrfmiddlewaretoken': csrf_token}
    response = session.post(login_url, payload)

    access_token = response.cookies.get('access_token')
    client_id = response.cookies.get('client_id')
    if access_token is None:
        print("Error: Couldn\'t fetch token !")
        sys.exit(1)
    session.set_auth_headers(access_token, client_id)

    response = response.text
    if 'error' in response:
        print(response)
        sys.exit(1)


def get_course_id(course_link):
    """ Retreiving course ID """
    response = session.get(course_link)
    matches = re.search('data-course-id="(\d+)"', response.text, re.IGNORECASE)
    return matches.groups()[0] if matches else None


def parse_video_url(course_id, lecture_id):
    """ Extracting video URLS. """
    get_url = 'https://www.udemy.com/api-2.0/users/me/subscribed-courses/{0}/lectures/{1}?video_only=&auto_play=&fields[lecture]=asset,embed_url&fields[asset]=asset_type,download_urls,title&instructorPreviewMode=False'.format(course_id, lecture_id)
    json_source = session.get(get_url).json()
    
    try:
        if json_source['asset']['download_urls']['Video']: 
            list_videos = [item_ for item_ in json_source['asset']['download_urls']['Video']]
            list_videos = sorted(list_videos,key=lambda item_: int(item_['label']),reverse=True)
            for element in list_videos:
                if element['label'] == '1080':
                    return element['file']
                elif element['label'] == '720':
                    return element['file']
                elif element['label'] == '480':
                    return element['file']
                elif element['label'] == '360':
                    return element['file']
                else:
                    print('Skipped. Couldn\'t fetch video')
                    return None
    except KeyError:
        try:
            if json_source['asset']['download_urls']['E-Book']:
                for element in json_source['asset']['download_urls']['E-Book']:
                    if element['label'] == 'download':
                        return element['file']
                    else:
                        print('Skipped. Couldn\'t fetch e-book')
                        return None
        except KeyError:
            if json_source['asset']['download_urls']['Audio']:
                for element in json_source['asset']['download_urls']['Audio']:
                    if element['label'] == 'download':
                        return element['file']
                    else:
                        print('Skipped. Couldn\'t fetch audio')
                        return None
    else:
        print('Skipped. Something unexpected')
        return None


def get_video_links(course_id, lecture_start, lecture_end):
    """ Getting video links from api 1.1. """
    course_url = 'https://www.udemy.com/api-1.1/courses/{0}/curriculum?fields[lecture]=@min,completionRatio,progressStatus&fields[quiz]=@min,completionRatio'.format(course_id)
    course_data = session.get(course_url).json()

    chapter = None
    video_list = []

    lecture_number = 1
    chapter_number = 0
    # A udemy course has chapters, each having one or more lectures
    for item in course_data:
        if item['__class'] == 'chapter':
            chapter = item['title']
            chapter_number += 1

        elif item['__class'] == 'lecture' and (item['assetType'] == 'Video' or item['assetType'] == 'E-Book' or item['assetType'] == 'VideoMashup' or item['assetType'] == 'Audio'):
            lecture = item['title']
            if valid_lecture(lecture_number, lecture_start, lecture_end):
                try:
                    lecture_id = item['id']
                    video_url = parse_video_url(course_id, lecture_id)
                    video_list.append({'chapter': chapter,
                                       'lecture': lecture,
                                       'video_url': video_url,
                                       'lecture_number': lecture_number,
                                       'chapter_number': chapter_number})
                except Exception as e:
                    print('Cannot download lecture "{0!s}"'.format((lecture)))
            lecture_number += 1
    return video_list


def valid_lecture(lecture_number, lecture_start, lecture_end):
    """ Testing if the given lecture number is valid and exisit. """
    if lecture_start and lecture_end:
        return lecture_start <= lecture_number <= lecture_end
    elif lecture_start:
        return lecture_start <= lecture_number
    else:
        return lecture_number <= lecture_end


def sanitize_path(s):
    """ Cleaning up path for saving files. """
    return "".join([c for c in s if c.isalpha() or c.isdigit() or c in ' .-_,']).rstrip()


def mkdir(directory):
    """ Creating output directory structure, if not exisit. """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_video(directory, filename, link):
    """ Get video content. """
    print('Downloading {0!s}  '.format((filename.encode('utf-8'))))
    previous_dir = os.getcwd()
    mkdir(directory)
    os.chdir(directory)
    try:
        download(link, filename)
    except DLException as e:
        print('Couldn\'t download this lecture: {0}'.format(e))
    os.chdir(previous_dir)
    print('\n'),


def save_link(url):
    """save links to a file named links.txt"""
    url_str = str(url)
    with open('links.txt', 'a') as sv_file:
        sv_file.write(url_str + '\n')
        sv_file.close()


def udemy_dl(username, password, course_link, lecture_start, lecture_end, dest_dir="", save_links = None):
    """ Login into udemy and do all magic. """

    login(username, password)

    course_id = get_course_id(course_link)
    if not course_id:
        print('Failed to get course ID')
        return

    for video in get_video_links(course_id, lecture_start, lecture_end):
        if save_links:
            save_link(video['video_url'])
        else:
            directory = '{0:02d} {1!s}'.format(video['chapter_number'], video['chapter'])
            directory = sanitize_path(directory)

            if dest_dir:
                directory = os.path.join(dest_dir, directory)

            filename = '{0:03d} {1!s}.mp4'.format(video['lecture_number'], video['lecture'])
            filename = sanitize_path(filename)

            get_video(directory, filename, video['video_url'])
            
    if os.path.exists('links.txt'):
        print('links saved to file successfully.')

    session.get('http://www.udemy.com/user/logout')


def is_integer(p):
    """ Check if given value is an intiger. """
    try:
        int(p)
        return True
    except ValueError:
        return False

def main():
    """ Accepting arguments and preparing """
    parser = argparse.ArgumentParser(description='Fetch all the videos for a udemy course')
    parser.add_argument('link', help='Link for udemy course', action='store')
    parser.add_argument('-u', '--username', help='Username/Email', default=None, action='store')
    parser.add_argument('-p', '--password', help='Password', default=None, action='store')
    parser.add_argument('--lecture-start', help='Lecture to start at (default is 1)', default=1, action='store')
    parser.add_argument('--lecture-end', help='Lecture to end at (default is last)', default=None, action='store')
    parser.add_argument('-o', '--output-dir', help='Output directory', default=None, action='store')
    parser.add_argument('-s', '--save-links', help='Do not download but save links to a file', action='store_const', const=True, default=None)
    parser.add_argument('-v', '--version', help='Display the version of udemy-dl and exit', action='version', version='%(prog)s {version}'.format(version=__version__))

    args = vars(parser.parse_args())

    username = args['username']
    password = args['password']
    link_args = args['link']
    link = re.search( r'(https://www.udemy.com/.*?)/', link_args+'/').group(1)
    lecture_start = args['lecture_start']
    lecture_end = args['lecture_end']
    save_links = args['save_links']

    if lecture_start is not None:
        if not is_integer(lecture_start) or int(lecture_start) <= 0:
            print('--lecture_start requires natural number argument')
            sys.exit(1)
        lecture_start = int(lecture_start)
    if lecture_end is not None:
        if not is_integer(lecture_end) or int(lecture_end) <= 0:
            print('--lecture_end requires natural number argument')
            sys.exit(1)
        lecture_end = int(lecture_end)
    
    if args['output_dir']:
        # Normalize the output path if specified
        output_dir = os.path.normpath(args['output_dir'])
    else:
        # Get output dir name from the URL
        output_dir = os.path.join(".", link.rsplit('/', 1)[1])

    if not username:
        try:
            username = raw_input("Username/Email: ")  # Python 2
        except NameError:
            username = input("Username/Email: ")  # Python 3

    if not password:
        password = getpass.getpass(prompt='Password: ')

    print('Downloading to: {0!s}\n'.format((os.path.abspath(output_dir))))

    udemy_dl(username, password, link, lecture_start, lecture_end, output_dir, save_links)


if __name__ == '__main__':
    main()
