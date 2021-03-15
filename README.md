# Grafana Backup and Restore 

This script can:

* Donwload `datasources`, `folders` and `dashboards` to json files from Grafana.
* Upload `datasources`, `folders` and `dashboards` from json files to Grafana.

## Requirements
- python3
- requests

## Usage

Required environment variables:
* `GRAFANA_URL` - Grafana address (Example: https://grafana.example.com)
* `GRAFANA_TOKEN` - Admin API token generated in Grafana

Optional environment variables:
* `DIR_DATASOURCES` - Grafana Datasources directory. Will be created if not exist. (Default is `./datasources`)
* `DIR_FOLDERS` - Grafana Folders directory. Will be created if not exist. (Default is `./folders`)
* `DIR_DASHBOARDS` - Grafana Dashboards directory. Will be created if not exist. (Default is `./dashboards`)
* LOG_LEVEL - Logging level. (Defauls is INFO)

Running script:
```
main.py <action>
```
Actions:
```
  --help                show this help message and exit
  --get-datasources     download datasources as json files
  --get-folders         download folders as json files
  --get-dashboards      download dashasboards json files
  --upload-datasources  upload datasources from json files
  --upload-folders      upload folders from json files
  --upload-dashboards   upload dashboards from json files
```

**NOTE:**  Folders upload must be executed before uploading dashboards! When uploading dashboards, script will make a request to Grafana instance to get folders IDs.