# Passive Communication between Radar and Corner Reflector

### What's inside?

* `demodulate.py`: processes the range profile
* `main.py`: real-time processing and visulation of binData files
* `monitor.py`: monitors the binData folder and files, process if necessary
* `parse_bin_data.py`: parses binData files and convert to raw ADC input
* `plot_data.py`: plot range profile and range doppler
* `process_data.py`: converts raw ADC data to range profile
* `utils.py`: wraps the radar config file

### How to run the code

Only read one at a time, e.g. only run industrial visualizer for one corner reflector type, and stops the visualizer.

With the industrial visualizer running and generating new `binData` files, run the `main.py`, this is mainly for visualizing range profiles.

Or, first run the industrial visualizer, then run `monitor.py` by invoking `if __name__ == "__main__":`, then run `demodulate.py` to run demodulate the range profile.