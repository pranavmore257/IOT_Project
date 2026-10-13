import numpy as np
from typing import Dict, Any, Tuple

class AudioFeatureExtractor:
    """Extracts MFCCs, spectral centroid, zero-crossing rate, and spectral roll-off."""

    def __init__(self, sample_rate: int = 16000, n_mfcc: int = 20, n_mels: int = 64):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.has_librosa = False

        try:
            import librosa
            self.has_librosa = True
        except ImportError:
            self.has_librosa = False

    def extract_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Extracts acoustic features from 1D audio waveform.
        Returns dictionary with mfcc_mean, spectral_centroid, zcr, dominant_freq.
        """
        if len(audio) == 0:
            return {
                "mfcc": np.zeros(self.n_mfcc),
                "spectral_centroid": 0.0,
                "zero_crossing_rate": 0.0,
                "dominant_freq": 0.0
            }

        if self.has_librosa:
            return self._extract_librosa(audio)
        else:
            return self._extract_scipy_numpy(audio)

    def _extract_librosa(self, audio: np.ndarray) -> Dict[str, Any]:
        import librosa
        try:
            mfccs = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=self.n_mfcc)
            mfcc_mean = np.mean(mfccs, axis=1)

            centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)
            centroid_mean = float(np.mean(centroid))

            zcr = librosa.feature.zero_crossing_rate(audio)
            zcr_mean = float(np.mean(zcr))

            # FFT for dominant frequency
            fft_vals = np.abs(np.fft.rfft(audio))
            freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
            dom_freq = float(freqs[np.argmax(fft_vals)])

            return {
                "mfcc": mfcc_mean,
                "spectral_centroid": centroid_mean,
                "zero_crossing_rate": zcr_mean,
                "dominant_freq": dom_freq
            }
        except Exception:
            return self._extract_scipy_numpy(audio)

    def _extract_scipy_numpy(self, audio: np.ndarray) -> Dict[str, Any]:
        """NumPy/SciPy fallback feature extractor when librosa is not available."""
        # Zero crossing rate
        zero_crosses = np.nonzero(np.diff(audio > 0))[0]
        zcr = float(len(zero_crosses)) / max(1, len(audio))

        # FFT Spectrum
        fft_vals = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
        
        # Dominant frequency
        dom_idx = np.argmax(fft_vals)
        dom_freq = float(freqs[dom_idx])

        # Spectral centroid
        sum_fft = np.sum(fft_vals)
        if sum_fft > 1e-6:
            centroid = float(np.sum(freqs * fft_vals) / sum_fft)
        else:
            centroid = 0.0

        # Synthetic/approximate 20 frequency band energies as MFCC stand-in
        band_size = len(fft_vals) // self.n_mfcc
        mfcc_approx = []
        for i in range(self.n_mfcc):
            start = i * band_size
            end = (i + 1) * band_size if i < self.n_mfcc - 1 else len(fft_vals)
            band_energy = float(np.mean(fft_vals[start:end])) if end > start else 0.0
            mfcc_approx.append(np.log1p(band_energy))

        return {
            "mfcc": np.array(mfcc_approx),
            "spectral_centroid": centroid,
            "zero_crossing_rate": zcr,
            "dominant_freq": dom_freq
        }
