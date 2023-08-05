#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 imm studios, z.s.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import time
import json
import subprocess

from .common import decode_if_py3
from .shell import Shell

__all__ = ["ffmpeg", "ffprobe", "ffanalyse", "join_filters", "filter_deinterlace", "filter_arc"]


def ffmpeg(fin, fout, profile=[], start=False, duration=False, progress_handler=None):
    cmd = ["ffmpeg", "-y"]
    if start:
        cmd.extend(["-ss", str(start)])            
    cmd.extend(["-i", fin])
    if duration:
        cmd.extend(["-t", str(duration)])
    for p in profile:
        if len(p) == 2 and type(p) != str:
            key, val = p
        else:
            key = p
            val = False
        cmd.append("-{}".format(key))
        if val:
            cmd.append(str(val))
    cmd.append(fout)
    proc = subprocess.Popen(cmd)
    while proc.poll() == None:
        #TODO: Progress handler
        time.sleep(.1)
    if proc.returncode:
        return False
    return True


def ffprobe(fname):
    """Runs ffprobe on file and returns python dict with result"""
    if not os.path.exists(fname):
        return False
    cmd = [
        "ffprobe",
        "-show_format",
        "-show_streams",
        "-print_format", "json",
        fname
        ]
    FNULL = open(os.devnull, "w")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=FNULL)
    while proc.poll() == None:
        time.sleep(.1)
    if proc.returncode:
        return False
    return json.loads(decode_if_py3(proc.stdout.read()))


def ffanalyse(fname):
    """Run several analysis filters. Work in progress. Do not use"""
    result = {}
    tags = [
            ("mean_volume:", "audio/gain/mean"),
            ("max_volume:",  "audio/gain/peak"),
            ("I:",           "audio/r128/i"),
            ("Threshold:",   "audio/r128/t"),
            ("LRA:",         "audio/r128/lra"),
            ("Threshold:",   "audio/r128/lra/t"),
            ("LRA low:",     "audio/r128/lra/l"),
            ("LRA high:",    "audio/r128/lra/r"),
        ]
    exp_tag = tags.pop(0) 
    filters = "silencedetect=n=-20dB:d=5,ebur128,volumedetect"
    cmd = "ffmpeg -i \"{}\" -filter_complex \"{}\" -f null -".format(fname, filters)
    shell = Shell(cmd)
    silences = []
    for line in shell.stderr().readlines():
        line = line.strip()
        if line.find("silence_end") > -1:
            e, d = line.split("|")
            e = e.split(":")[1].strip()
            d = d.split(":")[1].strip()
            try:
                e = float(e)
                s = max(0, e - float(d))
            except:
                pass
            else:
                silences.append([s, e])
        if line.find(exp_tag[0]) > -1:
            value = float(line.split()[-2])
            result[exp_tag[1]] =  value
            try:
                exp_tag = tags.pop(0)
            except:
                break

##
# Filters
##


def join_filters(*filters):
    """Joins multiple filters"""
    return "[in]{}[out]".format("[out];[out]".join(i for i in filters if i))


def filter_deinterlace():
    """Yadif deinterlace"""
    return "yadif=0:-1:0"


def filter_arc(w, h, aspect):
    """Aspect ratio convertor. you must specify output size and source aspect ratio (as float)"""
    taspect = float(w)/h
    if abs(taspect - aspect) < 0.01:
        return "scale=%s:%s"%(w,h)
    if taspect > aspect: # pillarbox
        pt = 0
        ph = h
        pw = int (h*aspect)
        pl = int((w - pw)/2.0)
    else: # letterbox
        pl = 0
        pw = w
        ph = int(w * (1/aspect))
        pt = int((h - ph)/2.0)
    return "scale=%s:%s[out];[out]pad=%s:%s:%s:%s:black" % (pw,ph,w,h,pl,pt) 
