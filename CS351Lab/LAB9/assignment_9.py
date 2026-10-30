# Name: Sayan Shit
# Roll No: 2401179

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

def initialize_spark_and_load_data(file_path):
    """
    Initializes a SparkSession and loads the Adult dataset from a raw .data file.
    
    Inputs:
        file_path (str): The path to the adult.data file.
    
    Outputs:
        spark (SparkSession): The active Spark session.
        df (DataFrame): The loaded dataset as a Spark DataFrame with named columns.
        
    Working Logic:
        Creates a Spark application named 'Assignment9', defines a specific 
        schema matching the UCI Adult dataset attributes, and reads the CSV 
        file without a header row.
    """
    # Initialize the SparkSession
    spark = SparkSession.builder \
        .appName("Assignment9") \
        .getOrCreate()
        
    # Define the schema explicitly since adult.data lacks a header row
    schema = StructType([
        StructField("age", IntegerType(), True),
        StructField("workclass", StringType(), True),
        StructField("fnlwgt", IntegerType(), True),
        StructField("education", StringType(), True),
        StructField("education_num", IntegerType(), True),
        StructField("marital_status", StringType(), True),
        StructField("occupation", StringType(), True),
        StructField("relationship", StringType(), True),
        StructField("race", StringType(), True),
        StructField("sex", StringType(), True),
        StructField("capital_gain", IntegerType(), True),
        StructField("capital_loss", IntegerType(), True),
        StructField("hours_per_week", IntegerType(), True),
        StructField("native_country", StringType(), True),
        StructField("income", StringType(), True)
    ])
        
    # Read the dataset into a DataFrame applying the defined schema
    df = spark.read.csv(file_path, header=False, schema=schema)
    
    return spark, df

if __name__ == "__main__":
    # Point this to the extracted adult.data file in your LAB9 folder
    dataset_path = r"E:\IIIT G\SEM_5\CS351Lab\LAB9\adult\adult.data"
    
    # Load the data
    spark_session, adult_df = initialize_spark_and_load_data(dataset_path)
    
    # Display the first few rows to verify successful loading
    print("Dataset loaded successfully. Showing top 5 rows:")
    adult_df.show(5)