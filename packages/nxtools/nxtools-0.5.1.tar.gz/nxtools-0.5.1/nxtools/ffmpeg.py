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
from .misc import indent 
from .shell import Shell
from .logging import *

__all__ = ["ffmpeg", "ffprobe", "ffanalyse", "join_filters", "filter_deinterlace", "filter_arc"]


def _profiler(p):
    cmd = []
    if len(p) == 2 and type(p) != str:
        key, val = p
    else:
        key = p
        val = False
    cmd.append("-{}".format(key))
    if val:
        cmd.append(str(val))
    return cmd


def ffmpeg(input_path, output_path, output_format=[], start=False, duration=False, input_format=[], progress_handler=None, stdin=None, stdout=None):
    """Universal ffmpeg wrapper with progress and error handling.

    Parameters
    ----------
    input_path : string
        input file path
    output_path : string
        output file path
    output_format : list 
        list of (param, value) tuples specifiing output format
    start : float 
        start time in seconds (using fast seek)
    duration : float
        duration in seconds
    input_format : list 
        input format specification. same syntax as profile
    progress_handler : function
        method which will receive current progress as float
    stdin : file
        standard input (usable when input_path=="-")
    stdout : file
        standard output (usable when output_path=="-)"
    """

    cmd = ["ffmpeg", "-y"]
    if start:
        cmd.extend(["-ss", str(start)])
    for p in input_format:
        cmd.extend(_profiler(p))
    cmd.extend(["-i", input_path])
    if duration:
        cmd.extend(["-t", str(duration)])
    for p in output_format:
        cmd.extend(_profiler(p))
    cmd.append(output_path)
    buff = err_log = ""
    logging.debug("Executing", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE)
    while proc.poll() == None:
        ch = decode_if_py3(proc.stderr.read(1))
        if ch in ["\n", "\r"]:
            if buff.startswith("frame="):
                at_frame = buff.split("fps")[0].split("=")[1].strip()
                at_frame = int(at_frame)
                if progress_handler:
                    progress_handler(at_frame)
            else:
                err_log += buff + "\n"
            buff = ""
        else:
            buff += ch
    if proc.returncode:
        logging.error("Problem occured during transcoding\n\n{}\n\n".format(indent(err_log)))
        return False
    return True


def ffprobe(input_path):
    """Runs ffprobe on file and returns python dict with result"""
    if not os.path.exists(input_path):
        return False
    cmd = [
        "ffprobe",
        "-show_format",
        "-show_streams",
        "-print_format", "json",
        input_path
        ]
    FNULL = open(os.devnull, "w")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=FNULL)
    while proc.poll() == None:
        time.sleep(.1)
    if proc.returncode:
        return False
    return json.loads(decode_if_py3(proc.stdout.read()))


def ffanalyse(input_path):
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
    cmd = "ffmpeg -i \"{}\" -filter_complex \"{}\" -f null -".format(input_path, filters)
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
    return result

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
