import numpy as np
from utils import RadarConfig
from plot_data import DataPlotter as plt

# Some constants
Nd = 128  # number of doppler bins

class ProcessingPipeline:
    """Raw ADC to range profile and range doppler"""
    def __init__(self, npy_path: str):
        """Initialize the pipeline.
        
        Args:
            npy_path (str): The path to the npy file.
        """
        self.rawData = np.load(npy_path)
        self.data = np.array([frame["adcSamples"][:, 128:] for frame in self.rawData])
        self.radar_config = RadarConfig("ADCDataCapture.cfg")

    def getRangeProfile(self, antenna_idx=0, start_frame=0, end_frame=-1):
        """Get range FFT from a single chirp. Normalization is applied.

        Args:
            data (np.ndarray): The data array.
            antenna_idx (int, optional): The antenna index. Defaults to 0.

        Returns:
            np.ndarray: The range FFT with shape (num_chirps, num_range_bins)
        """
        data = self.data[start_frame:end_frame, antenna_idx, :]  # shape: (num_chirps, num_range_bins)
        rangeProfile = np.fft.fft(data, axis=1)
        rangeProfile = np.abs(rangeProfile)
        # Normalize
        rangeProfile = rangeProfile / np.max(rangeProfile)
        # FFT is double sided signal, we only need one side
        rangeProfile = rangeProfile[:, : rangeProfile.shape[1] // 2 ]
        return rangeProfile

    def getRangeDoppler(self, antenna_idx=0, start_frame=0, end_frame=-1):
        """Get range-Doppler map.

        Args:
            antenna_idx (int, optional): The antenna index. Defaults to 0.
            start_frame (int, optional): The start frame index. Defaults to 0.
            end_frame (int, optional): The end frame index. Defaults to -1.

        Returns:
            np.ndarray: The range-Doppler map.
        """
        # rangeProfile = np.fft.fft(self.data[start_frame:end_frame, antenna_idx, :], axis=1)
        # # rangeProfile = np.fft.fftshift(rangeProfile, axes=1)
        
        # rangeDoppler = np.fft.fft(rangeProfile, axis=0)
        # rangeDoppler = np.fft.fftshift(rangeDoppler, axes=0)
        # rangeDoppler = np.abs(rangeDoppler)

        data = self.data[start_frame:end_frame, antenna_idx, :]
        # data.shape: (num_chirps, num_range_bins)
        num_chirps, num_range_bins = data.shape
        rangeDoppler = np.fft.fft2(data, axes=(0, 1))
        rangeDoppler = rangeDoppler[:, : num_range_bins // 2]
        rangeDoppler = np.fft.fftshift(rangeDoppler, axes=0)
        rangeDoppler = np.abs(rangeDoppler)
        rangeDoppler = 10 * np.log10(rangeDoppler)
        return rangeDoppler

    def CFAR(
        self,
        range_doppler_map: np.ndarray,
        guard_cells=(4, 4),
        training_cells=(8, 8),
        threshold_factor=1.5,
    ):
        """
        Apply 2D CFAR filter to the range-Doppler map.

        Args:
            range_doppler_map (np.ndarray): The range-Doppler map.
            guard_cells (tuple): Number of guard cells in each dimension.
            training_cells (tuple): Number of training cells in each dimension.
            threshold_factor (float): Threshold factor for CFAR.

        Returns:
            np.ndarray: Filtered range-Doppler map.
        """
        filtered_map = np.zeros_like(range_doppler_map)

        # Iterate over the range and Doppler dimensions
        for r in range(guard_cells[0], range_doppler_map.shape[0] - guard_cells[0]):
            for d in range(guard_cells[1], range_doppler_map.shape[1] - guard_cells[1]):
                # Extract the local region for training
                training_cells_region = range_doppler_map[
                    r - guard_cells[0] : r + guard_cells[0] + 1,
                    d - guard_cells[1] : d + guard_cells[1] + 1,
                ]

                # Extract the local region for guard cells
                guard_cells_region = range_doppler_map[
                    r - guard_cells[0] : r + guard_cells[0] + 1,
                    d - guard_cells[1] : d + guard_cells[1] + 1,
                ]

                # Calculate the threshold based on training cells
                threshold = np.mean(training_cells_region) * threshold_factor

                # Check if the value at the cell is greater than the threshold
                if range_doppler_map[r, d] > threshold:
                    filtered_map[r, d] = range_doppler_map[r, d]

        return filtered_map


if __name__ == "__main__":
    pipeline = ProcessingPipeline("newest.npy")
    rangeProfile = pipeline.getRangeProfile()
    rangeDoppler = pipeline.getRangeDoppler(start_frame=0, end_frame=200)
    print(rangeDoppler.shape)

    # mask = pipeline.CFAR(rangeDoppler, threshold_factor=1.1)
    # rangeDoppler = rangeDoppler * mask

    plt.plotRangeProfile(rangeProfile)
    plt.plotRangeDoppler(rangeDoppler)
