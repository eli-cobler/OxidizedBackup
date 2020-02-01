#
#  removeBackupFiles.py
#  MikrotikBakcup
#
#  Created by Eli Cobler on 06/13/19.
#  Copyright © 2018 Eli Cobler. All rights reserved.
#
#  This project allows you generate and store backup and config
#  files from Mikrotik Routers.
#
#  This file removes all backup files from the router keeping them from filling up on backups.

import database, subprocess, logging, sys

# log setup
logging.basicConfig(filename='logs/removeBackupFiles.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filemode='w',
                    level=logging.DEBUG)

def run():
    print("Gathering Routers...")
    logging.info("Gathering Routers...")
    ignore_list = ['Broadway Liquor',
                    'Spectrum Voice',
                    'CASA',
                    'Value Med Midwest City',
                    'Valu Med Harrah',
                    'Value Med FTG',
                    'GPSS Hobart',
                    '.DS_Store',
                    'SPARK Datacenter',
                   'GPSS-CNH - EOMC - Poteau']
    router_list = database.get()
    routers = []
    for item in router_list:
        data = item.split(':')
        data[0] = {'router_name': data[0], 'router_ip': data[1], 'username': data[2], 'password': data[3].replace('\n', '')}
        routers.append(data[0])
    
    print("Routers Gathered.")
    logging.info("Routers Gathered.")

    for item in routers:
        print(f"Starting Removal for {item['router_name']}...")
        logging.info("Starting Removal for %s...", item['router_name'])
        if item['router_name'] in ignore_list:
            print("Removal skipped.")
            logging.info("Removal skipped.")
        else:
            try:
                remove_backup = subprocess.run('ssh {}@{} /file remove [find type="backup"]'.format(item['username'], 
                                                                                    item['router_ip']),
                                                                                    shell=True,
                                                                                    universal_newlines=True, 
                                                                                    stdout=subprocess.PIPE, 
                                                                                    stderr=subprocess.PIPE)
                if remove_backup.stdout != '':
                    logging.info(remove_backup.stdout)
                    print(f"stdout: {remove_backup.stdout}")

                if remove_backup.stderr != '':
                    logging.warning(remove_backup.stderr)
                    print(f"stderr: {remove_backup.stderr}")
            except:
                logging.error(sys.exc_info()[1])
                print(f"Exception: {sys.exc_info()[1]}")

            print(f"Removal for {['router_name']} completed.")
            logging.info("Removal for %s completed.", item['router_name'])

if __name__ == "__main__":
    run()