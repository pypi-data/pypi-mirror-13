"""
Functions that implement analysis and synthesis of sounds using the Sinusoidal
plus Stochastic Model.

In this model the signal is first modeled using the sinusoidal model. Then the
residual is modeled using the stochastic model.
"""

from . import sine, stochastic
from ..utils import residual


def from_audio(x, fs, w, N, H, t, minSineDur, maxnSines, freqDevOffset, freqDevSlope, stocf):
    """
    Analyzes a sound using the sinusoidal plus stochastic model.

    :param x: input sound
    :param fs: sampling rate
    :param w: analysis window
    :param N: FFT size
    :param t: threshold in negative dB
    :param minSineDur: minimum duration of sinusoidal tracks
    :param maxnSines: maximum number of parallel sinusoids
    :param freqDevOffset: frequency deviation allowed in the sinusoids from frame to frame at frequency 0
    :param freqDevSlope: slope of the frequency deviation, higher frequencies have bigger deviation
    :param stocf: decimation factor used for the stochastic approximation
    :returns:
      - hfreq, hmag, hphase: harmonic frequencies, magnitude and phases
      - stocEnv: stochastic residual
    """

    # perform sinusoidal analysis
    tfreq, tmag, tphase = sine.from_audio(x, fs, w, N, H, t, maxnSines, minSineDur, freqDevOffset, freqDevSlope)
    Ns = 512
    # subtract sinusoids from original sound
    xr = residual.subtract_sinusoids(x, Ns, H, tfreq, tmag, tphase, fs)
    # compute stochastic model of residual
    stocEnv = stochastic.from_audio(xr, H, H * 2, stocf)
    return tfreq, tmag, tphase, stocEnv


def to_audio(tfreq, tmag, tphase, stocEnv, N, H, fs):
    """
    Synthesizes a sound using the sinusoidal plus stochastic model.

    :param tfreq: sinusoidal frequencies
    :param tmag: sinusoidal amplitudes
    :param tphase: sinusoidal phases
    :param stocEnv: stochastic envelope
    :param N: synthesis FFT size
    :param H: hop size
    :param fs: sampling rate
    :returns:
      - y: output sound
      - ys: sinusoidal component
      - yst: stochastic component
    """

    # synthesize sinusoids
    ys = sine.to_audio(tfreq, tmag, tphase, N, H, fs)
    # synthesize stochastic residual
    yst = stochastic.to_audio(stocEnv, H, H * 2)
    # sum sinusoids and stochastic components
    end = min(ys.size, yst.size)
    y = ys[:end] + yst[:end]
    return y, ys, yst
