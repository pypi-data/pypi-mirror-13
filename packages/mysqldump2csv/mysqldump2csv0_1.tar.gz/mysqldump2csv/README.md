# mysqldump2csv
Since Amazon RDS not allowed to use `SELECT INTO OUTFILE` to generate CSV, this script should do the trick.

# Usage example:

```bash
mysqldump -h host -u username -ppasswrd database table
--skip-extended-insert --no-create-db --no-create-info --skip-disable-keys > table.csv.gz
&& python mysqldump2csv.py -df table.csv.gz -t table -s 500000
```


** ./mysqldump2csv.py -h for more information.
