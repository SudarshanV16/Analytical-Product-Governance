# 🛡️ Universal BI Governance Hub

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![Architecture](https://img.shields.io/badge/Architecture-Medallion-orange)

A platform-agnostic Business Intelligence (BI) governance, cataloging, and auditing engine. Designed to combat "dashboard sprawl" across enterprise platforms (Power BI, Qlik, Tableau) by providing a single pane of glass for data stewards and business users.

## 📖 The Problem: Dashboard Sprawl
Modern enterprises utilize multiple BI platforms, leading to fragmented metadata. Finding the "certified" dashboard for a specific KPI, auditing user access routes (Direct vs. AD Group), and tracking documentation links becomes a manual, cross-platform nightmare. 

This project solves this by abstracting the extraction of BI metadata and centralizing governance workflows into a unified catalog.

---

## 🏗️ Architecture Decision Records (ADRs)

### ADR 001: The Extensible Provider Pattern
To ensure the engine is platform-agnostic, metadata ingestion uses an Object-Oriented Provider Pattern. 
* A `BaseBIExtractor` abstract base class defines the strict contract (e.g., `get_workspaces()`, `get_apps()`, `get_users()`).
* New BI tools (Power BI, Qlik, Tableau) are integrated simply by subclassing this base class and handling the specific REST API idiosyncrasies. The downstream data pipeline remains entirely untouched.

### ADR 002: Medallion Architecture (Databricks Paradigm)
The data processing pipeline is modeled after the Databricks Medallion Architecture:
* **Bronze (Raw):** Raw JSON arrays extracted from the BI Provider APIs.
* **Silver (Normalized):** Flattened, relational entities (`df_apps`, `df_workspaces`, `df_users`) structured via Pandas (locally) or PySpark (production).
* **Gold (Serving):** Business-level aggregates (e.g., `tbl_bi_catalog`, `tbl_effective_access`).
* **Serving Layer:** In production, this layer is queried via a Databricks Serverless SQL Warehouse. For local development, this is simulated using an embedded **SQLite** database.

### ADR 003: Synthetic Data Generation (Mocking)
To enable zero-friction local development, CI/CD testing, and portfolio demonstrations without requiring live enterprise API credentials, this repository utilizes a `MockBIExtractor`.
* Powered by the Python `Faker` library.
* Generates deterministic, highly relational synthetic metadata.
* Maintains complex foreign key relationships (e.g., mapping a generated User to an AD Group, and that Group to a Workspace) to ensure SQL joins function identically to production.

---

## 🚀 Local Quickstart (Zero Configuration)

You can run this entire enterprise architecture locally in seconds. The mock engine will generate a synthetic Power BI and Qlik environment.

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/universal-bi-governance.git](https://github.com/YOUR_USERNAME/universal-bi-governance.git)
cd universal-bi-governance

---
### 2. Set up the environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize the Medallion Pipeline
```bash
python app/init_db.py
```

### 4. Launch the Governance UI
```bash
streamlit run app/main.py
```

### 5. Launch the Governance UI
``` bash
universal-bi-governance/
├── extractors/            # Data Extraction Layer
│   ├── base.py            # Abstract Base Class contract
│   └── mock.py            # Faker-driven synthetic data provider
├── app/                   # Serving Layer
│   ├── init_db.py         # Local ETL pipeline & SQLite builder
│   └── main.py            # Streamlit interactive UI
├── Dockerfile             # Containerization config
├── requirements.txt       # Python dependencies
└── README.md
```