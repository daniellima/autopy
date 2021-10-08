import os
import logging
import urllib.request
import shutil
import subprocess

def execute_command_in_bash(command_text):
    completed_process = subprocess.run(['bash', '-c', command_text], capture_output=True, text=True)
    if completed_process.returncode != 0:
        logger.info(f'> An error happened while executing command on bash: {command_text}')
        logger.info(f'Return Code: {completed_process.returncode}')
        logger.info(f'Stdout: \'{completed_process.stdout}\'')
        logger.info(f'Stderr: \'{completed_process.stderr}\'')
        exit(1)
    
    return completed_process

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

logger.info(f'Install latest version of VS Code...')
completed_process = subprocess.run(['dpkg', '-s', 'code'], capture_output=True, text=True)
if completed_process.returncode != 0:
    vscode_deb_url = 'https://go.microsoft.com/fwlink/?LinkID=760868'
    vscode_deb_name = 'code_1.46.1-1592428892_amd64.deb'
    vscode_deb_path = installers_dir_path + '/' + vscode_deb_name
    logger.info(f'  Download VS Code .deb file from \'{vscode_deb_url} to {vscode_deb_path}\'...')
    if not os.path.exists(vscode_deb_path): # verify md5sum?
        with urllib.request.urlopen(vscode_deb_url) as response:
            with open(vscode_deb_path, 'wb+') as vscode_deb_file:
                shutil.copyfileobj(response, vscode_deb_file)
        logger.info('  > Downloaded sucessfully')
    else:
        logger.info('  > Already downloaded')

    logger.info(f'  Install VS Code...')
    completed_process = subprocess.run(['sudo', 'apt', 'install', '-y', vscode_deb_path], capture_output=True, text=True)
    if completed_process.returncode == 0:
        logger.info(f'  > Installed successfully')
    else:
        logger.info(f'  > An error happened while installing')
        logger.info(f'  Return Code: {completed_process.returncode}')
        logger.info(f'  Stdout: \'{completed_process.stdout}\'')
        logger.info(f'  Stderr: \'{completed_process.stderr}\'')
        exit(1)

logger.info(f'  Ensure VS Code is in latest version...')
completed_process = subprocess.run(['sudo', 'apt', 'install', '-y', 'code'], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'  > Updated successfully')
else:
    logger.info(f'  > An error happened while updating')
    logger.info(f'  Return Code: {completed_process.returncode}')
    logger.info(f'  Stdout: \'{completed_process.stdout}\'')
    logger.info(f'  Stderr: \'{completed_process.stderr}\'')
    exit(1)
logger.info(f'> VS Code is in the latest version.')

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

docker_extension_id = 'ms-azuretools.vscode-docker'
logger.info(f'Install Docker extension on VS Code...')
completed_process = subprocess.run(['code', '--install-extension', docker_extension_id], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'> Installed successfully')
else:
    logger.info(f'> An error happened while installing')
    logger.info(f'Return Code: {completed_process.returncode}')
    logger.info(f'Stdout: \'{completed_process.stdout}\'')
    logger.info(f'Stderr: \'{completed_process.stderr}\'')
    exit(1)

# Instruction from https://docs.docker.com/engine/install/ubuntu/
logger.info(f'Setup Docker repositories...')
execute_command_in_bash('sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release')

docker_keyring_path = '/usr/share/keyrings/docker-archive-keyring.gpg';
if not os.path.exists(docker_keyring_path):
    execute_command_in_bash(f'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o {docker_keyring_path}')

docker_repo_configuration_file_path = '/etc/apt/sources.list.d/docker.list'
if not os.path.exists(docker_repo_configuration_file_path):
    execute_command_in_bash(f'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee {docker_repo_configuration_file_path} > /dev/null')
logger.info(f'> Docker repositories have been defined')

logger.info(f'Install Docker...')
execute_command_in_bash('sudo apt-get install -y docker-ce docker-ce-cli containerd.io')
logger.info(f'> Installed successfully...')

logger.info(f'Configure Docker to be run by non-root user')
if execute_command_in_bash('getent group docker').returncode != 0:
    execute_command_in_bash('sudo groupadd docker')
execute_command_in_bash('sudo usermod -aG docker $USER')
logger.info(f'> Configuration applied successfully')

logger.info(f'Install Docker-Compose')
execute_command_in_bash('sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose')
execute_command_in_bash('sudo chmod +x /usr/local/bin/docker-compose')
logger.info(f'> Installed successfully...')

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
should_recreate = False
logger.info(f'Creating .gitconfig file at \'{home_path}\'')
if not os.path.exists(gitconfig_path):
    should_recreate = True
else:
    with open(gitconfig_path, 'r') as gitconfig_file:
        content = gitconfig_file.read()
        if content != gitconfig_content:
            should_recreate = True
        else:
            logger.info(f'> Already exists and it\'s contents are correct')

if should_recreate:
    with open(gitconfig_path, 'w') as gitconfig_file:
        gitconfig_file.write(gitconfig_content)
    logger.info(f'> File recreated sucessfully')

code_dir_name = 'code'
code_dir_path = files_dir_path + '/' + code_dir_name
logger.info(f"Create '{code_dir_path}' directory...")
if not os.path.exists(code_dir_path):
    os.mkdir(code_dir_path)
    logger.info('> Created')
else:
    logger.info('> Already exists')

autopy_repository_url = 'git@github.com:daniellima/autopy.git'
autopy_repository_path = code_dir_path + '/' + 'autopy'
logger.info(f"Clone autopy repository on \'{autopy_repository_path}\'...")
if not os.path.exists(autopy_repository_path):
    completed_process = subprocess.run(['git', 'clone', autopy_repository_url, autopy_repository_path], capture_output=True, text=True)
    if completed_process.returncode == 0:
        logger.info(f'> Cloned successfully')
    else:
        logger.info(f'> An error happened while cloning')
        logger.info(f'Return Code: {completed_process.returncode}')
        logger.info(f'Stdout: \'{completed_process.stdout}\'')
        logger.info(f'Stderr: \'{completed_process.stderr}\'')
        exit(1)
else:
    logger.info('> Already exists')


awesome_links_generator_repository_url = 'git@github.com:daniellima/awesome-links-generator.git'
awesome_links_generator_repository_path = code_dir_path + '/' + 'awesome-links-generator'
logger.info(f"Clone awesome-links-generator repository on \'{awesome_links_generator_repository_path}\'...")
if not os.path.exists(awesome_links_generator_repository_path):
    completed_process = subprocess.run(['git', 'clone', awesome_links_generator_repository_url, awesome_links_generator_repository_path], capture_output=True, text=True)
    if completed_process.returncode == 0:
        logger.info(f'> Cloned successfully')
    else:
        logger.info(f'> An error happened while cloning')
        logger.info(f'Return Code: {completed_process.returncode}')
        logger.info(f'Stdout: \'{completed_process.stdout}\'')
        logger.info(f'Stderr: \'{completed_process.stderr}\'')
        exit(1)
else:
    logger.info('> Already exists')

desafio_loja_integrada_repository_url = 'git@github.com:daniellima/desafio-lojaintegrada.git'
desafio_loja_integrada_repository_path = code_dir_path + '/' + 'desafio-lojaintegrada'
logger.info(f"Clone desafio-lojaintegrada repository on \'{desafio_loja_integrada_repository_path}\'...")
if not os.path.exists(desafio_loja_integrada_repository_path):
    completed_process = subprocess.run(['git', 'clone', desafio_loja_integrada_repository_url, desafio_loja_integrada_repository_path], capture_output=True, text=True)
    if completed_process.returncode == 0:
        logger.info(f'> Cloned successfully')
    else:
        logger.info(f'> An error happened while cloning')
        logger.info(f'Return Code: {completed_process.returncode}')
        logger.info(f'Stdout: \'{completed_process.stdout}\'')
        logger.info(f'Stderr: \'{completed_process.stderr}\'')
        exit(1)
else:
    logger.info('> Already exists')

logger.info('Install net-tools')
execute_command_in_bash('sudo apt install -y net-tools')
logger.info('> Installed successfully')

logger.info('Install Beekeeper Studio (Database Client)')
execute_command_in_bash('sudo snap install beekeeper-studio')
logger.info('> Installed successfully')
