# 🛡️ Universal BI Governance Hub

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![Architecture](https://img.shields.io/badge/Architecture-Medallion-orange)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED.svg)

A platform-agnostic Business Intelligence (BI) governance, cataloging, and auditing engine. Designed to combat "dashboard sprawl" across enterprise platforms (Power BI, Qlik, Tableau) by providing a single pane of glass for data stewards and business users.

---

## 📖 The Problem: Dashboard Sprawl
Modern enterprises utilize multiple BI platforms, leading to fragmented metadata. Finding the "certified" dashboard for a specific KPI, auditing user access routes (Direct vs. AD Group), and tracking documentation links becomes a manual, cross-platform nightmare. 

This project solves this by abstracting the extraction of BI metadata and centralizing governance workflows into a unified catalog.

---

## 🏗️ Architecture Decision Records (ADRs)

### ADR 001: The Extensible Provider Pattern
To ensure the engine is platform-agnostic, metadata ingestion uses an Object-Oriented Provider Pattern. 
* A `BaseBIExtractor` abstract base class defines the strict contract (e.g., `get_workspaces()`, `get_apps()`, `get_users()`).
* New BI tools (Power BI, Qlik, Tableau) are integrated simply by subclassing this base class and handling the specific REST API idiosyncrasies. 

### ADR 002: Medallion Architecture (Databricks Paradigm)
The data processing pipeline is modeled after the Databricks Medallion Architecture:
* **Bronze (Raw):** Raw JSON arrays extracted from the BI Provider APIs.
* **Silver (Normalized):** Flattened, relational entities (`df_apps`, `df_workspaces`) structured via Pandas (locally) or PySpark (production).
* **Gold (Serving):** Business-level aggregates (e.g., `tbl_bi_catalog`). In local development, this is simulated using an embedded **SQLite** database.

### ADR 003: Synthetic Data Generation (Mocking)
To enable zero-friction local development and portfolio demonstrations without requiring live enterprise API credentials, this repository utilizes a `MockBIExtractor` powered by the `Faker` library. It maintains complex foreign key relationships to ensure SQL joins function identically to production.

---

## 🚀 Local Quickstart (Zero Configuration)

You can run this entire enterprise architecture locally in seconds. The mock engine will automatically generate a synthetic Power BI and Qlik environment for you.

### Option A: Running with Docker (Recommended)
No local Python installation is required.

# 1. Build the image
```bash
docker build -t bi-gov-hub .
```

# 2. Run the container
```bash
docker run -p 8501:8501 bi-gov-hub
```