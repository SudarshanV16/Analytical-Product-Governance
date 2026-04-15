import sqlite3
import pandas as pd
import os
import sys

# Add parent directory to path so we can import extractors
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extractors.mock import MockBIExtractor

DB_PATH = "app/local_governance.db"

def build_local_database():
    print("🚀 Initializing Local SQLite Database (Databricks Mock)...")
    
    # 1. Generate Mock Data
    pbi_mock = MockBIExtractor(platform="Power BI", seed=101)
    qlik_mock = MockBIExtractor(platform="Qlik", seed=202)

    apps = pbi_mock.get_apps(count=15) + qlik_mock.get_apps(count=15)
    workspaces = pbi_mock._workspaces + qlik_mock._workspaces
    
    df_apps = pd.DataFrame(apps)
    df_workspaces = pd.DataFrame(workspaces)

    # 2. Join to create the Gold Layer Catalog View
    df_catalog = pd.merge(df_apps, df_workspaces, on=["workspace_id", "platform"], how="left")
    
    # Rename columns to match your existing Streamlit logic
    df_catalog = df_catalog.rename(columns={
        "workspace_name": "space_name",
        "owner_name": "app_owner_name"
    })

    # 3. Connect to SQLite and write tables
    conn = sqlite3.connect(DB_PATH)
    
    print("📦 Writing Gold Catalog Table...")
    df_catalog.to_sql("tbl_bi_catalog", conn, if_exists="replace", index=False)

    print("🛠️ Creating Governance & State Tables...")
    cursor = conn.cursor()
    
    # Governance Inputs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_governance_inputs (
        app_id TEXT PRIMARY KEY,
        approved_status TEXT,
        governance_comments TEXT,
        documentation_link TEXT,
        kpi_definitions_link TEXT,
        work_instructions_link TEXT,
        last_updated DATETIME
    )
    """)
    
    # User Favorites Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_user_favorites (
        user_email TEXT,
        app_id TEXT,
        added_at DATETIME
    )
    """)

    # User iFrames Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_user_iframes (
        user_email TEXT,
        iframe_code TEXT,
        grid_width TEXT,
        height_px INTEGER,
        added_at DATETIME
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Local database ready at:", DB_PATH)

if __name__ == "__main__":
    build_local_database()