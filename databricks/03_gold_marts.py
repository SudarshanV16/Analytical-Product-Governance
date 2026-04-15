"""
Gold Layer: Business-Level Aggregation
Joins the Silver dimensional tables to create the highly optimized serving 
views that power the Streamlit/Serverless SQL Warehouse UI.
"""
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("BI_Governance_Gold").getOrCreate()

def build_gold_catalog_mart():
    # Read normalized Silver tables
    df_apps = spark.table("catalog.bi_gov_silver.dim_apps")
    df_workspaces = spark.table("catalog.bi_gov_silver.dim_workspaces")
    
    # Join into a flat, wide table optimized for BI/Streamlit querying
    df_catalog = df_apps.join(df_workspaces, "workspace_id", "left") \
        .select(
            df_apps.app_id,
            df_apps.platform,
            df_apps.app_name,
            df_workspaces.workspace_name.alias("space_name"),
            df_apps.app_owner_name
        )
        
    df_catalog.write.format("delta") \
              .mode("overwrite") \
              .saveAsTable("catalog.bi_gov_gold.mart_bi_catalog")

# Example execution
# build_gold_catalog_mart()