from monitor import ParseBinData
from process_data import ProcessingPipeline
from plot_data import DataPlotter as plt


def main():
    """Real-time visulization of the range profile
    
    Run the radar app, then run this script.
    When the new binData file is generated, the range profile will be plotted.
    Close the plot window to visualize the next range profile.
    """
    realtimeParseBinData = ParseBinData("./Industrial_Visualizer/binData/")

    while True:
        realtimeParseBinData.scan_new_binData()

        pipeline = ProcessingPipeline("newest.npy")

        start_frame = -500
        if -1*start_frame > len(pipeline.data):
            start_frame = -len(pipeline.data)

        rangeProfile = pipeline.getRangeProfile(start_frame=start_frame)
        plt.plotRangeProfile(rangeProfile, extent_x=[len(pipeline.data)+start_frame, len(pipeline.data)])

if __name__ == "__main__":
    main()