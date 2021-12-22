import os
import logging
import urllib.request
import shutil
import subprocess
from pathlib import Path

def execute_command_in_bash(command_text):
    # logger.debug(f'Executing command {command_text}')
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

home_path = str(Path.home())

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
    completed_process = subprocess.run(['sudo', 'apt-get', 'install', '-y', vscode_deb_path], capture_output=True, text=True)
    if completed_process.returncode == 0:
        logger.info(f'  > Installed successfully')
    else:
        logger.info(f'  > An error happened while installing')
        logger.info(f'  Return Code: {completed_process.returncode}')
        logger.info(f'  Stdout: \'{completed_process.stdout}\'')
        logger.info(f'  Stderr: \'{completed_process.stderr}\'')
        exit(1)

logger.info(f'  Ensure VS Code is in latest version...')
completed_process = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'code'], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'  > Updated successfully')
else:
    logger.info(f'  > An error happened while updating')
    logger.info(f'  Return Code: {completed_process.returncode}')
    logger.info(f'  Stdout: \'{completed_process.stdout}\'')
    logger.info(f'  Stderr: \'{completed_process.stderr}\'')
    exit(1)
logger.info(f'> VS Code is in the latest version.')

# VS Code extension ids can be found on the 'Identifier field'
# of the extension page, at the bottom right corner

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

terraform_extension_id = 'hashicorp.terraform'
logger.info(f'Install Terraform extension on VS Code...')
completed_process = subprocess.run(['code', '--install-extension', terraform_extension_id], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'> Installed successfully')
else:
    logger.info(f'> An error happened while installing')
    logger.info(f'Return Code: {completed_process.returncode}')
    logger.info(f'Stdout: \'{completed_process.stdout}\'')
    logger.info(f'Stderr: \'{completed_process.stderr}\'')
    exit(1)

prisma_extension_id = 'prisma.prisma'
logger.info(f'Install Prisma extension on VS Code...')
completed_process = subprocess.run(['code', '--install-extension', prisma_extension_id], capture_output=True, text=True)
if completed_process.returncode == 0:
    logger.info(f'> Installed successfully')
else:
    logger.info(f'> An error happened while installing')
    logger.info(f'Return Code: {completed_process.returncode}')
    logger.info(f'Stdout: \'{completed_process.stdout}\'')
    logger.info(f'Stderr: \'{completed_process.stderr}\'')
    exit(1)

logger.info('Adding custom configuration to VS Code')
execute_command_in_bash('cp vscode/keybindings.json ~/.config/Code/User/keybindings.json')
execute_command_in_bash('cp vscode/settings.json ~/.config/Code/User/settings.json')
logger.info('> Custom configuration set')

# Instruction from https://docs.docker.com/engine/install/ubuntu/
logger.info(f'Setup Docker repositories...')
execute_command_in_bash('sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release')

docker_keyring_path = '/usr/share/keyrings/docker-archive-keyring.gpg';
if not os.path.exists(docker_keyring_path):
    execute_command_in_bash(f'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o {docker_keyring_path}')

docker_repo_configuration_file_path = '/etc/apt/sources.list.d/docker.list'
if not os.path.exists(docker_repo_configuration_file_path):
    execute_command_in_bash(f'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee {docker_repo_configuration_file_path} > /dev/null')
    execute_command_in_bash('sudo apt-get update')
logger.info(f'> Docker repositories have been defined')

logger.info(f'Install Docker...')
execute_command_in_bash('sudo apt-get install -y docker-ce docker-ce-cli containerd.io')
logger.info(f'> Installed successfully...')

logger.info(f'Configure Docker to be run by non-root user')
execute_command_in_bash('sudo usermod -aG docker $USER')
logger.info(f'> Configuration applied successfully')

logger.info(f'Install Docker-Compose')
docker_compose_bin_path = '/usr/local/bin/docker-compose'
if not os.path.exists(docker_repo_configuration_file_path):
    execute_command_in_bash(f'sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o {docker_repo_configuration_file_path}')    
    logger.info('  > Downloaded sucessfully')
else:
    logger.info('  > Download already done')
execute_command_in_bash(f'sudo chmod +x {docker_repo_configuration_file_path}')
logger.info(f'> Installed successfully...')

logger.info(f'Install Git...')
completed_process = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'git'], capture_output=True, text=True)
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
execute_command_in_bash('sudo apt-get install -y net-tools')
logger.info('> Installed successfully')

logger.info('Install htop')
execute_command_in_bash('sudo apt-get install -y htop')
logger.info('> Installed successfully')

logger.info('Install Beekeeper Studio (Database Client)')
execute_command_in_bash('sudo snap install beekeeper-studio')
logger.info('> Installed successfully')

logger.info('Install Postman')
execute_command_in_bash('sudo snap install postman')
logger.info('> Installed successfully')

logger.info('Disable Xfce4 locking the screen after the VM is idle for sometime')
# It's not necessary, since the Host SO will ask for password in the lock screen after being idle for sometime
# these next commands came from here: https://askubuntu.com/questions/259190/xubuntu-no-password-request-after-suspension
execute_command_in_bash('xfconf-query -c xfce4-session -p /shutdown/LockScreen -s false')
execute_command_in_bash('xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/lock-screen-suspend-hibernate -s false')
# disable screen saver lock screen
# came from here: https://askubuntu.com/a/1263959
execute_command_in_bash('xfconf-query -c xfce4-screensaver -p /lock/enabled -s false')
logger.info('> Configuration done')

logger.info('Disable window dragging with alt+click')
execute_command_in_bash('xfconf-query -c xfwm4 -p /general/easy_click -s none')
logger.info('> Configuration done')

logger.info('Windows Key open Application Menu (Whisker Menu)')
execute_command_in_bash('xfconf-query -c xfce4-keyboard-shortcuts -p /commands/custom/Super_L --create -t string -s xfce4-popup-whiskermenu')
logger.info('> Configuration done')

logger.info('Install Meld')
execute_command_in_bash('sudo apt-get install -y meld')
logger.info('> Installed successfully')

logger.info('Install Kubectl')
execute_command_in_bash('sudo snap install kubectl --classic')
logger.info('> Installed successfully')

logger.info('Configure kubectl autocompletion')
execute_command_in_bash('kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null')
logger.info('> Successfully configured kubectl bash completion')

logger.info('Install AWS CLI')
awscli_installer_dir_path = installers_dir_path + '/aws'
awscli_unzipped_path = f'{awscli_installer_dir_path}/aws'
logger.info(f' > Creating \'{awscli_installer_dir_path}\'')
if not os.path.exists(awscli_installer_dir_path):
    os.mkdir(awscli_installer_dir_path)
    logger.info(' > Created')
else:
    logger.info(' > Already exists')
logger.info(' > Installing AWS CLI')
if os.path.exists('/usr/local/bin/aws'):
    logger.info(' > Already installed')
else:
    logger.info(' > Download AWS CLI Zip')
    awscli_zip_path = awscli_installer_dir_path + '/awscliv2.zip'
    if not os.path.exists(awscli_zip_path):
        execute_command_in_bash(f'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "{awscli_zip_path}"')
        logger.info(' > Downloaded AWS CLI Zip')
    else:
        logger.info(' > Already exists')
    
    if not os.path.exists(awscli_unzipped_path):
        execute_command_in_bash(f'unzip {awscli_zip_path} -d {awscli_installer_dir_path}')
    
    execute_command_in_bash(f'sudo {awscli_unzipped_path}/install')
    logger.info(' > Successfully installed')
logger.info('> Successfully installed')

logger.info('Ensure AWS CLI latest version')
execute_command_in_bash(f'sudo {awscli_unzipped_path}/install --update')
logger.info('> Successfully ensured latest version')

lens_deb_url = 'https://api.k8slens.dev/binaries/Lens-5.2.6-latest.20211104.1.amd64.deb'
lens_deb_name = 'Lens-5.2.6-latest.20211104.1.amd64.deb'
lens_deb_path = installers_dir_path + '/' + lens_deb_name
logger.info(f'  Download Lens .deb file from \'{lens_deb_url} to {lens_deb_path}\'...')
if not os.path.exists(lens_deb_path): # verify md5sum?
    with urllib.request.urlopen(lens_deb_url) as response:
        with open(lens_deb_path, 'wb+') as lens_deb_file:
            shutil.copyfileobj(response, lens_deb_file)
    logger.info('  > Downloaded sucessfully')
else:
    logger.info('  > Already downloaded')

logger.info(f'  Install Lens...')
execute_command_in_bash(f'sudo apt-get install -y {lens_deb_path}')


logger.info('Install DBeaver')
execute_command_in_bash('sudo snap install dbeaver-ce')
logger.info('> Installed successfully')

logger.info('Install tfenv')
tfenv_repository_url = 'https://github.com/tfutils/tfenv.git'
tfenv_repository_path = installers_dir_path + '/' + 'tfenv'
logger.info(f"> Clone tfenv repository on \'{tfenv_repository_path}\'...")
if not os.path.exists(tfenv_repository_path):
    completed_process = subprocess.run(['git', 'clone', tfenv_repository_url, tfenv_repository_path], capture_output=True, text=True)
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

logger.info('> Add tfenv to path')
if not os.path.exists('/usr/local/bin/tfenv'):
    execute_command_in_bash(f'sudo ln -s {tfenv_repository_path}/bin/tfenv /usr/local/bin')
    logger.info(' > Added tfenv to path')

if not os.path.exists('/usr/local/bin/terraform'):
    execute_command_in_bash(f'sudo ln -s {tfenv_repository_path}/bin/terraform /usr/local/bin')
    logger.info(' > Added tfenv\'s terraform to path')

logger.info('> Already in path')