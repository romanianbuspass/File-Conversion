# File Conversion

Seismic waveform file conversion tooling for GaiaCode OmegaBox digitizer
data: converting between binary miniSEED, ASCII `.dat` (for SeismoSignal
ingestion), and SAC formats, with StationXML metadata injection into SAC
headers.

## Contents

| Path | Description |
|---|---|
| `seed2dat.py` | Convert miniSEED → ASCII `.dat` (Time, Amplitude columns) for SeismoSignal, with optional sensitivity scaling from raw counts to physical units |
| `dat2seed.py` | Convert ASCII `.dat` back to binary miniSEED, reversing the sensitivity scaling to restore raw integer counts |
| `SEED2SAC/GaiaCode Pipeline/` | Headless, cron-safe pipeline: mirrors miniSEED data directly from OmegaBox units over HTTP (wget), converts to SAC with ObsPy, and injects station coordinates / component orientation from StationXML into SAC headers |

## Technology Stack

- **Python 3** with [ObsPy](https://github.com/obspy/obspy) (miniSEED/SAC
  I/O, StationXML parsing) and NumPy
- **PyYAML** — pipeline configuration
- **wget** — mirroring OmegaBox `/data/` trees (pipeline)

## Hardware Dependencies

- **GaiaCode OmegaBox** digitizer units (24-bit ADC) — the headless
  pipeline mirrors continuous data directly from the units' built-in HTTP
  server (`http://<unit-ip>/data/`). The OmegaBox does not serve
  StationXML, so one metadata file per station is kept alongside the
  pipeline.
- `seed2dat.py` / `dat2seed.py` operate on local files and have no
  hardware dependency.

## Setup & Installation

```bash
python3 -m venv venv
./venv/bin/pip install obspy numpy pyyaml
sudo apt install wget        # pipeline only (Debian/Ubuntu)
```

## Usage

### miniSEED → ASCII `.dat` (`seed2dat.py`)

```python
from seed2dat import mseed_to_dat

# sensitivity=1.0 keeps raw counts; use the channel's StationXML
# sensitivity (counts per m/s²) to export physical units
mseed_to_dat("sample.mseed", "converted_waveform.dat", sensitivity=1.0)
```

Output: tab-separated `Time(s)` / `Amplitude` columns with a header row,
relative time starting at 0.0 s.

### ASCII `.dat` → miniSEED (`dat2seed.py`)

```python
from dat2seed import dat_to_mseed

# use the SAME sensitivity used during export to restore original counts
dat_to_mseed("converted_waveform.dat", "restored_sample.mseed",
             sensitivity=1.0, station="ST01")
```

Sampling rate is recovered from the time column; absolute time and
station metadata (lost by the `.dat` format) are supplied as arguments.

### Headless OmegaBox → SAC pipeline

```bash
cd "SEED2SAC/GaiaCode Pipeline"
# edit config.yaml: station list, archive roots, per-unit web_url
../venv/bin/python gaiacode_pipeline.py [--config config.yaml]
```

One-shot per invocation — drive the schedule with cron (see the
pipeline's own [README](SEED2SAC/GaiaCode%20Pipeline/README.md) for
deployment details). Exit code `0` when every file converted, `1` if any
file failed.

## Data Formats & Protocols

- **miniSEED** — input/output waveform format (Steim-compressed records);
  read/written via ObsPy.
- **SAC** (Seismic Analysis Code) — output of the pipeline; one file per
  channel per continuous segment, named
  `NET.STA.LOC.CHAN.D.YYYY.JJJ.HHMMSS.SAC`. Headers populated with
  `STLA/STLO/STEL` (coordinates), `CMPAZ` (azimuth), and
  `CMPINC = dip + 90` (SEED dip → SAC inclination convention).
- **StationXML** (SeisComP schema) — per-station metadata used for SAC
  header injection; example files with placeholder coordinates included.
- **ASCII `.dat`** — two-column `Time(s)`/`Amplitude` text for
  SeismoSignal ingestion.
- **HTTP** — OmegaBox units expose their `/data/` archive tree over plain
  HTTP; the pipeline mirrors it with `wget -m` (timestamping, only
  new/changed files transferred).
