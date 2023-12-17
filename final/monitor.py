import os
import shutil
import time
from parse_bin_data import parse_ADC


class ParseBinData:
    """Detects any changes in the binData folder and process the new bin files."""
    def __init__(self, binData_directory):
        self.src_directory = binData_directory
        self.binData_folders = os.listdir(self.src_directory)

        self.binData_count = 0
    
    def get_newest_bin_folder(self):
        """Get the newest bin folder.

        Returns:
            str: The newest bin folder.
        """
        bin_folders = os.listdir(self.src_directory)
        bin_folders.sort()
        return bin_folders[-1]
    
    def process_data(self, new_bin_folder):
        """Process the new bin files.

        Args:
            new_bin_folder (str): The new bin folder.
        """
        print("Process bin folder: {}".format(new_bin_folder))
        outputName = "./npy_data/data_" + new_bin_folder + ".npy"
        bin_folder = os.path.join(self.src_directory, new_bin_folder)
        parse_ADC(bin_folder, outputName)
        shutil.copyfile(outputName, "newest.npy")
        print("New npy file: {}".format(outputName))

    def run(self):
        """Generate a new npy file from the newest bin folder, named as newest.npy"""
        new_bin_folder = self.get_newest_bin_folder()
        self.process_data(new_bin_folder)

    def scan_new_binData(self):
        """Scan the binData folder and process the new bin files."""
        new_bin_folder = self.get_newest_bin_folder()
        bin_data_files = os.listdir(os.path.join(self.src_directory, new_bin_folder))
        self.binData_count = len(bin_data_files)
        while len(bin_data_files) == self.binData_count:
            time.sleep(1)
            new_bin_folder = self.get_newest_bin_folder()
            bin_data_files = os.listdir(os.path.join(self.src_directory, new_bin_folder))

        self.binData_count = len(bin_data_files)
        self.process_data(new_bin_folder)
        print("New bin data: {}".format(bin_data_files[-1]))

if __name__ == "__main__":
    realtimeParseBinData = ParseBinData("./Industrial_Visualizer/binData/")
    realtimeParseBinData.run()
