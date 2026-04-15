import pandas as pd
from extractors.mock import MockBIExtractor

def main():
    print("--- Initializing Mock Providers ---")
    pbi_mock = MockBIExtractor(platform="Power BI", seed=101)
    qlik_mock = MockBIExtractor(platform="Qlik", seed=202)

    # 1. Generate Power BI Data
    pbi_workspaces = pbi_mock.get_workspaces(count=3)
    pbi_apps = pbi_mock.get_apps(count=10)
    
    # 2. Generate Qlik Data
    qlik_workspaces = qlik_mock.get_workspaces(count=2)
    qlik_apps = qlik_mock.get_apps(count=5)

    # 3. Combine into DataFrames (Simulating our Bronze -> Silver layer transition)
    all_apps = pbi_apps + qlik_apps
    df_apps = pd.DataFrame(all_apps)
    
    print("\n--- Unified Silver Layer: Apps ---")
    print(df_apps.head(15).to_string())

if __name__ == "__main__":
    main()