import matplotlib.pyplot as plt
import numpy as np
from utils import RadarConfig

radar_config = RadarConfig("ADCDataCapture.cfg")

class DataPlotter:
    @staticmethod
    def plotRangeProfile(rangeProfile: np.ndarray, extent_x=None):
        """Plot the range profile.

        Args:
            rangeProfile (np.ndarray): The range profile.
            extent_x (tuple, optional): The x axis extent. Defaults to [0, len(rangeProfile)].
        """
        # Plot range profile, x axis is frame index, y axis is range bin index
        plt.figure()
        vRange = radar_config.getRangeBins(rangeProfile.shape[1]) / 2

        # Set x axis extent
        if extent_x is None:
            extent = [0, rangeProfile.shape[0], vRange[-1], vRange[0]]
        else:
            extent = [extent_x[0], extent_x[1], vRange[-1], vRange[0]]

        plt.imshow(rangeProfile.T, aspect="auto", extent=extent)
        plt.xlabel("Frame index")
        plt.ylabel("Range (m)")
        plt.title("Range profile")
        plt.colorbar()
        plt.show()

    @staticmethod
    def plotRangeFrame(rangeProfile: np.ndarray, frame_idx: int):
        """Plot the range profile for a single frame.

        Args:
            rangeProfile (np.ndarray): The range profile.
            frame_idx (int): The frame index.
        """
        plt.figure()
        plt.plot(rangeProfile[frame_idx, :])
        plt.xlabel("Range bin index")
        plt.ylabel("Amplitude")
        plt.title("Range profile for frame {}".format(frame_idx))
        plt.show()

    @staticmethod
    def plotRangeDoppler(rangeDoppler: np.ndarray):
        """Plot the range-Doppler map.

        Args:
            rangeDoppler (np.ndarray): The range-Doppler map.
        """
        # Plot range-Doppler map, x axis is frame index, y axis is Doppler bin index
        plt.figure()
        # range_doppler_profile_normalized = 20 * np.log2(
        #     rangeDoppler / np.max(rangeDoppler)
        # )

        plt.imshow(rangeDoppler.T, aspect="auto")

        plt.xlabel("Doppler bin index")
        plt.ylabel("Range bin index")
        plt.title("Range-Doppler map")
        plt.colorbar()
        plt.show()
