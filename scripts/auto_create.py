import os
import json
import logging


def create_project_structure(api_key_file, expected_api_key):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(api_key_file, 'r') as file:
        api_key_data = json.load(file)
        api_key = api_key_data['key']

    if api_key == expected_api_key:
        root_folder = 'mtafsiribot'
        os.makedirs(root_folder, exist_ok=True)
        logging.info('[itsKios-09]: running creating ${root_folder}.....')

        subfolders = ['model', 'static', 'template']
        for folder in subfolders:
            os.makedirs(os.path.join(root_folder, folder), exist_ok=True)
        logging.info('[itsKios-09]: running creating ${subfolders}.....')

        # Create the app.py file
        with open(os.path.join(root_folder, 'app.py'), 'w') as file:
            file.write('# Your app.py code goes here')
        logging.info('[itsKios-09]: running creating app.py.....')

        return
    else:
        print('Error: API key does not match the expected key')


