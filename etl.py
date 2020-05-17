import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
        """
    Description: create extract songs table and artist table data for given
	spark session, input path and output path
    :param spark: a spark session instance
    :param input_data: input file path
    :param output_data: output file path
    """
    # get filepath to song data file
    song_data = song_data = input_data + "song_data/*/*/*/*"
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df['song_id', 'title', 'artist_id','artist_name', \
	'year', 'duration']
    songs_table = songs_table.drop_duplicates(subset=['song_id'])
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy('year', 'artist_id')\
	.parquet(os.path.join(output_data, 'songs.parquet'), 'overwrite')

    # extract columns to create artists table
    artists_table = df['artist_id', 'artist_name', 'artist_location',\
	'artist_latitude', 'artist_longitude']
    artists_table = artists_table.drop_duplicates(subset=['artist_id'])
    
    # write artists table to parquet files
    artists_table.write.parquet(os.path.join(output_data, 'artists.parquet'), 'overwrite')


def process_log_data(spark, input_data, output_data):
    """Processing log data in given spark session, input path and the output path
        :param spark: a spark session instance
        :param input_data: input file path
        :param output_data: output file path
    """  
    # get filepath to log data file
    log_data =os.path.join(input_data,"log_data/*/*/*.json")

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df= df.where(col("page")=="NextSong")

    # extract columns for users table    
    users_table = df['userId', 'firstName', 'lastName', 'gender', 'level','ts']
    users_table = users_table.orderBy("ts",ascending=False).\
    dropDuplicates(subset=["userId"]).drop('ts')
    
    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, 'users.parquet'), 'overwrite')

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x : datetime.utcfromtimestamp(int(x)/1000), TimestampType())
    df = df.withColumn("start_time", get_timestamp("ts"))
    
    # extract columns to create time table
    time_table = df.withColumn("hour",hour("start_time"))\
                    .withColumn("day",dayofmonth("start_time"))\
                    .withColumn("week",weekofyear("start_time"))\
                    .withColumn("month",month("start_time"))\
                    .withColumn("year",year("start_time"))\
                    .withColumn("weekday",dayofweek("start_time"))\
                    .select("ts","start_time","hour", "day", "week", \
                            "month", "year", "weekday").drop_duplicates()

    
    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(os.path.join(output_data, "time_table/"), \
                             mode='overwrite', partitionBy=["year","month"])

    # read in song data to use for songplays table
    song_df = spark.read.parquet(output_data+"songs.parquet")

    # extract columns from joined song and log datasets to create songplays table 
    df = df.join(song_df, (song_df.title == df.song) & (song_df.artist_name == df.artist))
    df = df.withColumn('songplay_id', monotonically_increasing_id()) 
    songplays_table = df['songplay_id','start_time', 'userId', 'level', \
                         'song_id', 'artist_id', 'sessionId', 'location', 'userAgent']
    

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.parquet(os.path.join(output_data, 'songplays.parquet'), \
                                  'overwrite', partitionBy=["year","month"])


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3://udacity-spark-project/result/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
