from process_data import ProcessingPipeline
from plot_data import DataPlotter as plt

# class Demodulater:
#     def __init__(self, modulater):
#         self.modulater = modulater

#     def demodulate(self, data):
#         # 100 for 0, 110 for 1
#         pass

# Demodulate the range profile, extract data from peaks
pipeline = ProcessingPipeline("newest.npy")
rangeProfile = pipeline.getRangeProfile(start_frame=0)

# rangeBinStart = 25
# rangeBinEnd = 40
rangeBinStart = 27
rangeBinEnd = 37

chirp = 50

range_of_interest = rangeProfile[chirp, rangeBinStart:rangeBinEnd]
print(range_of_interest)

# Count the number of values greater than 0.2 in range_of_interest
count = 0
for value in range_of_interest:
    if value > 0.2:
        count += 1

print(count)

if count > 5:
    print("1")
elif count <= 2:
    print("2")
elif count <= 3:
    print("3")
else:
    print("4")

# Plot the range profile
# plt.plotRangeProfile(rangeProfile)

