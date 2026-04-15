"""
Silver Layer: Normalization & Cleansing
Reads the raw JSON from Bronze, flattens the arrays, cleanses the data, 
and enforces schema structures for Apps and Workspaces.
"""
from pyspark.sql.functions import col
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("BI_Governance_Silver").getOrCreate()

def build_silver_apps_table():
    df_bronze = spark.table("catalog.bi_gov_bronze.raw_api_data")
    
    # Flatten and cast data types
    df_silver_apps = df_bronze.select(
        col("app_id").cast("string").alias("app_id"),
        col("platform").cast("string").alias("platform"),
        col("app_name").cast("string").alias("app_name"),
        col("workspace_id").cast("string").alias("workspace_id"),
        col("owner_name").cast("string").alias("app_owner_name"),
        col("created_at").cast("timestamp").alias("created_at")
    ).dropDuplicates(["app_id"]) # Ensure idempotency 
    
    # In a production environment, this would be a Delta MERGE (Upsert)
    df_silver_apps.write.format("delta") \
                  .mode("overwrite") \
                  .saveAsTable("catalog.bi_gov_silver.dim_apps")

# Example execution
# build_silver_apps_table()