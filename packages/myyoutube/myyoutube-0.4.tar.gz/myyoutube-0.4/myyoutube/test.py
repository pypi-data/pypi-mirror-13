# coding=utf-8
from __future__ import unicode_literals

import os
from myyoutube.uploader import upload
#file=os.path.join(os.path.dirname(__file__),"0.mp4")
file=os.path.join(os.path.dirname(__file__),"/Users/m/0.ts")
upload(file=file, title="TS테스트 입니다.",description="b",tags="c,d".split(","),allow_interactive=True)