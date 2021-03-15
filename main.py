import os
import json
import logging
import argparse
import urllib3
import requests

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")
REQUEST_HEADERS = {'Authorization': 'Bearer {}'.format(GRAFANA_TOKEN), 'Content-Type': 'application/json', 'Accept': 'application/json'}
DIR_DATASOURCES = os.getenv("DIR_DATASOURCES", "./datasources")
DIR_FOLDERS = os.getenv("DIR_FOLDERS", "./folders")
DIR_DASHBOARDS = os.getenv("DIR_DASHBOARDS", "./dashboards")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s] %(message)s',
    level=LOG_LEVEL,
    )

def get_datasources():
    """ Get Grafana Datasources """
    response = requests.get('{}/api/datasources'.format(GRAFANA_URL), headers=REQUEST_HEADERS, verify=False)
    if response.status_code != 200:
        logging.error('{} {}'.format(response.status_code, response.text))
    else:
        datasources = json.loads(response.text)
        # Create datasources directory
        if not os.path.exists(DIR_DATASOURCES):
            os.makedirs(DIR_DATASOURCES)

        for ds in datasources:
            # Remove unneccessary keys from datasource json
            ds.pop('id')
            ds.pop('typeLogoUrl')

            # Write modified datasource json to file
            filename = '{}/{}.json'.format(DIR_DATASOURCES, ds['name'])
            with open(filename, "w") as file:
                file.write(json.dumps(ds, indent=4))
            logging.info("Datasource {} downloaded".format(ds['name']))
        logging.info("Datasources download done")

def get_folders():
    """ Get Grafana Folders """
    response = requests.get('{}/api/folders'.format(GRAFANA_URL), headers=REQUEST_HEADERS, verify=False)
    if response.status_code != 200:
        logging.error('{} {}'.format(response.status_code, response.text))
    else:
        folders = json.loads(response.text)
        # Create folders directory
        if not os.path.exists(DIR_FOLDERS):
            os.makedirs(DIR_FOLDERS)

        for folder in folders:
            # Remove all keys except 'uid' and 'title' from folder json
            output = {key: folder[key] for key in ['uid', 'title']}

            # Replace unwanted symbols with underscore
            folder_name = folder['title'].replace(' ', '_').replace(':', '')

            # Write modified folder json to file
            filename = '{}/{}.json'.format(DIR_FOLDERS, folder_name)
            with open(filename, "w") as file:
                file.write(json.dumps(output, indent=4))
            logging.info("Folder {} downloaded".format(folder_name))
        logging.info("Folders download done")

def get_dashboards():
    """ Get Grafana Dashboards """
    response = requests.get('{}/api/search/?type=dash-db'.format(GRAFANA_URL), headers=REQUEST_HEADERS, verify=False)
    if response.status_code != 200:
        logging.error('{} {}'.format(response.status_code, response.text))
    else:
        dashboards = json.loads(response.text)
        # Create dashboards directory
        if not os.path.exists(DIR_DASHBOARDS):
            os.makedirs(DIR_DASHBOARDS)

        # Generate dashboard's uid list
        dashboards_uid_list = [dash['uid'] for dash in dashboards]

        # Get dashboards by uid
        for uid in dashboards_uid_list:
            response = requests.get('{}/api/dashboards/uid/{}'.format(GRAFANA_URL, uid), headers=REQUEST_HEADERS, verify=False)
            dashboard = json.loads(response.text)

            # Replace unwanted symbols with underscore
            dashboard_name = dashboard['dashboard']['title'].replace(' ', '_').replace(':', '')

            # Remove 'id' from 'dashboard' section from dashboard json
            dashboard['dashboard'].pop('id')

            # Write modified dashboard json to file
            filename = '{}/{}.json'.format(DIR_DASHBOARDS, dashboard_name)
            with open(filename, "w") as file:
                file.write(json.dumps(dashboard, indent=4))
            logging.info("Dashboard {} downloaded".format(dashboard_name))
        logging.info("Dashboards download done")

def upload_datasources():
    """ Upload Grafana Datasources """
    # Interactive warning
    choice = input('Datasources will be uploaded to {} Continue? [y/n]: '.format(GRAFANA_URL))
    if choice != 'y':
        exit()

    # Get files list if datasources directory
    for datasource_file in os.listdir(DIR_DATASOURCES):
        filename = '{}/{}'.format(DIR_DATASOURCES, datasource_file)
        # Upload datasources json
        with open(filename, "r") as file:
            datasource_json = json.loads(file.read())
            response = requests.post('{}/api/datasources'.format(GRAFANA_URL), json=datasource_json, headers=REQUEST_HEADERS, verify=False)
            if response.status_code != 200:
                logging.warning('{}: {} {}'.format(datasource_file, response.status_code, response.text))
            else:
                logging.info("Datasource {} uploaded".format(datasource_file))

def upload_folders():
    """ Upload Grafana Folders """
    # Interactive warning
    choice = input('Folders will be uploaded to {} Continue? [y/n]: '.format(GRAFANA_URL))
    if choice != 'y':
        exit()

    # Get files list from folders directory
    for folder_file in os.listdir(DIR_FOLDERS):
        filename = '{}/{}'.format(DIR_FOLDERS, folder_file)
        # Upload folders json
        with open(filename, "r") as file:
            folder_json = json.loads(file.read())
            response = requests.post('{}/api/folders'.format(GRAFANA_URL), json=folder_json, headers=REQUEST_HEADERS, verify=False)
            if response.status_code != 200:
                logging.warning('{}: {} {}'.format(folder_file, response.status_code, response.text))
            else:
                logging.info("Folder {} uploaded".format(folder_file))

def upload_dashboards():
    """ Upload Grafana Dashboards """
    # Interactive warning
    choice = input('Dashboards will be uploaded to {} Continue? [y/n]: '.format(GRAFANA_URL))
    if choice != 'y':
        exit()

    # Get existed folders
    response = requests.get('{}/api/folders'.format(GRAFANA_URL), headers=REQUEST_HEADERS, verify=False)
    if response.status_code != 200:
        logging.error('{} {}'.format(response.status_code, response.text))
    else:
        folders = json.loads(response.text)

        # Get folders id and create dict
        folders_ids = {}
        for folder in folders:
            response = requests.get('{}/api/folders/{}'.format(GRAFANA_URL, folder['uid']), headers=REQUEST_HEADERS, verify=False)
            # Get folder id
            folder_id = json.loads(response.text)['id']
            # Update dict
            folders_ids[folder['title']] = folder_id

        # Get files list from dashboards directory
        for dash_file in os.listdir(DIR_DASHBOARDS):
            filename = '{}/{}'.format(DIR_DASHBOARDS, dash_file)

            with open(filename, "r") as file:
                dash_json = json.loads(file.read())
                # Get dashboard's folder name
                folder_name = dash_json['meta']['folderTitle']
                # Update folderId key to match actual folder id (not needed for root General folder)
                if folder_name != 'General':
                    dash_json['folderId'] = folders_ids[folder_name]
                # Upload dashboard json
                response = requests.post('{}/api/dashboards/db'.format(GRAFANA_URL), json=dash_json, headers=REQUEST_HEADERS, verify=False)
                if response.status_code != 200:
                    logging.warning('{}: {} {}'.format(dash_file, response.status_code, response.text))
                else:
                    logging.info("Dashboard {} uploaded".format(dash_file))

if __name__ == "__main__":

    if not GRAFANA_URL:
        logging.error('GRAFANA_URL is not set')
        exit()
    if not GRAFANA_TOKEN:
        logging.error('GRAFANA_TOKEN is not set')
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('--get-datasources', help='download datasources as json files', action='store_const', const=True)
    parser.add_argument('--get-folders', help='download folders as json files', action='store_const', const=True)
    parser.add_argument('--get-dashboards', help='download dashasboards json files', action='store_const', const=True)
    parser.add_argument('--upload-datasources', help='upload datasources from json files', action='store_const', const=True)
    parser.add_argument('--upload-folders', help='upload folders from json files', action='store_const', const=True)
    parser.add_argument('--upload-dashboards', help='upload dashboards from json files', action='store_const', const=True)
    args = parser.parse_args()

    if args.get_datasources:
        get_datasources()
    elif args.get_folders:
        get_folders()
    elif args.get_dashboards:
        get_dashboards()
    elif args.upload_datasources:
        upload_datasources()
    elif args.upload_folders:
        upload_folders()
    elif args.upload_dashboards:
        upload_dashboards()
    else:
        parser.print_help()
