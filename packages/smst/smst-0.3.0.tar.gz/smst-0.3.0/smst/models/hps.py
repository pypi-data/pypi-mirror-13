# functions that implement analysis and synthesis of sounds using the Harmonic plus Stochastic Model
# (for example usage check the examples models_interface)

import math

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import resample, blackmanharris, triang, hanning

from scipy.fftpack import fft, ifft

from . import dft, harmonic, sine, stochastic
from ..utils import peaks, residual, synth


def from_audio(x, fs, w, N, H, t, nH, minf0, maxf0, f0et, harmDevSlope, minSineDur, Ns, stocf):
    """
    Analysis of a sound using the harmonic plus stochastic model
    x: input sound, fs: sampling rate, w: analysis window; N: FFT size, t: threshold in negative dB,
    nH: maximum number of harmonics, minf0: minimum f0 frequency in Hz,
    maxf0: maximim f0 frequency in Hz; f0et: error threshold in the f0 detection (ex: 5),
    harmDevSlope: slope of harmonic deviation; minSineDur: minimum length of harmonics
    returns hfreq, hmag, hphase: harmonic frequencies, magnitude and phases; stocEnv: stochastic residual
    """

    # perform harmonic analysis
    hfreq, hmag, hphase = harmonic.from_audio(x, fs, w, N, H, t, nH, minf0, maxf0, f0et, harmDevSlope, minSineDur)
    # subtract sinusoids from original sound
    xr = residual.subtract_sinusoids(x, Ns, H, hfreq, hmag, hphase, fs)
    # perform stochastic analysis of residual
    stocEnv = stochastic.from_audio(xr, H, H * 2, stocf)
    return hfreq, hmag, hphase, stocEnv


def to_audio(hfreq, hmag, hphase, stocEnv, N, H, fs):
    """
    Synthesis of a sound using the harmonic plus stochastic model
    hfreq, hmag: harmonic frequencies and amplitudes; stocEnv: stochastic envelope
    Ns: synthesis FFT size; H: hop size, fs: sampling rate
    returns y: output sound, yh: harmonic component, yst: stochastic component
    """

    yh = sine.to_audio(hfreq, hmag, hphase, N, H, fs)  # synthesize harmonics
    yst = stochastic.to_audio(stocEnv, H, H * 2)  # synthesize stochastic residual
    y = yh[:min(yh.size, yst.size)] + yst[:min(yh.size, yst.size)]  # sum harmonic and stochastic components
    return y, yh, yst


def reconstruct(x, fs, w, N, t, nH, minf0, maxf0, f0et, stocf):
    """
    Analysis/synthesis of a sound using the harmonic plus stochastic model, one frame at a time, no harmonic tracking
    x: input sound; fs: sampling rate, w: analysis window; N: FFT size (minimum 512), t: threshold in negative dB,
    nH: maximum number of harmonics, minf0: minimum f0 frequency in Hz; maxf0: maximim f0 frequency in Hz,
    f0et: error threshold in the f0 detection (ex: 5); stocf: decimation factor of mag spectrum for stochastic analysis
    returns y: output sound, yh: harmonic component, yst: stochastic component
    """

    hM1 = int(math.floor((w.size + 1) / 2))  # half analysis window size by rounding
    hM2 = int(math.floor(w.size / 2))  # half analysis window size by floor
    Ns = 512  # FFT size for synthesis (even)
    H = Ns / 4  # Hop size used for analysis and synthesis
    hNs = Ns / 2
    pin = max(hNs, hM1)  # initialize sound pointer in middle of analysis window
    pend = x.size - max(hNs, hM1)  # last sample to start a frame
    yhw = np.zeros(Ns)  # initialize output sound frame
    ystw = np.zeros(Ns)  # initialize output sound frame
    yh = np.zeros(x.size)  # initialize output array
    yst = np.zeros(x.size)  # initialize output array
    w = w / sum(w)  # normalize analysis window
    sw = np.zeros(Ns)
    ow = triang(2 * H)  # overlapping window
    sw[hNs - H:hNs + H] = ow
    bh = blackmanharris(Ns)  # synthesis window
    bh = bh / sum(bh)  # normalize synthesis window
    wr = bh  # window for residual
    sw[hNs - H:hNs + H] = sw[hNs - H:hNs + H] / bh[hNs - H:hNs + H]  # synthesis window for harmonic component
    sws = H * hanning(Ns) / 2  # synthesis window for stochastic
    hfreqp = []
    f0stable = 0
    while pin < pend:
        # -----analysis-----
        x1 = x[pin - hM1:pin + hM2]  # select frame
        mX, pX = dft.from_audio(x1, w, N)  # compute dft
        ploc = peaks.find_peaks(mX, t)  # find peaks
        iploc, ipmag, ipphase = peaks.interpolate_peaks(mX, pX, ploc)  # refine peak values
        ipfreq = fs * iploc / N  # convert peak locations to Hz
        f0t = peaks.find_fundamental_twm(ipfreq, ipmag, f0et, minf0, maxf0, f0stable)  # find f0
        if ((f0stable == 0) & (f0t > 0)) \
                or ((f0stable > 0) & (np.abs(f0stable - f0t) < f0stable / 5.0)):
            f0stable = f0t  # consider a stable f0 if it is close to the previous one
        else:
            f0stable = 0
        hfreq, hmag, hphase = harmonic.find_harmonics(ipfreq, ipmag, ipphase, f0t, nH, hfreqp, fs)  # find harmonics
        hfreqp = hfreq
        ri = pin - hNs - 1  # input sound pointer for residual analysis
        xw2 = x[ri:ri + Ns] * wr  # window the input sound
        fftbuffer = np.zeros(Ns)  # reset buffer
        fftbuffer[:hNs] = xw2[hNs:]  # zero-phase window in fftbuffer
        fftbuffer[hNs:] = xw2[:hNs]
        X2 = fft(fftbuffer)  # compute FFT for residual analysis
        # -----synthesis-----
        Yh = synth.spectrum_for_sinusoids(hfreq, hmag, hphase, Ns, fs)  # generate spec sines of harmonic component
        Xr = X2 - Yh  # get the residual complex spectrum
        mXr = 20 * np.log10(abs(Xr[:hNs]))  # magnitude spectrum of residual
        mXrenv = resample(np.maximum(-200, mXr), mXr.size * stocf)  # decimate the magnitude spectrum and avoid -Inf
        stocEnv = resample(mXrenv, hNs)  # interpolate to original size
        pYst = 2 * np.pi * np.random.rand(hNs)  # generate phase random values
        Yst = np.zeros(Ns, dtype=complex)
        Yst[:hNs] = 10 ** (stocEnv / 20) * np.exp(1j * pYst)  # generate positive freq.
        Yst[hNs + 1:] = 10 ** (stocEnv[:0:-1] / 20) * np.exp(-1j * pYst[:0:-1])  # generate negative freq.

        fftbuffer = np.real(ifft(Yh))  # inverse FFT of harmonic spectrum
        yhw[:hNs - 1] = fftbuffer[hNs + 1:]  # undo zero-phase window
        yhw[hNs - 1:] = fftbuffer[:hNs + 1]

        fftbuffer = np.real(ifft(Yst))  # inverse FFT of stochastic spectrum
        ystw[:hNs - 1] = fftbuffer[hNs + 1:]  # undo zero-phase window
        ystw[hNs - 1:] = fftbuffer[:hNs + 1]

        yh[ri:ri + Ns] += sw * yhw  # overlap-add for sines
        yst[ri:ri + Ns] += sws * ystw  # overlap-add for stochastic
        pin += H  # advance sound pointer

    y = yh + yst  # sum of harmonic and stochastic components
    return y, yh, yst


# functions that implement transformations using the hpsModel

def scale_time(hfreq, hmag, stocEnv, timeScaling):
    """
    Time scaling of the harmonic plus stochastic representation
    hfreq, hmag: harmonic frequencies and magnitudes, stocEnv: residual envelope
    timeScaling: scaling factors, in time-value pairs
    returns yhfreq, yhmag, ystocEnv: hps output representation
    """

    if timeScaling.size % 2 != 0:  # raise exception if array not even length
        raise ValueError("Time scaling array does not have an even size")

    L = hfreq[:, 0].size  # number of input frames
    maxInTime = max(timeScaling[::2])  # maximum value used as input times
    maxOutTime = max(timeScaling[1::2])  # maximum value used in output times
    outL = int(L * maxOutTime / maxInTime)  # number of output frames
    inFrames = (L - 1) * timeScaling[::2] / maxInTime  # input time values in frames
    outFrames = outL * timeScaling[1::2] / maxOutTime  # output time values in frames
    timeScalingEnv = interp1d(outFrames, inFrames, fill_value=0)  # interpolation function
    indexes = timeScalingEnv(np.arange(outL))  # generate frame indexes for the output
    yhfreq = hfreq[round(indexes[0]), :]  # first output frame
    yhmag = hmag[round(indexes[0]), :]  # first output frame
    ystocEnv = stocEnv[round(indexes[0]), :]  # first output frame
    for l in indexes[1:]:  # iterate over all output frame indexes
        yhfreq = np.vstack((yhfreq, hfreq[round(l), :]))  # get the closest input frame
        yhmag = np.vstack((yhmag, hmag[round(l), :]))  # get the closest input frame
        ystocEnv = np.vstack((ystocEnv, stocEnv[round(l), :]))  # get the closest input frame
    return yhfreq, yhmag, ystocEnv


def morph(hfreq1, hmag1, stocEnv1, hfreq2, hmag2, stocEnv2, hfreqIntp, hmagIntp, stocIntp):
    """
    Morph between two sounds using the harmonic plus stochastic model
    hfreq1, hmag1, stocEnv1: hps representation of sound 1
    hfreq2, hmag2, stocEnv2: hps representation of sound 2
    hfreqIntp: interpolation factor between the harmonic frequencies of the two sounds, 0 is sound 1 and 1 is sound 2 (time,value pairs)
    hmagIntp: interpolation factor between the harmonic magnitudes of the two sounds, 0 is sound 1 and 1 is sound 2  (time,value pairs)
    stocIntp: interpolation factor between the stochastic representation of the two sounds, 0 is sound 1 and 1 is sound 2  (time,value pairs)
    returns yhfreq, yhmag, ystocEnv: hps output representation
    """

    if hfreqIntp.size % 2 != 0:  # raise exception if array not even length
        raise ValueError("Harmonic frequencies interpolation array does not have an even size")

    if hmagIntp.size % 2 != 0:  # raise exception if array not even length
        raise ValueError("Harmonic magnitudes interpolation does not have an even size")

    if stocIntp.size % 2 != 0:  # raise exception if array not even length
        raise ValueError("Stochastic component array does not have an even size")

    L1 = hfreq1[:, 0].size  # number of frames of sound 1
    L2 = hfreq2[:, 0].size  # number of frames of sound 2
    hfreqIntp[::2] = (L1 - 1) * hfreqIntp[::2] / hfreqIntp[-2]  # normalize input values
    hmagIntp[::2] = (L1 - 1) * hmagIntp[::2] / hmagIntp[-2]  # normalize input values
    stocIntp[::2] = (L1 - 1) * stocIntp[::2] / stocIntp[-2]  # normalize input values
    hfreqIntpEnv = interp1d(hfreqIntp[0::2], hfreqIntp[1::2], fill_value=0)  # interpolation function
    hfreqIndexes = hfreqIntpEnv(np.arange(L1))  # generate frame indexes for the output
    hmagIntpEnv = interp1d(hmagIntp[0::2], hmagIntp[1::2], fill_value=0)  # interpolation function
    hmagIndexes = hmagIntpEnv(np.arange(L1))  # generate frame indexes for the output
    stocIntpEnv = interp1d(stocIntp[0::2], stocIntp[1::2], fill_value=0)  # interpolation function
    stocIndexes = stocIntpEnv(np.arange(L1))  # generate frame indexes for the output
    yhfreq = np.zeros_like(hfreq1)  # create empty output matrix
    yhmag = np.zeros_like(hmag1)  # create empty output matrix
    ystocEnv = np.zeros_like(stocEnv1)  # create empty output matrix

    for l in range(L1):  # generate morphed frames
        # identify harmonics that are present in both frames
        harmonics = np.intersect1d(np.array(np.nonzero(hfreq1[l, :]), dtype=np.int)[0],
                                   np.array(np.nonzero(hfreq2[round(L2 * l / float(L1)), :]), dtype=np.int)[0])
        # interpolate the frequencies of the existing harmonics
        yhfreq[l, harmonics] = (1 - hfreqIndexes[l]) * hfreq1[l, harmonics] + hfreqIndexes[l] * hfreq2[
            round(L2 * l / float(L1)), harmonics]
        # interpolate the magnitudes of the existing harmonics
        yhmag[l, harmonics] = (1 - hmagIndexes[l]) * hmag1[l, harmonics] + hmagIndexes[l] * hmag2[
            round(L2 * l / float(L1)), harmonics]
        # interpolate the stochastic envelopes of both frames
        ystocEnv[l, :] = (1 - stocIndexes[l]) * stocEnv1[l, :] + stocIndexes[l] * stocEnv2[round(L2 * l / float(L1)), :]
    return yhfreq, yhmag, ystocEnv
