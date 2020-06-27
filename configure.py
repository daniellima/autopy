import os
import logging
import urllib.request
import shutil
import subprocess

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(asctime)s - %(name)s: %(message)s')
logger = logging.getLogger(__name__)

home_path = '/home/daniellima'

logger.info(f'Home is {home_path}')

files_dir_name = 'files'
files_dir_path = home_path + '/' + files_dir_name
logger.info(f"Create '{files_dir_path}' directory...")
if not os.path.exists(files_dir_path):
    os.mkdir(files_dir_path)
    logger.info('> Created')
else:
    logger.info('> Already exists')

configuration_dir_name = 'configuration'
configuration_dir_path = home_path + '/' + configuration_dir_name
logger.info(f"Create '{configuration_dir_path}' directory...")
if not os.path.exists(configuration_dir_path):
    os.mkdir(configuration_dir_path)
    logger.info('> Created')
else:
    logger.info('> Already exists')

installers_dir_name = 'installers'
installers_dir_path = configuration_dir_path + '/' + installers_dir_name
logger.info(f"Create '{installers_dir_path}' directory...")
if not os.path.exists(installers_dir_path):
    os.mkdir(installers_dir_path)
    logger.info('> Created')
else:
    logger.info('> Already exists')

vscode_deb_url = 'https://go.microsoft.com/fwlink/?LinkID=760868'
vscode_deb_name = 'code_1.46.1-1592428892_amd64.deb'
vscode_deb_path = installers_dir_path + '/' + vscode_deb_name
logger.info(f'Download VS Code .deb file from {vscode_deb_url} to {vscode_deb_path}...')
if not os.path.exists(vscode_deb_path): # verify md5sum?
    with urllib.request.urlopen(vscode_deb_url) as response:
        with open(vscode_deb_path, 'wb+') as vscode_deb_file:
            shutil.copyfileobj(response, vscode_deb_file)
    logger.info('> Downloaded sucessfully')
else:
    logger.info('> Already downloaded')

logger.info(f'Install VS Code...')
completed_process = subprocess.run(['sudo', 'apt', 'install', vscode_deb_path], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'> Installed successfully')
else:
    logger.info(f'> An error happened while installing')
    logger.info(f'Return Code: {completed_process.returncode}')
    logger.info(f'Stdout: \'{completed_process.stdout}\'')
    logger.info(f'Stderr: \'{completed_process.stderr}\'')
    exit(1)

python_extension_id = 'ms-python.python'
logger.info(f'Install Python extension on VS Code...')
completed_process = subprocess.run(['code', '--install-extension', python_extension_id], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'> Installed successfully')
else:
    logger.info(f'> An error happened while installing')
    logger.info(f'Return Code: {completed_process.returncode}')
    logger.info(f'Stdout: \'{completed_process.stdout}\'')
    logger.info(f'Stderr: \'{completed_process.stderr}\'')
    exit(1)

logger.info(f'Install Git...')
completed_process = subprocess.run(['sudo', 'apt', 'install', 'git'], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'> Installed successfully')
else:
    logger.info(f'> An error happened while installing')
    logger.info(f'Return Code: {completed_process.returncode}')
    logger.info(f'Stdout: \'{completed_process.stdout}\'')
    logger.info(f'Stderr: \'{completed_process.stderr}\'')
    exit(1)

gitconfig_path = home_path + '/' + '.gitconfig'
gitconfig_content = (
    '# This is Git\'s per-user configuration file.\n'
    '[user]\n'
    '# Please adapt and uncomment the following lines:\n'
    '       name = Daniel Lima\n'
    '       email = daniellima.pessoal@gmail.com\n'
)
logger.info(f'Creating .gitconfig file at {home_path}')
if not os.path.exists(gitconfig_path):
    should_write = True
else:
    with open(gitconfig_path, 'r') as gitconfig_file:
        content = gitconfig_file.read()
        if content != gitconfig_content:
            should_write = True
        else:
            logger.info(f'Already exists and it\'s contents are correct')

if should_write:
    with open(gitconfig_path, 'w') as gitconfig_file:
        gitconfig_file.write(gitconfig_content)
    logger.info(f'File recreated sucessfully')
