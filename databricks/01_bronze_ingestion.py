"""
Bronze Layer: Raw Ingestion
Simulates reading the raw JSON payloads from our Mock Extractors (or live APIs) 
landed in Azure Data Lake Storage (ADLS Gen2) and saving them as raw Delta tables.
"""
from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("BI_Governance_Bronze").getOrCreate()

def ingest_api_payloads_to_bronze(source_path: str, target_table: str):
    print(f"Reading raw JSON from ADLS path: {source_path}")
    df_raw = spark.read.json(source_path)
    
    # Append auditing metadata
    df_bronze = df_raw.withColumn("ingestion_timestamp", current_timestamp()) \
                      .withColumn("source_system", lit("BI_API_Extract"))
    
    # Write to Bronze Delta Table
    df_bronze.write.format("delta") \
             .mode("append") \
             .option("mergeSchema", "true") \
             .saveAsTable(target_table)
    
    print(f"Successfully ingested data into Bronze: {target_table}")

# Example execution
# ingest_api_payloads_to_bronze("abfss://raw@datalake.dfs.core.windows.net/bi_extracts/", "catalog.bi_gov_bronze.raw_api_data")