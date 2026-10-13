import obspy
import numpy as np
import sys

def mseed_to_dat(mseed_file, dat_file, sensitivity=1.0):
    """
    Converts binary miniSEED to ASCII .dat for SeismoSignal ingestion.
    Applies optional sensitivity scaling to convert raw counts to physical units.
    """
    try:
        # Load the miniSEED stream
        st = obspy.read(mseed_file)
        
        # Merge to interpolate any micro-gaps and prevent step-functions
        st.merge(method=1, fill_value='interpolate')
        trace = st[0]
        
        # Extract stats
        fs = trace.stats.sampling_rate
        npts = trace.stats.npts
        
        # Convert counts to physical units (e.g., m/s^2) using sensitivity
        data_physical = trace.data.astype(np.float64) / sensitivity
        
        # Generate relative time array starting at 0.0s
        t = np.arange(0, npts / fs, 1 / fs)
        
        # Stack into two columns and export
        output = np.column_stack((t, data_physical))
        np.savetxt(dat_file, output, fmt='%.6f', delimiter='\t', 
                   header='Time(s)\tAmplitude', comments='')
                   
        print(f"Success: {mseed_file} converted to {dat_file}")
        
    except Exception as e:
        print(f"Error converting file: {e}")

if __name__ == "__main__":
    # Example usage:
    # Set sensitivity to 1.0 to keep raw counts, or use your channel's
    # exact XML sensitivity (counts per m/s^2) to export in physical units.

    input_file = "sample.mseed"
    output_file = "converted_waveform.dat"
    # Replace with your channel's sensitivity in counts per physical unit
    # (from the channel's StationXML response).
    sensitivity = 1.0

    mseed_to_dat(input_file, output_file, sensitivity=sensitivity)
