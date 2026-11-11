# FarmCarbon MRV

**AI-powered agricultural carbon monitoring, reporting and verification demonstrator**

FarmCarbon MRV is a local-first Streamlit MVP for farm registration, GeoJSON boundaries, optional Sentinel-2 monitoring, soil organic carbon calculations, agricultural practice tracking, MRV completeness checks and PDF reporting.

> **Storage change:** This project intentionally uses **no SQL database**. There is no SQLite, PostgreSQL, MySQL, SQLAlchemy, database server, schema migration or table setup. Records are kept in readable JSON files, boundaries in GeoJSON, uploads on the local filesystem, and exports as CSV/PDF.

## Features

- Dashboard with farm, area, practice, observation and soil metrics.
- Farm registration with Polygon/MultiPolygon GeoJSON validation and geodesic area calculation (WGS84).
- Satellite monitoring using a synthetic offline demo provider, CSV imports, and an optional Google Earth Engine Sentinel-2 provider.
- NDVI, NDMI and EVI time series. These are not treated as direct soil-carbon measurements.
- Soil sample entry and fixed-depth SOC stock calculation, baseline/follow-up comparison, bulk-density warnings and CO2e equivalent calculation.
- Agricultural intervention register with local evidence attachments.
- MRV completeness checklist, data-quality warnings and explicit reviewer action.
- Farm-level PDF report and CSV/GeoJSON exports.
- Synthetic demonstration data for two sample farms.

## Run locally

Python 3.10 or newer is recommended.

### 1. Create an environment

**Windows PowerShell**

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start the app

```bash
streamlit run app.py
```

The app creates its local storage folders and JSON files on first launch. No database setup is needed.

## Local storage layout

```text
storage/
├── data/
│   ├── farms.json
│   ├── soil_samples.json
│   ├── satellite_observations.json
│   ├── practices.json
│   ├── evidence_files.json
│   ├── mrv_reviews.json
│   └── audit_events.json
└── uploads/

data/
├── demo/
└── exports/
```

Each JSON file contains an array of records. Writes are made through a temporary file and atomically replaced. This approach is designed for a **single-user local MVP**. It is not intended for concurrent multi-user or distributed production workloads. Back up the `storage/` folder to preserve local work.

## Demo data

Two clearly labelled synthetic farms are seeded when the app starts and no farm records exist. Synthetic satellite observations, soil samples and agricultural interventions are marked as demo records. They are not real Sentinel-2 observations, laboratory results, verified carbon removals or credit quantities.

Use **Reset demonstration data** in the dashboard to reset local records to the seeded examples. This deletes all current local records and files in the uploads folder; export or back up anything you need first.

## Optional Google Earth Engine

The app works without Earth Engine. To enable the optional live provider:

1. Install the optional package: `pip install earthengine-api`.
2. Copy `.env.example` to `.env`.
3. Set `FARMCARBON_SATELLITE_PROVIDER=earth_engine` and `EE_PROJECT_ID=your-google-cloud-project-id`.
4. Authenticate locally using `earthengine authenticate`.
5. Restart Streamlit.

The provider reads `COPERNICUS/S2_SR_HARMONIZED`, uses B4/B8/B3/B11 (and B2 for EVI), applies an SCL mask for classes 3, 8, 9, 10 and 11, and returns per-farm mean indices. If Earth Engine cannot initialise, FarmCarbon MRV falls back to the synthetic provider and displays the reason.

## Soil-carbon method

```text
SOC stock (Mg C/ha) = SOC (g/kg)
                       × bulk density (g/cm³)
                       × (1 - coarse fragment fraction)
                       × sampling depth (cm)
                       × 0.1
```

Example: `10 × 1.3 × (1 - 0.10) × 30 × 0.1 = 35.1 Mg C/ha`.

Comparisons are paired only when farm, zone, top and bottom depths, and measurement method match. A zone area is needed for carbon mass and CO2e calculations. Negative stock changes are retained. Equivalent soil mass adjustment and uncertainty propagation are not implemented; changes in bulk density are flagged. Results are not certified carbon-credit quantities.

## Tests

```bash
pytest -q
```

## Main routes

Streamlit pages are in `pages/`: Farm Registry, Satellite Monitoring, Soil Carbon Analysis, Agricultural Practices, MRV Reports and Methodology. The dashboard is `app.py`.

## Disclaimer

This is an independent demonstrator and not an official Varaha product. It is not a third-party verification statement, carbon-credit certification, registry issuance, or guarantee of additionality, permanence, ownership or carbon-credit eligibility.
