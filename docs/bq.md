# Google BigQuery

## Creating a new table in BQ UI

* Go to the BQ console
* Create and share new database as needed
* Create a new table
* For source data, select "Create empty table"
* Open the generated .bq.json file
* Copy the "fields" [] array to clipboard 
* Under Schema, select "Edit as text"
* Paste the "fields" array []
* Click "Create Table" button

## Using BQ command tool

### Load Data
To load a CSV file:
> ```"bq load --project_id <project> --format csv <database>.<table> <datafile>```

Example:
> ```bq load --project_id mtna-opendata --format csv us_census.us_census_2010_h <datafile>```
> ```bq load --project_id mtna-opendata --format csv --skip_leading_rows 1 us_anes.us_anes_1948_ts NES1948.dta.csv```


### References

* [Google Cloud SDK](https://cloud.google.com/sdk/docs/)
* [bq Command-Line Tool](https://cloud.google.com/bigquery/bq-command-line-tool)



