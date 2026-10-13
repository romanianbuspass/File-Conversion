import obspy
import numpy as np

def dat_to_mseed(dat_file, mseed_file, sensitivity=1.0, station="ST01"):
    """
    Converts ASCII .dat (Time, Amplitude) back to binary miniSEED.
    Reverses the sensitivity scaling to restore raw integer counts.
    """
    try:
        # Load the ASCII data, skipping the header row
        data = np.loadtxt(dat_file, skiprows=1)
        time_sec = data[:, 0]
        amplitude = data[:, 1]
        
        # Calculate sampling rate from the time column differences
        dt = time_sec[1] - time_sec[0]
        fs = 1.0 / dt
        
        # Reverse the sensitivity scaling and convert back to int32 (miniSEED standard)
        raw_counts = np.round(amplitude * sensitivity).astype(np.int32)
        
        # Build the miniSEED header
        # .dat files lose absolute time and station metadata, so we define them here
        stats = {
            'network': 'XX',
            'station': station,
            'location': '00',
            'channel': 'HHZ',
            'sampling_rate': fs,
            # Assigning a default start time since .dat only holds relative seconds
            'starttime': obspy.UTCDateTime("2026-08-01T00:00:00.000000Z")
        }
        
        # Create Trace and Stream, then export
        trace = obspy.Trace(data=raw_counts, header=stats)
        st = obspy.Stream([trace])
        st.write(mseed_file, format='MSEED')
        
        print(f"Success: {dat_file} converted to {mseed_file} at {fs:.1f} Hz")
        
    except Exception as e:
        print(f"Error converting file: {e}")

if __name__ == "__main__":
    # Example usage:
    # Use the exact same sensitivity used during the initial export to accurately
    # restore the original integer counts.

    input_file = "converted_waveform.dat"
    output_file = "restored_sample.mseed"
    # Replace with your channel's sensitivity in counts per physical unit
    # (from the channel's StationXML response).
    sensitivity = 1.0

    dat_to_mseed(input_file, output_file, sensitivity=sensitivity)
