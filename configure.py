import os
import logging
import urllib.request
import shutil
import re
import subprocess
from pathlib import Path

def bash(command_text):
    # logger.debug(f'Executing command {command_text}')
    completed_process = subprocess.run(['bash', '-c', command_text], capture_output=True, text=True)
    if completed_process.returncode != 0:
        logger.info(f'> An error happened while executing command on bash: {command_text}')
        logger.info(f'Return Code: {completed_process.returncode}')
        logger.info(f'Stdout: \'{completed_process.stdout}\'')
        logger.info(f'Stderr: \'{completed_process.stderr}\'')
        exit(1)
    
    return completed_process

def create_folder(folder_path):
    logger.info(f"Create '{folder_path}' directory...")
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        logger.info('> Created')
    else:
        logger.info('> Already exists')

def clone_git_repo(repo_url, clone_path):
    repo_folder_name = re.search(r'.*/(.*)\.git', repo_url).group(1)
    repo_path = os.path.join(clone_path, repo_folder_name)
    logger.info(f"Clone {repo_url} repository on \'{repo_path}\'...")
    
    if not os.path.exists(repo_path):
        print(f'git clone {repo_url} {repo_path}')
        logger.info(f'> Cloned successfully')
    else:
        logger.info('> Already exists')

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(asctime)s - %(name)s: %(message)s')
logger = logging.getLogger(__name__)

home_path = str(Path.home())
files_path = os.path.join(home_path, 'files')
configuration_path = os.path.join(home_path, 'configuration')
installers_path = os.path.join(configuration_path, 'installers')
code_path = os.path.join(files_path, 'code')

logger.info(f'Home is {home_path}')

create_folder(files_path)
create_folder(configuration_path)
create_folder(installers_path)
create_folder(code_path)

logger.info(f'Install latest version of VS Code...')
completed_process = subprocess.run(['dpkg', '-s', 'code'], capture_output=True, text=True)
if completed_process.returncode != 0:
    vscode_deb_url = 'https://go.microsoft.com/fwlink/?LinkID=760868'
    vscode_deb_name = 'code_1.46.1-1592428892_amd64.deb'
    vscode_deb_path = installers_path + '/' + vscode_deb_name
    logger.info(f'  Download VS Code .deb file from \'{vscode_deb_url} to {vscode_deb_path}\'...')
    if not os.path.exists(vscode_deb_path): # verify md5sum?
        with urllib.request.urlopen(vscode_deb_url) as response:
            with open(vscode_deb_path, 'wb+') as vscode_deb_file:
                shutil.copyfileobj(response, vscode_deb_file)
        logger.info('  > Downloaded sucessfully')
    else:
        logger.info('  > Already downloaded')

    logger.info(f'  Install VS Code...')
    bash(f'sudo apt-get install -y {vscode_deb_path}')
    logger.info(f'  > Installed successfully')

logger.info(f'  Ensure VS Code is in latest version...')
bash('sudo apt-get install -y code')
logger.info(f'  > Updated successfully')
logger.info(f'> VS Code is in the latest version.')

# VS Code extension ids can be found on the 'Identifier field'
# of the extension page, at the bottom right corner
vscode_extensions = [
    ('Python', 'ms-python.python'),
    ('Docker', 'ms-azuretools.vscode-docker'),
    ('Terraform', 'hashicorp.terraform'),
    ('Prisma', 'prisma.prisma'),
    ('C#', 'ms-dotnettools.csharp')
]
for extension in vscode_extensions:
    logger.info(f'Install {extension[0]} extension on VS Code...')
    bash(f'code --install-extension {extension[1]}')
    logger.info(f'> Installed successfully')

logger.info('Adding custom configuration to VS Code')
bash('cp vscode/keybindings.json ~/.config/Code/User/keybindings.json')
bash('cp vscode/settings.json ~/.config/Code/User/settings.json')
logger.info('> Custom configuration set')

# Instruction from https://docs.docker.com/engine/install/ubuntu/
logger.info(f'Setup Docker repositories...')
bash('sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release')

docker_keyring_path = '/usr/share/keyrings/docker-archive-keyring.gpg';
if not os.path.exists(docker_keyring_path):
    bash(f'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o {docker_keyring_path}')

docker_repo_configuration_file_path = '/etc/apt/sources.list.d/docker.list'
if not os.path.exists(docker_repo_configuration_file_path):
    bash(f'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee {docker_repo_configuration_file_path} > /dev/null')
    bash('sudo apt-get update')
logger.info(f'> Docker repositories have been defined')

logger.info(f'Install Docker...')
bash('sudo apt-get install -y docker-ce docker-ce-cli containerd.io')
logger.info(f'> Installed successfully...')

logger.info(f'Configure Docker to be run by non-root user')
bash('sudo usermod -aG docker $USER')
logger.info(f'> Configuration applied successfully')

logger.info(f'Install Docker-Compose')
docker_compose_bin_path = '/usr/local/bin/docker-compose'
if not os.path.exists(docker_compose_bin_path):
    bash(f'sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o {docker_compose_bin_path}')    
    logger.info('  > Downloaded sucessfully')
else:
    logger.info('  > Download already done')
bash(f'sudo chmod +x {docker_compose_bin_path}')
logger.info(f'> Installed successfully...')

logger.info(f'Install Git...')
bash('sudo apt-get install -y git')
logger.info(f'> Installed successfully')

gitconfig_path = os.path.join(home_path, '.gitconfig')
logger.info(f'Creating .gitconfig file at \'{gitconfig_path}\'')

bash(f'cp git/.gitconfig {gitconfig_path}')
logger.info(f'> sucessfully defined .gitconfig')

git_repo_urls = [
    'git@github.com:daniellima/autopy.git',
    'git@github.com:daniellima/awesome-links-generator.git',
]

for repo_url in git_repo_urls:
    clone_git_repo(repo_url, code_path)

logger.info('Install net-tools')
bash('sudo apt-get install -y net-tools')
logger.info('> Installed successfully')

logger.info('Install htop')
bash('sudo apt-get install -y htop')
logger.info('> Installed successfully')

logger.info('Install Postman')
bash('sudo snap install postman')
logger.info('> Installed successfully')

logger.info('Disable Xfce4 locking the screen after the VM is idle for sometime')
# It's not necessary, since the Host SO will ask for password in the lock screen after being idle for sometime
# these next commands came from here: https://askubuntu.com/questions/259190/xubuntu-no-password-request-after-suspension
bash('xfconf-query -c xfce4-session -p /shutdown/LockScreen -s false')
bash('xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/lock-screen-suspend-hibernate -s false')
# disable screen saver lock screen
# came from here: https://askubuntu.com/a/1263959
bash('xfconf-query -c xfce4-screensaver -p /lock/enabled -s false')
logger.info('> Configuration done')

logger.info('Disable window dragging with alt+click')
bash('xfconf-query -c xfwm4 -p /general/easy_click -s none')
logger.info('> Configuration done')

logger.info('Windows Key open Application Menu (Whisker Menu)')
bash('xfconf-query -c xfce4-keyboard-shortcuts -p /commands/custom/Super_L --create -t string -s xfce4-popup-whiskermenu')
logger.info('> Configuration done')

logger.info('Install Meld')
bash('sudo apt-get install -y meld')
logger.info('> Installed successfully')

logger.info('Install Kubectl')
bash('sudo snap install kubectl --classic')
logger.info('> Installed successfully')

logger.info('Configure kubectl autocompletion')
bash('kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null')
logger.info('> Successfully configured kubectl bash completion')

logger.info('Install AWS CLI')
awscli_installer_dir_path = installers_path + '/aws'
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
        bash(f'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "{awscli_zip_path}"')
        logger.info(' > Downloaded AWS CLI Zip')
    else:
        logger.info(' > Already exists')
    
    if not os.path.exists(awscli_unzipped_path):
        bash(f'unzip {awscli_zip_path} -d {awscli_installer_dir_path}')
    
    bash(f'sudo {awscli_unzipped_path}/install')
    logger.info(' > Successfully installed')
logger.info('> Successfully installed')

lens_deb_url = 'https://api.k8slens.dev/binaries/Lens-5.2.6-latest.20211104.1.amd64.deb'
lens_deb_name = 'Lens-5.2.6-latest.20211104.1.amd64.deb'
lens_deb_path = installers_path + '/' + lens_deb_name
logger.info(f'  Download Lens .deb file from \'{lens_deb_url} to {lens_deb_path}\'...')
if not os.path.exists(lens_deb_path): # verify md5sum?
    with urllib.request.urlopen(lens_deb_url) as response:
        with open(lens_deb_path, 'wb+') as lens_deb_file:
            shutil.copyfileobj(response, lens_deb_file)
    logger.info('  > Downloaded sucessfully')
else:
    logger.info('  > Already downloaded')

logger.info(f'  Install Lens...')
bash(f'sudo apt-get install -y {lens_deb_path}')

logger.info('Install tfenv')
clone_git_repo('https://github.com/tfutils/tfenv.git', installers_path)

tfenv_repository_path = os.path.join(installers_path, 'tfenv')
logger.info('> Add tfenv to path')
if not os.path.exists('/usr/local/bin/tfenv'):
    bash(f'sudo ln -s {tfenv_repository_path}/bin/tfenv /usr/local/bin')
    logger.info(' > Added tfenv to path')

if not os.path.exists('/usr/local/bin/terraform'):
    bash(f'sudo ln -s {tfenv_repository_path}/bin/terraform /usr/local/bin')
    logger.info(' > Added tfenv\'s terraform to path')

logger.info('> tfenv in path')

# Apparently there is not a package to install just the redis-cli.
# So, we install the server package and disable the server installation
logger.info('Install Redis CLI')
bash('sudo apt-get install -y redis-server')
bash('sudo systemctl disable redis-server')
bash('sudo systemctl stop redis-server')
logger.info('> Installed successfully')

# Instruction from https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/#install-mongodb-community-edition-using-deb-packages
logger.info(f'Setup MongoDB repositories...')

bash(f'wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -')

mongodb_repo_configuration_file_path = '/etc/apt/sources.list.d/mongodb-org-5.0.list'
if not os.path.exists(mongodb_repo_configuration_file_path):
    bash(f'echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee {mongodb_repo_configuration_file_path}')
    bash('sudo apt-get update')
logger.info(f'> MongoDB repositories have been defined')

logger.info(f'Install MongoDB Shell and Tools...')
bash('sudo apt-get install -y mongodb-mongosh mongodb-org-tools')
logger.info(f'> Installed successfully...')

logger.info(f'Install NVM...')
bash('curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash')
logger.info(f'> Installed successfully...')

logger.info(f'Install jq...')
bash('sudo apt-get install -y jq')
logger.info(f'> Installed successfully...')

logger.info(f'Installing .NET 6 SDK')
dotnet_deb_file_path = os.path.join(installers_path, 'packages-microsoft-prod.deb')
if not os.path.exists(dotnet_deb_file_path):
    bash(f'wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O {dotnet_deb_file_path}')
    bash(f'sudo dpkg -i {dotnet_deb_file_path}')
    bash('sudo apt-get update')
bash('sudo apt-get install -y dotnet-sdk-6.0')

dbeaver_deb_url = 'https://dbeaver.io/files/22.0.5/dbeaver-ce_22.0.5_amd64.deb'
dbeaver_deb_name = 'dbeaver-ce_22.0.5_amd64.deb'
dbeaver_deb_path = installers_path + '/' + dbeaver_deb_name
logger.info(f'  Download Debeaver .deb file from \'{dbeaver_deb_url} to {dbeaver_deb_path}\'...')
if not os.path.exists(dbeaver_deb_path): # verify md5sum?
    with urllib.request.urlopen(dbeaver_deb_url) as response:
        with open(dbeaver_deb_path, 'wb+') as dbeaver_deb_file:
            shutil.copyfileobj(response, dbeaver_deb_file)
    logger.info('  > Downloaded sucessfully')
else:
    logger.info('  > Already downloaded')

logger.info(f'  Install DBeaver Community...')
bash(f'sudo apt-get install -y {dbeaver_deb_path}')