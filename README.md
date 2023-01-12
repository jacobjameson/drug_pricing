## How-to

### If you need to add data:

(1) add row(s) to "data/new data/new data.xlsx"
(2) open terminal on computer
(3) run `bash add_data.sh`
  - this will add the additional rows to "data/raw data/raw data.xlsx"
  - clear "data/new data/new data.xlsx" to an empty excel file
  - if there is no data in "data/new data/new data.xlsx", you will be alerted that the data has not been added yet
(4) run `bash clean_data.sh`
(5) new cleaned data, summarized by drug, will appear in "data/clean data/clean data.xlsx" 

