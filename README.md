FarmCarbon MRV

Agricultural Carbon Monitoring, Reporting & Verification Platform
A data-driven Streamlit application for farm registration, geospatial boundary management, satellite vegetation monitoring, soil organic carbon (SOC) analysis, agricultural practice tracking, MRV review workflows, and report generation.

<p align="center">
  <a href="https://farmcarbon.streamlit.app/">Live Demo</a> ·
  <a href="https://github.com/RishabhGuptaX/FarmCarbon-MRV">GitHub Repository</a>
</p>---

Live application

Try FarmCarbon MRV: https://farmcarbon.streamlit.app/

The hosted application is intended for demonstration and exploration. It starts with clearly identified synthetic sample records so that the core workflows can be explored without connecting a live satellite provider or entering real farm data.

«Demo-data notice: Sample farms, satellite observations, soil measurements, and agricultural interventions are synthetic. They are provided to demonstrate application workflows and must not be interpreted as real-world measurements, verified carbon removals, or issued carbon credits.»

---

Table of contents

- "Overview" (#overview)
- "Project objectives" (#project-objectives)
- "Application modules" (#application-modules)
- "Key capabilities" (#key-capabilities)
- "Architecture" (#architecture)
- "Technology stack" (#technology-stack)
- "Repository structure" (#repository-structure)
- "Data model and storage" (#data-model-and-storage)
- "Soil organic carbon methodology" (#soil-organic-carbon-methodology)
- "Satellite monitoring" (#satellite-monitoring)
- "Run locally" (#run-locally)
- "Configuration" (#configuration)
- "Run the test suite" (#run-the-test-suite)
- "Exports and generated reports" (#exports-and-generated-reports)
- "Deployment" (#deployment)
- "Known limitations" (#known-limitations)
- "Roadmap" (#roadmap)
- "Contributing" (#contributing)
- "Disclaimer" (#disclaimer)

---

Overview

FarmCarbon MRV is a local-first, modular application that demonstrates how farm-level information and monitoring evidence can be organised into an agricultural carbon MRV workflow.

The application brings together several related activities:

1. Register farms and maintain geospatial boundaries.
2. Review vegetation indicators and satellite observation records.
3. Record soil sampling information and calculate fixed-depth SOC stock estimates.
4. Track agricultural interventions and their supporting evidence.
5. Review data completeness and quality warnings.
6. Generate farm-level reports and export selected records.

The project is built with Python and Streamlit. Its current persistence layer uses JSON files and the local filesystem; it does not require a SQL database or a database server.

Project objectives

- Provide a single interface for exploring farm, soil, satellite, and intervention records.
- Keep farm boundary information in GeoJSON-compatible form.
- Separate UI pages from reusable application services and storage code.
- Support a default offline demonstration mode, with an optional Google Earth Engine satellite provider.
- Make data gaps and MRV review status visible rather than silently treating incomplete evidence as verified.
- Produce downloadable outputs that can support review and further analysis.

---

Application modules

The app contains a dashboard and six workflow pages.

Module| Purpose| Main workflow
Overview Dashboard| Summarises the current farm and monitoring dataset.| Review high-level farm, area, soil, practice, and observation metrics.
Farm Registry| Maintains farm records and mapped boundaries.| Add or review farm details, validate Polygon/MultiPolygon GeoJSON boundaries, and view farm locations.
Satellite Monitoring| Presents vegetation-index observations for registered farms.| Explore observation time series, use imported observation data, and review the active satellite provider.
Soil Carbon Analysis| Records soil measurements and calculates SOC stock estimates.| Enter sample details, compare compatible baseline/follow-up measurements, and inspect calculation warnings.
Agricultural Practices| Tracks agricultural interventions and supporting evidence.| Record practice activity and attach supporting files.
MRV Reports & Review| Supports completeness checks and report generation.| Inspect missing information and quality warnings, record reviewer actions, and export farm-level outputs.
Methodology| Explains the calculations and assumptions used by the demonstrator.| Review SOC calculation logic, satellite indicators, and methodological limitations.

---

Key capabilities

Farm registry and geospatial boundaries

- Create and maintain farm records.
- Work with GeoJSON Polygon and MultiPolygon boundary geometries.
- Validate uploaded or supplied geometries before use.
- Calculate farm area geodesically using WGS84-oriented geospatial tooling.
- Display farm locations and available boundaries on an interactive map.

Satellite and vegetation monitoring

- Use an offline synthetic provider by default, so the demo can run without external satellite credentials.
- Import satellite observation records from CSV.
- Optionally connect a Google Earth Engine Sentinel-2 provider.
- Display NDVI, NDMI, and EVI time series for monitoring exploration.
- Show which provider is active and provide a fallback to the synthetic provider if Earth Engine cannot initialise.

Vegetation indices are indicators derived from spectral bands. They are not direct measurements of soil organic carbon and should not be interpreted as SOC results on their own.

Soil carbon analysis

- Capture soil sample information such as SOC concentration, bulk density, sampling depth, and coarse-fragment fraction.
- Calculate fixed-depth SOC stock estimates.
- Compare measurements only when the farm, zone, sampling depths, and measurement method are compatible.
- Flag bulk-density differences and other data-quality concerns.
- Estimate carbon mass and CO2-equivalent values when the required zone-area information is available.

Agricultural practices and evidence

- Maintain a record of agricultural interventions.
- Associate practice records with farm information and supporting evidence files.
- Keep evidence records separate from the practice workflow so that the information can be reviewed later.

MRV review and reporting

- Evaluate record completeness using an MRV checklist.
- Display data-quality warnings and missing-information indicators.
- Capture reviewer actions in the review workflow.
- Generate farm-level PDF reports.
- Export supported records in CSV and GeoJSON formats.

---

Architecture

FarmCarbon MRV uses a layered, service-oriented structure within a single Streamlit application.

flowchart TD
    A[Streamlit UI: app.py and pages/] --> B[Runtime and configuration]
    B --> C[Application services]
    C --> D[Repository layer]
    D --> E[JSON storage]
    C --> F[Satellite provider interface]
    F --> G[Demo satellite provider]
    F --> H[Optional Earth Engine provider]
    C --> I[Report and export services]
    I --> J[PDF, CSV and GeoJSON outputs]
    A --> K[UI components: theme and maps]

Architectural layers

Layer| Location| Responsibility
Presentation| "app.py", "pages/"| Streamlit dashboard, page navigation, forms, charts, and workflow screens.
UI components| "farmcarbon/components/"| Shared visual styling and reusable interface components such as map rendering.
Runtime and configuration| "farmcarbon/runtime.py", "config/settings.py"| Initialise storage, build shared services, load environment configuration, and select the satellite provider.
Application services| "farmcarbon/services/"| Farm, geometry, satellite, soil-carbon, practice, MRV, and reporting operations.
Provider integrations| "farmcarbon/providers/satellite/"| Common satellite-provider interface, synthetic demo provider, and optional Earth Engine provider.
Persistence| "farmcarbon/storage/"| JSON file storage and repository access.
Tests| "tests/"| Unit and workflow tests for geometry, validation, storage, soil carbon, MRV, reports, and application workflows.

Design choices

- No SQL database: records are stored in JSON files through the storage/repository layer.
- Provider abstraction: the satellite service can use the demo provider or the optional Earth Engine provider.
- Reusable services: business logic is kept outside individual Streamlit page files where practical.
- Local-first MVP: the current storage model is designed for a single-user demonstrator, not concurrent production workloads.

---

Technology stack

Area| Technologies
Language| Python
Application UI| Streamlit
Data processing| Pandas, NumPy
Charts| Plotly
Geospatial processing| Shapely, PyProj, GeoJSON
Interactive maps| Folium, streamlit-folium
Reporting| ReportLab
Configuration| python-dotenv
Testing| Pytest
Optional satellite integration| Google Earth Engine API, Sentinel-2 Surface Reflectance Harmonized collection
Deployment| Streamlit Community Cloud

Pinned Python dependencies are listed in ""requirements.txt"" (requirements.txt). Python 3.12 is the recommended deployment/runtime target for the current pinned environment.

---

Repository structure

FarmCarbon-MRV/
│
├── app.py                         # Main dashboard and application entry point
├── config/
│   └── settings.py                # Paths and environment-based settings
│
├── farmcarbon/
│   ├── components/                 # Shared UI, styling, and map components
│   ├── models/                     # Application data models
│   ├── providers/
│   │   └── satellite/
│   │       ├── base.py             # Satellite provider interface
│   │       ├── demo_provider.py    # Synthetic offline provider
│   │       └── earth_engine_provider.py  # Optional Earth Engine provider
│   ├── services/                   # Application/business logic
│   ├── storage/                    # JSON store, repository, initialisation
│   ├── utils/                      # Shared utilities and validation helpers
│   ├── demo_data.py                # Synthetic demonstration records
│   └── runtime.py                  # Shared application runtime construction
│
├── pages/
│   ├── 1_Farm_Registry.py
│   ├── 2_Satellite_Monitoring.py
│   ├── 3_Soil_Carbon_Analysis.py
│   ├── 4_Agricultural_Practices.py
│   ├── 5_MRV_Reports.py
│   └── 6_Methodology.py
│
├── storage/
│   └── uploads/                    # Local evidence uploads (runtime-created/managed)
│
├── data/
│   ├── demo/                       # Demo input/output resources
│   └── exports/                    # Generated exports
│
├── tests/                          # Pytest test suite
├── .streamlit/
│   └── config.toml                 # Streamlit theme and server configuration
├── .env.example                    # Example environment configuration
├── requirements.txt                # Pinned dependencies
├── pytest.ini                      # Pytest configuration
└── README.md

Some runtime directories and JSON files are created automatically on first launch and may not be present in a fresh clone.

---

Data model and storage

The application stores structured records in JSON collections. It does not use SQLite, PostgreSQL, MySQL, SQLAlchemy, or another SQL database.

Collection| What it stores
"farms.json"| Farm profiles, identifiers, location information, and boundary references/data.
"soil_samples.json"| Soil sampling records and measurement values used by SOC analysis.
"satellite_observations.json"| Satellite-derived or imported observation records and index values.
"practices.json"| Agricultural practice and intervention records.
"evidence_files.json"| Metadata for files attached as supporting evidence.
"mrv_reviews.json"| MRV completeness and reviewer-action records.
"audit_events.json"| Recorded application events relevant to the audit trail.

Typical runtime storage layout:

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

The JSON store writes through a temporary file and then replaces the target file. This reduces the chance of leaving a partially written JSON document after an interrupted write, but it does not provide the transaction, concurrency, access-control, or scaling guarantees of a production database.

Back up the "storage/" directory before resetting local demonstration data or changing environments. Evidence uploads are stored on the local filesystem and should be backed up separately when they need to be retained.

---

Soil organic carbon methodology

The current demonstrator estimates SOC stock using a fixed-depth calculation:

SOC stock (Mg C/ha) =
    SOC concentration (g/kg)
    × bulk density (g/cm³)
    × (1 − coarse-fragment fraction)
    × sampling depth (cm)
    × 0.1

Example

For a sample with:

- SOC concentration = "10 g/kg"
- Bulk density = "1.3 g/cm³"
- Coarse-fragment fraction = "0.10"
- Sampling depth = "30 cm"

SOC stock = 10 × 1.3 × (1 − 0.10) × 30 × 0.1
          = 35.1 Mg C/ha

Comparison rules and interpretation

- Baseline/follow-up comparisons are paired only when farm, zone, top depth, bottom depth, and measurement method match.
- Zone area is required to estimate total carbon mass and convert it to a CO2-equivalent quantity.
- Negative stock changes are retained rather than being automatically changed to zero.
- Changes in bulk density are flagged because fixed-depth comparisons can be affected by changes in soil mass.
- Equivalent soil mass adjustment and uncertainty propagation are not currently implemented.

These outputs are calculation estimates based on the recorded inputs and stated assumptions. They are not independently measured or certified carbon-credit quantities.

---

Satellite monitoring

Default mode: synthetic demonstration provider

The application defaults to the "demo" provider. It creates synthetic observation data for demonstration and does not require an Earth Engine account. The dashboard and satellite page should identify that the data is synthetic.

Optional mode: Google Earth Engine

The optional provider uses the "COPERNICUS/S2_SR_HARMONIZED" collection. The implementation uses Sentinel-2 spectral bands to derive vegetation/water-related indicators, including:

- NDVI — Normalized Difference Vegetation Index.
- NDMI — Normalized Difference Moisture Index.
- EVI — Enhanced Vegetation Index.

The provider applies a Scene Classification Layer (SCL) mask to classes "3", "8", "9", "10", and "11" before aggregating per-farm mean index values. Earth Engine must be installed and authenticated, and a Google Cloud project ID must be configured.

If Earth Engine cannot initialise, the runtime is designed to fall back to the synthetic provider and surface a provider notice. A fallback to demo observations should not be confused with receipt of fresh satellite imagery.

---

Run locally

Requirements

- Git
- Python 3.12 recommended
- pip
- Internet access to install Python packages

1. Clone the repository

git clone https://github.com/RishabhGuptaX/FarmCarbon-MRV.git
cd FarmCarbon-MRV

2. Create and activate a virtual environment

Windows PowerShell

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

If PowerShell blocks activation for the current session, run the following and activate again:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

macOS / Linux

python3.12 -m venv .venv
source .venv/bin/activate

3. Install dependencies

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

The repository pins compatible versions of NumPy and PyArrow. Installing the requirements file as provided is recommended instead of upgrading individual binary dependencies independently.

4. Create a local environment file

Windows PowerShell

Copy-Item .env.example .env

macOS / Linux

cp .env.example .env

The default ".env.example" selects the synthetic demo provider. No additional configuration is needed to start the standard local demo.

5. Start the application

streamlit run app.py

Streamlit will print a local URL (typically "http://localhost:8501"). The application initialises required storage folders and JSON collections automatically.

---

Configuration

The application reads environment variables from ".env" when present.

Variable| Default| Description
"FARMCARBON_SATELLITE_PROVIDER"| "demo"| Selects the satellite provider. Use "demo" for synthetic observations or "earth_engine" to request the optional Earth Engine provider.
"EE_PROJECT_ID"| Empty| Google Cloud project ID used by the optional Earth Engine integration.

Enable the optional Earth Engine provider locally

1. Install the optional package:
   
   python -m pip install earthengine-api

2. Edit ".env":
   
   FARMCARBON_SATELLITE_PROVIDER=earth_engine
EE_PROJECT_ID=your-google-cloud-project-id

3. Authenticate with Earth Engine:
   
   earthengine authenticate

4. Confirm that the account has access to Earth Engine and that the configured Cloud project is enabled for the integration.

5. Restart Streamlit.

Keep credentials and private keys out of source control. Do not commit ".env", service-account keys, or Streamlit secrets to GitHub.

---

Run the test suite

Install the project dependencies, activate the virtual environment, and run:

pytest -q

The repository includes tests covering geometry, validators, JSON storage, soil-carbon calculations, MRV logic, report generation, and workflow behaviour.

---

Exports and generated reports

The application supports the following output types where applicable in the relevant workflow:

- PDF: farm-level MRV report generated through the reporting service.
- CSV: tabular exports for supported records and analysis outputs.
- GeoJSON: geospatial farm-boundary export.

Generated files are written to the configured local exports directory ("data/exports/"). Output availability depends on the completeness of the underlying records.

---

Deployment

FarmCarbon MRV is deployed on Streamlit Community Cloud.

- Live application: https://farmcarbon.streamlit.app/
- GitHub repository: https://github.com/RishabhGuptaX/FarmCarbon-MRV
- Application entry point: "app.py"
- Dependency file: "requirements.txt"
- Recommended Python version: 3.12

Deploy your own instance

1. Fork or clone this repository to your GitHub account.
2. Open "Streamlit Community Cloud" (https://share.streamlit.io/).
3. Connect the GitHub repository.
4. Select the branch containing the application code (the default branch is "main").
5. Set the main file path to "app.py".
6. Select Python 3.12 in the advanced settings, where available.
7. Deploy the application.

The default demo does not require secrets because it uses the synthetic satellite provider. The optional Earth Engine integration requires additional dependency and credential configuration; it is not enabled by default.

Hosted-storage consideration

The application uses local JSON files and local file uploads. This is suitable for a demonstrator, but it should not be treated as a durable shared data platform for production use. Do not rely on the hosted app's local filesystem as the sole copy of important farm records or evidence. A production deployment should use managed persistent storage, a database, authentication, role-based access control, and a secure file-storage service.

---

Known limitations

The following limitations are intentional or remain outside the current MVP scope:

- The default satellite provider returns synthetic demonstration observations.
- Live Earth Engine monitoring is optional and requires separate account/project configuration.
- NDVI, NDMI, and EVI are vegetation/moisture indicators, not direct soil-carbon measurements.
- SOC stock uses a fixed-depth method; equivalent soil mass adjustment is not implemented.
- Uncertainty propagation is not implemented in the current SOC calculations.
- Results depend on the quality, representativeness, and completeness of submitted farm and soil data.
- The JSON/local-filesystem storage layer is designed for a single-user local MVP, not concurrent multi-user or distributed production use.
- Production-grade authentication, authorisation, tenant isolation, and managed persistent storage are not included.
- Generated reports support review and demonstration; they are not third-party verification statements or registry submissions.

---

Roadmap

Potential directions for future development include:

- Add persistent managed database and object storage for production deployments.
- Add user authentication, role-based permissions, and organisation/farm-level access controls.
- Extend evidence traceability and reviewer workflows.
- Improve sampling design, depth harmonisation, equivalent-soil-mass analysis, and uncertainty reporting.
- Add robust validation and provenance metadata for imported monitoring data.
- Improve production monitoring, deployment automation, and operational auditability.

These are possible future enhancements, not claims about functionality already delivered.

---

Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make focused changes and add or update tests where relevant.
4. Run the test suite with "pytest -q".
5. Open a pull request describing the change and its impact.

Please avoid committing real farmer personal information, private evidence files, local ".env" files, credentials, or generated runtime data.

---

Disclaimer

FarmCarbon MRV is an independent software demonstrator. It is not an official Varaha product, a carbon registry, a certification system, or a third-party verification service. The application does not guarantee additionality, permanence, ownership, eligibility, issuance, or saleability of carbon credits. All calculations and reports must be independently reviewed and validated against the relevant methodology, data-quality requirements, and applicable verification standards before any real-world use.

---

Author

Rishabh Gupta
GitHub: "@RishabhGuptaX" (https://github.com/RishabhGuptaX)

---

<p align="center">
  <strong>FarmCarbon MRV</strong><br />
  Monitoring • Reporting • Verification
</p>