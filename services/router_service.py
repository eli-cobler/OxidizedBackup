import os,logging,shutil,sys
from distutils.dir_util import copy_tree
from typing import List, Optional

import data.db_session as db_session
from data.router import Router

def get_router_count() -> int:
    session = db_session.create_session()
    session.close()
    return session.query(Router).count()

def get_backup_complete_count() -> int:
    session = db_session.create_session()
    backup_status_query = session.query(Router.backup_status)
    complete_count = 0
    for status in backup_status_query:
        if status == ('Backup Complete',):
            complete_count += 1

    session.close()

    return complete_count

def get_config_complete_count() -> int:
    session = db_session.create_session()
    config_status_query = session.query(Router.config_status)
    complete_count = 0
    for status in config_status_query:
        if status == ('Config Export Complete',):
            complete_count += 1

    session.close()

    return complete_count

def get_backup_failed_count() -> int:
    session = db_session.create_session()
    backup_status_query = session.query(Router.backup_status)
    failed_count = 0
    for status in backup_status_query:
        if status != ('Backup Complete',):
            failed_count += 1

    session.close()

    return failed_count

def get_config_failed_count() -> int:
    session = db_session.create_session()
    config_status_query = session.query(Router.config_status)
    failed_count = 0
    for status in config_status_query:
        if status != ('Config Export Complete',):
            failed_count += 1

    session.close()

    return failed_count

def get_unknown_status_count() -> int:
    session = db_session.create_session()
    backup_status_query = session.query(Router.backup_status)
    config_status_query = session.query(Router.config_status)
    unknown_count = 0
    for backup_status in backup_status_query:
        if backup_status == ('Unknown',):
            unknown_count += 1
    for config_status in config_status_query:
        if config_status == ('Unknown',):
            unknown_count += 1

    session.close()

    return unknown_count

def get_router_list()-> List[Router]:
    session = db_session.create_session()
    routers = session.query(Router).\
        order_by(Router.router_name.asc()).\
        all()

    session.close()

    return routers

def get_router_details(router_name: str)-> Optional[Router]:
    if not router_name:
        return None

    router_name = router_name.strip()

    session = db_session.create_session()

    router = session.query(Router) \
        .filter(Router.router_name == router_name) \
        .first()

    session.close()

    return router

def add_router(router_name,router_ip,username,password):

    path = os.getcwd()
    directory_exists = os.path.isdir(path + '/backups/{}'.format(router_name))
    logging.info("Checking if directory for %s already exists." % router_name)

    if directory_exists:
        logging.info("The direcotry did already exist.")
        return True
    else:
        logging.info("The direcotry didn't exist.")
        # writes new router to database file
        logging.info("Attempting to write new router to database.")
        r = Router()

        r.router_name = router_name
        r.router_ip = router_ip
        r.username = username
        r.password = password

        session = db_session.create_session()
        session.add(r)
        session.commit()
        logging.info("Database entry added successfully.")

        logging.info("Attempting to create backup folder for %s" % router_name)
        try:
            os.mkdir(path + '/backups/{}'.format(router_name))
            f = open("router_info/{}.txt".format(router_name), "w+")
            f.write('')
            f.close()
        except:
            logging.error("There was a problem creating backup folder. See the error below.")
            logging.error(sys.exc_info()[1])
        return False

def remove_router(router_name):
    path = os.getcwd()

    logging.info("Attempting to remove %s from the database." % router_name)
    r = Router()
    session = db_session.create_session()
    router = session.query(Router) \
        .filter(Router.router_name == router_name) \
        .first()
    session.delete(router)
    session.commit()
    logging.info("Router successfully removed from database.")

    logging.info("Attempting to remove the backups for %s." % router)
    try:
        # Gathering Backups path and removing it
        backup_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../backups/{}'.format(router_name)))
        shutil.rmtree(backup_path)
        logging.info("Router backups successfully removed.")

        # Gathering Router info.txt path and removing it
        router_info_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../router_info/{}.txt'.format(router_name)))
        os.remove(router_info_path)
        logging.info("Router info successfully removed.")
    except:
        logging.error("There was a problem removing the router's backups. See the error below.")
        logging.error(sys.exc_info()[1])

def update_router(selected_router,router_name, router_ip, username, password):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../backups/'))

    if router_name != selected_router:
        logging.info("Changing name of router from %s to %s." % (selected_router, router_name))
        logging.info("Creating new backup directory for %s" % router_name)

        # creating new backup directory
        try:
            os.mkdir(path + router_name)
            logging.info("New backup directory created.")
        except:
            logging.error("There was a problem creating new backup direcotry. See the error below.")
            logging.error(sys.exc_info()[1])

        logging.info("Moving the backups from old direcotry.")

        # moving backup files to new backup directory
        try:
            fromDirectory = path + '/{}'.format(selected_router)
            toDirectory = path + '/{}'.format(router_name)
            copy_tree(fromDirectory, toDirectory)
            logging.info("Files moved successfully.")
        except:
            logging.error("There was a problem moving the backups. See the error below.")
            logging.error(sys.exc_info()[1])

        logging.info("Removing old backups directory.")

        # removing old backup directory
        try:
            shutil.rmtree(path + '/{}'.format(selected_router))
            logging.info("Directory removed successfully.")
        except:
            logging.error("There was a problem removing the directory. See the error below.")
            logging.error(sys.exc_info()[1])

        # # renaming info text file
        # try:
        #     old_info_file =  path + '/{}.txt'.format(selected_router)
        #     new_info_file = path + '/{}.txt'.format(router_name)
        #     os.rename(old_info_file,new_info_file)
        # except:
        #     logging.error("There was a problem renaming the info file. See the error below.")
        #     logging.error(sys.exc_info()[1])

    # updating database values in sql database
    logging.info("Updating database values for %s." % selected_router)
    session = db_session.create_session()
    r = session.query(Router).filter(Router.router_name == selected_router).one()
    r.router_name = router_name
    r.router_ip = router_ip
    r.username = username
    r.password = password
    session.commit()
    logging.info("Database values updated successfully.")