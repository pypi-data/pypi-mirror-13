#!/usr/bin/env python
"""
New version of audio sync for Python
"""

import logging
import scipy.signal
import numpy as np




def find_offset(signal0,signal1,audio_sample_rate=48000.,video_fps=30.):
    """
    Finds the offset between two audio signals using fftconvolve to 
    do the auto- and cross-correlations.  The signals are assumed to be
    mono and the audio sample rate and video fps must be known. 
    """
    corr01 = scipy.signal.fftconvolve(signal0,signal1[::-1],mode="full")
    corr00 = scipy.signal.fftconvolve(signal0,signal0[::-1],mode="valid")
    corr11 = scipy.signal.fftconvolve(signal1,signal1[::-1],mode="valid")
    lag = corr01.argmax()
    maxcorr = np.nanmax(corr01)/((corr00**0.5)*(corr11**0.5))
    offset_samples = int(len(corr01)/2)-lag
    offset_seconds = float(offset_samples)/float(audio_sample_rate)
    offset_frames = float(offset_samples)/float(audio_sample_rate) \
                    * float(video_fps)
    integer_offset = int(np.round(offset_frames))
    return offset_seconds,offset_frames,integer_offset,maxcorr[0]
