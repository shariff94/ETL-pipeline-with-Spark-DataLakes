# Apache Spark and Data Lake for Sparkify

## Summary of project

Startup called Sparkify wants to analyze the data they've been collecting on songs and user activity on their new music streaming app.Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

We will be building an ETL pipeline that extracts their data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow the analytics team to continue finding insights in what songs their users are listening to.

A Spark ETL Pipeline was created, which reads the data stored inside S3 buckets.

## How to run the python scripts

To start the ETL pipeline, you have to run a python script `etl.py`:

To fill tables via ETL:
```bash
python etl.py
```

## Files in the repository

* **[etl.py](etl.py)**: Python script to extract the needed information from Song and Log uses Spark, performs data normalization and parquet file writing


## Schema

* **Fact Table**: songplays_table
* **Dimension Tables**: users_table, songs_table, artists_table and time_table.

## Dataset used

The data is queried from s3 buckets hosten at AWS

* **Song data**: ```s3://udacity-dend/song_data```
* **Log data**: ```s3://udacity-dend/log_data```