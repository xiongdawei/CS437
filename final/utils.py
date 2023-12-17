import numpy as np
from typing import Any


class RadarConfig:
    """Radar configuration wrapper and parser. Supports easier access to the configuration file.
    
    Example:
        config = RadarConfig("ADCDataCapture.cfg")
        print(config["chirpComnCfg"])
    """
    def __init__(self, config_path):
        self.data = self.parse(config_path)

        self.Fs = 100e6 / int(self.data["chirpComnCfg"][0])      # Sampling Frequency
        C = 3e8   # speed of light
        self.S = int(self.data["chirpTimingCfg"][3]) * 1e12      # Chirp Slope

        self.d_max = self.Fs * C / 2 / self.S   # max range = Fs * c / (2 * S)

    def parse(self, config_path):
        """Parse the configuration file."""
        config = {}
        with open(config_path, "r") as f:
            for line in f:
                if line.startswith("%"):  # comment
                    continue
                if line.startswith("\n"):
                    continue
                # example line: chirpComnCfg 12 0 0 128 4 20 0
                # config = {"chirpComnCfg": ["12", "0", "0", "128", "4", "20", "0"]}
                data = line.strip().split()
                config[data[0]] = data[1:]
        return config
    
    def __getitem__(self, __name: str) -> Any:
        return self.data[__name]
    
    def getRangeBins(self, nFFT: int):
        """Get range profile from a single chirp.

        Args:
            nFFT (int): The number of FFT points.

        Returns:
            np.ndarray: The range profile.
        """
        
        delta_d = self.d_max / nFFT   # each range bin length = max range / nFFT

        vRange = np.arange(nFFT) * delta_d
        return vRange
    
    def getVelocityBins(self, nFFT: int):
        """Get velocity bins.

        Args:
            nFFT (int): The number of FFT points.

        Returns:
            np.ndarray: The velocity bins.
        """
        Fs = 100e6 / int(self.data["chirpComnCfg"][0])      # Sampling Frequency
        c = 3e8   # speed of light
        S = int(self.data["chirpTimingCfg"][3]) * 1e12      # Chirp Slope

        v_max = c / 2 / S   # max velocity = c / (2 * S)
        delta_v = v_max / nFFT

        vRange = np.arange(nFFT) * delta_v
        return vRange


if __name__ == "__main__":
    config = RadarConfig("ADCDataCapture.cfg")
    print(config.d_max)
