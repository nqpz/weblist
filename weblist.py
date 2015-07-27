#!/usr/bin/env python3

import subprocess
import os.path
import tempfile
import base64


def load(fn):
    with open(fn) as f:
        return f.read().strip()

script_dir = os.path.dirname(__file__)
page_template = load(os.path.join(script_dir, 'page.html'))
media_block_template = load(os.path.join(script_dir, 'media-block.html'))
dir_block_template = load(os.path.join(script_dir, 'dir-block.html'))

def format(t, **kws):
    for k, v in kws.items():
        t = t.replace('{' + k + '}', v)
    return t

def run(*xs):
    subprocess.check_call(xs)

def thumbnail_image(inpath, real_inpath=None):
    outpath = os.path.join('.weblist', 'thumbnails', base64.b64encode(inpath.encode('utf-8'), b'-_').decode() + '.jpg')
    if real_inpath is not None:
        inpath = real_inpath
    run('convert', inpath, '-resize', '400x', '-quality', '75', outpath)
    return outpath

def thumbnail_video(inpath):
    with tempfile.TemporaryDirectory() as d:
        temp_outpath = os.path.join(d, 'frame.jpg')
        run('ffmpeg', '-i', inpath, '-ss', '1', '-frames:v', '1', temp_outpath)
        return thumbnail_image(inpath, temp_outpath)

def make_thumbnail(path):
    p = path.lower()
    if p.endswith('.jpg') or p.endswith('.png'):
        return (thumbnail_image(path), 'IMAGE')
    elif p.endswith('.mkv') or p.endswith('.webm') or p.endswith('.mp4'):
        return (thumbnail_video(path), 'VIDEO')
    
def prepare():
    os.makedirs(os.path.join('.weblist', 'thumbnails'), exist_ok=True)

def make_index():
    blocks = []
    for x in sorted(filter(lambda x: x != '.weblist' and x != 'index.html', os.listdir())):
        if os.path.isdir(x):
            block = format(dir_block_template, url=x)
        else:
            (thumb_path, file_type) = make_thumbnail(x)
            desc = file_type + ': ' + x
            block = format(media_block_template, url=x, thumbnail=thumb_path,
                           description=desc)
        blocks.append(block)
    page = format(page_template, content='\n'.join(blocks))
    with open('index.html', 'w') as f:
        f.write(page)

if __name__ == '__main__':
    prepare()
    make_index()
