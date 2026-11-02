# Name: Sayan Shit
# Roll No: 2401179
# Course: CS351 - IT Workshop II (Cloud Computing)
# Assignment 9: Apache Spark Data Processing & Machine Learning

import os
import sys
import warnings
import contextlib

# Suppress Python library warnings (such as pandas/pyspark version notices)
warnings.filterwarnings("ignore")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator


@contextlib.contextmanager
def suppress_jvm_stderr():
    """
    Context manager to suppress low-level JVM startup warnings on Windows
    (such as winutils.exe missing, incubator vector module, native Hadoop library).
    """
    try:
        stderr_fd = sys.stderr.fileno()
        saved_stderr_fd = os.dup(stderr_fd)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, stderr_fd)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(saved_stderr_fd, stderr_fd)
            os.close(saved_stderr_fd)
    except Exception:
        yield


def initialize_spark_session(app_name="Assignment9_AdultAnalysis"):
    """
    Initializes and configures an Apache Spark session for local execution.
    
    Inputs:
        app_name (str): The name of the Spark application.
        
    Outputs:
        spark (SparkSession): The configured SparkSession instance.
        
    Working Logic:
        Builds a SparkSession with master set to 'local[*]' to utilize all available
        local CPU cores. Sets log level to 'ERROR' and disables the web UI to eliminate
        verbose startup warnings and port binding conflicts on Windows.
    """
    with suppress_jvm_stderr():
        spark = SparkSession.builder \
            .appName(app_name) \
            .master("local[*]") \
            .config("spark.driver.host", "127.0.0.1") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.ui.enabled", "false") \
            .config("spark.ui.showConsoleProgress", "false") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        
    return spark


def load_and_preprocess_adult_dataset(spark, file_path):
    """
    Loads the UCI Adult dataset into a Spark DataFrame with schema and whitespace trimming.
    
    Inputs:
        spark (SparkSession): Active Spark session.
        file_path (str): Path to the adult.data file.
        
    Outputs:
        df (DataFrame): Cleaned Spark DataFrame with trimmed string values.
        
    Working Logic:
        1. Explicitly defines the 15-column schema corresponding to the UCI Adult dataset.
        2. Reads the CSV data with whitespace trimming enabled.
        3. Iterates over all string columns and applies trim() to remove any residual whitespace.
    """
    # Define explicit schema matching UCI Adult dataset specifications
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
    
    # Load dataset with whitespace trimming enabled
    df = spark.read.csv(
        file_path,
        header=False,
        schema=schema,
        ignoreLeadingWhiteSpace=True,
        ignoreTrailingWhiteSpace=True
    )
    
    # Ensure all string columns are clean and trimmed
    for col_name, col_type in df.dtypes:
        if col_type == "string":
            df = df.withColumn(col_name, F.trim(F.col(col_name)))
            
    return df


def perform_clustering_on_attributes(df, k_clusters=3):
    """
    Performs K-Means clustering on at least 3 attributes (age, workclass, education, hours_per_week).
    
    Inputs:
        df (DataFrame): Preprocessed Adult dataset DataFrame.
        k_clusters (int): Number of clusters to form (default: 3).
        
    Outputs:
        clustered_df (DataFrame): DataFrame augmented with a 'prediction' cluster column.
        kmeans_model (KMeansModel): The trained K-Means model.
        silhouette (float): Silhouette score measuring clustering quality.
        
    Working Logic:
        1. Encodes categorical variables (workclass, education) into numeric indices using StringIndexer.
        2. Combines numeric and indexed attributes ('age', 'workclass_idx', 'education_idx', 'hours_per_week')
           into a feature vector using VectorAssembler.
        3. Scales the assembled features using StandardScaler to give equal weight to attributes.
        4. Trains a KMeans model with k=3 and computes cluster assignments.
        5. Evaluates cluster separation using ClusteringEvaluator (Silhouette score with Euclidean distance).
    """
    print("\n" + "=" * 80)
    print("TASK 1: CLUSTERING ON AT LEAST 3 ATTRIBUTES (age, workclass, education, hours_per_week)")
    print("=" * 80)
    
    # Filter out missing records denoted by '?' in key clustering attributes
    clean_df = df.filter(
        (F.col("workclass") != "?") & 
        (F.col("education") != "?") & 
        F.col("age").isNotNull()
    )
    
    # Step 1: String Indexing for categorical attributes
    indexer_workclass = StringIndexer(inputCol="workclass", outputCol="workclass_idx", handleInvalid="keep")
    indexer_education = StringIndexer(inputCol="education", outputCol="education_idx", handleInvalid="keep")
    
    indexed_df = indexer_workclass.fit(clean_df).transform(clean_df)
    indexed_df = indexer_education.fit(indexed_df).transform(indexed_df)
    
    # Step 2: Assemble feature columns into a vector (age, workclass_idx, education_idx, hours_per_week)
    feature_cols = ["age", "workclass_idx", "education_idx", "hours_per_week"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_raw")
    assembled_df = assembler.transform(indexed_df)
    
    # Step 3: Feature Scaling using StandardScaler
    scaler = StandardScaler(inputCol="features_raw", outputCol="features", withMean=True, withStd=True)
    scaler_model = scaler.fit(assembled_df)
    scaled_df = scaler_model.transform(assembled_df)
    
    # Step 4: Fit K-Means Clustering Model
    kmeans = KMeans(featuresCol="features", predictionCol="prediction", k=k_clusters, seed=42)
    kmeans_model = kmeans.fit(scaled_df)
    
    # Step 5: Make cluster predictions
    clustered_df = kmeans_model.transform(scaled_df)
    
    # Step 6: Evaluate clustering using Silhouette score
    evaluator = ClusteringEvaluator(featuresCol="features", predictionCol="prediction", metricName="silhouette")
    silhouette = evaluator.evaluate(clustered_df)
    
    print(f"[*] K-Means Model Trained Successfully with k = {k_clusters}")
    print(f"[*] Silhouette with squared Euclidean distance: {silhouette:.4f}")
    
    print("\n[*] Cluster Centers (Standardized Space):")
    for i, center in enumerate(kmeans_model.clusterCenters()):
        print(f"    Cluster {i}: {center}")
        
    print("\n[*] Cluster Size Distribution:")
    clustered_df.groupBy("prediction").count().orderBy("prediction").show()
    
    print("[*] Sample Clustered Records (Showing age, workclass, education, hours_per_week, prediction):")
    clustered_df.select("age", "workclass", "education", "hours_per_week", "prediction").show(10, truncate=False)
    
    return clustered_df, kmeans_model, silhouette


def find_top_country_except_usa(df):
    """
    Finds the native country with the highest number of adults, excluding the USA.
    
    Inputs:
        df (DataFrame): Adult dataset DataFrame.
        
    Outputs:
        top_country (str): The name of the country with the most adults outside the USA.
        adult_count (int): The number of adults from that country.
        
    Working Logic:
        1. Filters out 'United-States' (and missing '?' entries) from native_country.
        2. Groups by native_country and counts adults.
        3. Orders counts in descending order to identify the maximum.
        4. Extracts the first record via an action (.first()).
    """
    print("\n" + "=" * 80)
    print("TASK 2(i): COUNTRY WITH HIGHEST NUMBER OF ADULTS (EXCEPT USA)")
    print("=" * 80)
    
    # Filter out United-States and unknown '?'
    country_df = df.filter(
        (F.col("native_country") != "United-States") & 
        (F.col("native_country") != "?")
    )
    
    # Group by country and calculate counts
    country_counts = country_df.groupBy("native_country") \
        .agg(F.count("*").alias("adult_count")) \
        .orderBy(F.col("adult_count").desc())
    
    print("[*] Top 5 Non-USA Countries by Adult Count:")
    country_counts.show(5, truncate=False)
    
    top_row = country_counts.first()
    top_country = top_row["native_country"]
    adult_count = top_row["adult_count"]
    
    print(f"RESULT 2(i): The country with the highest number of adults (excluding USA) is '{top_country}' with {adult_count} adults.")
    return top_country, adult_count


def find_tech_support_with_at_least_masters(df):
    """
    Finds the number of people who have at least a Master's degree and work in 'Tech-support'.
    
    Inputs:
        df (DataFrame): Adult dataset DataFrame.
        
    Outputs:
        count_at_least_masters (int): Count of individuals meeting the criteria.
        
    Working Logic:
        1. In the UCI Adult dataset:
           - education_num = 14 corresponds to 'Masters'
           - education_num = 15 corresponds to 'Prof-school'
           - education_num = 16 corresponds to 'Doctorate'
           Therefore, 'at least a Master\'s' is represented by education_num >= 14
           (or education IN ('Masters', 'Prof-school', 'Doctorate')).
        2. Filters for occupation == 'Tech-support' AND education_num >= 14.
        3. Executes .count() action and also displays the breakdown by degree.
    """
    print("\n" + "=" * 80)
    print("TASK 2(ii): NUMBER OF PEOPLE WITH AT LEAST A MASTER'S WORKING IN 'Tech-support'")
    print("=" * 80)
    
    # Filter where occupation is Tech-support and education is at least Master's (education_num >= 14)
    tech_masters_df = df.filter(
        (F.col("occupation") == "Tech-support") & 
        (F.col("education_num") >= 14)
    )
    
    count_at_least_masters = tech_masters_df.count()
    
    print(f"[*] Total count with at least Master's (education_num >= 14): {count_at_least_masters}")
    print("\n[*] Breakdown by specific education level in Tech-support:")
    tech_masters_df.groupBy("education", "education_num") \
        .agg(F.count("*").alias("count")) \
        .orderBy(F.col("education_num").desc()) \
        .show(truncate=False)
        
    # Also show count strictly for education == 'Masters'
    exact_masters_count = df.filter(
        (F.col("occupation") == "Tech-support") & 
        (F.col("education") == "Masters")
    ).count()
    print(f"[*] Additional Context:")
    print(f"    - Exactly Masters degree: {exact_masters_count}")
    print(f"    - Masters + Prof-school + Doctorate (education_num >= 14): {count_at_least_masters}")
    
    print(f"RESULT 2(ii): Number of people with at least a Master's in Tech-support = {count_at_least_masters}")
    return count_at_least_masters


def find_unmarried_males_in_local_govt(df):
    """
    Finds the number of unmarried males who work in 'Local_govt' (Local-gov).
    
    Inputs:
        df (DataFrame): Adult dataset DataFrame.
        
    Outputs:
        unmarried_count (int): Count of unmarried males working in Local-gov.
        
    Working Logic:
        1. In the Adult dataset, the workclass entry for local government is labeled 'Local-gov'.
           We check for both 'Local-gov' and 'Local_govt' to cover naming variations.
        2. Filters for sex == 'Male'.
        3. Addresses the definition of 'unmarried':
           - Interpretation A (via 'relationship' column): relationship == 'Unmarried'
           - Interpretation B (via 'marital_status' column): marital_status == 'Never-married'
           - Interpretation C (all non-married): marital_status NOT LIKE 'Married%'
        4. Calculates and prints counts for both standard interpretations for complete clarity.
    """
    print("\n" + "=" * 80)
    print("TASK 2(iii): NUMBER OF UNMARRIED MALES WHO WORK IN 'Local_govt'")
    print("=" * 80)
    
    # Base filter: Male working in Local Government (Local-gov / Local_govt)
    local_govt_males_df = df.filter(
        (F.col("sex") == "Male") & 
        (F.col("workclass").isin("Local-gov", "Local_govt"))
    )
    
    # Interpretation A: relationship == 'Unmarried'
    rel_unmarried_df = local_govt_males_df.filter(F.col("relationship") == "Unmarried")
    count_rel_unmarried = rel_unmarried_df.count()
    
    # Interpretation B: marital_status == 'Never-married'
    mar_never_married_df = local_govt_males_df.filter(F.col("marital_status") == "Never-married")
    count_mar_never_married = mar_never_married_df.count()
    
    # Interpretation C: all non-currently married (Never-married, Divorced, Separated, Widowed)
    all_unmarried_df = local_govt_males_df.filter(~F.col("marital_status").startswith("Married"))
    count_all_unmarried = all_unmarried_df.count()
    
    print("[*] Detailed Breakdown of Marital Statuses for Males in Local Government:")
    local_govt_males_df.groupBy("marital_status", "relationship") \
        .agg(F.count("*").alias("count")) \
        .orderBy(F.col("count").desc()) \
        .show(truncate=False)
        
    print(f"[*] Counts under standard interpretations:")
    print(f"    - Based on relationship == 'Unmarried': {count_rel_unmarried}")
    print(f"    - Based on marital_status == 'Never-married': {count_mar_never_married}")
    print(f"    - Based on all non-married marital statuses: {count_all_unmarried}")
    
    print(f"\nRESULT 2(iii):")
    print(f"    - If defining by relationship == 'Unmarried': {count_rel_unmarried}")
    print(f"    - If defining by marital_status == 'Never-married': {count_mar_never_married}")
    
    return count_rel_unmarried, count_mar_never_married


def main():
    """
    Main driver function that executes all parts of Assignment 9.
    """
    print("=" * 80)
    print("CS351 - IT Workshop II (Cloud Computing) | Lab Assignment 9")
    print("Student Name: Sayan Shit | Roll No: 2401179")
    print("=" * 80)
    
    # Locate dataset
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "adult", "adult.data")
    
    if not os.path.exists(dataset_path):
        # Fallback to absolute path if script is run from a different working directory
        dataset_path = r"E:\IIIT G\SEM_5\CS351Lab\LAB9\adult\adult.data"
        
    print(f"[*] Dataset Path: {dataset_path}")
    
    # Initialize Spark
    spark = initialize_spark_session()
    print("[*] Apache Spark session initialized successfully.")
    
    try:
        # Load and preprocess dataset
        adult_df = load_and_preprocess_adult_dataset(spark, dataset_path)
        print(f"[*] Dataset loaded successfully. Total records: {adult_df.count()}")
        
        # Display schema and preview
        print("\n[*] Dataset Schema:")
        adult_df.printSchema()
        
        print("[*] Preview of first 5 rows:")
        adult_df.show(5)
        
        # Task 1: Clustering
        perform_clustering_on_attributes(adult_df, k_clusters=3)
        
        # Task 2(i): Highest adults country except USA
        find_top_country_except_usa(adult_df)
        
        # Task 2(ii): Tech-support with at least Master's
        find_tech_support_with_at_least_masters(adult_df)
        
        # Task 2(iii): Unmarried males in Local_govt
        find_unmarried_males_in_local_govt(adult_df)
        
        print("\n" + "=" * 80)
        print("ALL ASSIGNMENT 9 TASKS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    finally:
        # Gracefully stop the SparkSession
        spark.stop()
        print("[*] Spark session stopped.")


if __name__ == "__main__":
    main()
