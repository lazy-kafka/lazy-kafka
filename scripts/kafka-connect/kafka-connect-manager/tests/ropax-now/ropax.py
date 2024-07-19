import awswrangler as wr

wr.config.s3_endpoint_url = "http://127.0.0.1:4566"

if __name__ == "__main__":
    #pip install "pandas[aws,pyarrow,fastparquet]"
    # pip install awswrangler

    # Read from S3
    #storage_options = {"client_kwargs": {"endpoint_url": "http://127.0.0.1:4566"}}
    #s3path = "s3://my-bucket/topics/foo/year=2024/month=04/day=15/hour=12/foo+0+0000000002.snappy.parquet"
#    df = pd.read_parquet(, storage_options=storage_options)
    s3path = "s3://my-bucket/topics/foo/"
    df = wr.s3.read_parquet(path=s3path, dataset=True)
    #partition_filter=lambda x: x["year"] == "2020"
    print(df)
