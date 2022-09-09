import os
import logging
import re
import subprocess
from pathlib import Path

def log_section(section_name):
   logger.info(f'-------------------- {section_name} --------------------')

def bash(command_text):
    logger.info(f'$ {command_text}')
    completed_process = subprocess.run(['bash', '-c', command_text], capture_output=True, text=True)
    if completed_process.returncode != 0:
        logger.info(f'> An error happened while executing command on bash: {command_text}')
        logger.info(f'Return Code: {completed_process.returncode}')
        logger.info(f'Stdout: \'{completed_process.stdout}\'')
        logger.info(f'Stderr: \'{completed_process.stderr}\'')
        exit(1)
    
    return completed_process

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        logger.info(f"Created '{folder_path}' directory")

def clone_git_repo(repo_url, clone_path):
    repo_folder_name = re.search(r'^.*/(.*)\.git$', repo_url).group(1)
    repo_path = os.path.join(clone_path, repo_folder_name)
    
    if not os.path.exists(repo_path):
        bash(f'git clone {repo_url} {repo_path}')

def download(from_url, to_file_name=None):
    if to_file_name is None:
        to_file_name = os.path.basename(from_url)

    download_file_path = os.path.join(downloads_path, to_file_name)
    if not os.path.exists(download_file_path):
        bash(f'curl -L "{from_url}" -o {download_file_path}')
        return download_file_path, True
    else:
        return download_file_path, False

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(asctime)s - %(name)s: %(message)s')
logger = logging.getLogger('autopy')

home_path = str(Path.home())
files_path = os.path.join(home_path, 'files')
configuration_path = os.path.join(home_path, 'configuration')
downloads_path = os.path.join(configuration_path, 'downloads')
code_path = os.path.join(files_path, 'code')


log_section('Basic folders')

create_folder(files_path)
create_folder(configuration_path)
create_folder(downloads_path)
create_folder(code_path)


log_section('Built in packages')

apps = [
    "apt-transport-https ca-certificates curl gnupg lsb-release", # for docker
    "git",
    "htop",
    "net-tools",
    "jq",
    "meld",
    "zsh"
]
bash(f'sudo apt-get install -y {" ".join(apps)}')


log_section('Postman')

bash('sudo snap install postman')


log_section('ZSH')
# Makes zsh the default shell
bash('sudo bash -c "chsh -s $(which zsh) $USER"')
zshrc_path = os.path.join(home_path, '.zshrc')
bash(f'touch {zshrc_path}')
if not os.path.exists(os.path.join(home_path, '.oh-my-zsh')):
    # using echo to respond 'no' when install script asks if I want to make zsh the default shell
    bash('echo n | sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"')
# oh my zsh installation overrides the .zshrc file. So we set it after installing oh my zsh
bash(f'cat zsh/.zshrc zsh/zsh_conf.sh zsh/git_alias.sh zsh/docker_compose_alias.sh > {zshrc_path}')
# install custom theme
zsh_custom_path = bash('zsh -ic \'echo $ZSH_CUSTOM\'').stdout.split()[-1].strip()
zsh_theme_path = os.path.join(zsh_custom_path, 'themes')
clone_git_repo('https://github.com/reobin/typewritten.git', zsh_theme_path)


log_section('VS Code')

vscode_deb_path, downloaded = download('https://go.microsoft.com/fwlink/?LinkID=760868', 'code_1.46.1-1592428892_amd64.deb')
if downloaded:
    bash(f'sudo apt-get install -y {vscode_deb_path}')
bash('sudo apt-get install -y code')

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
    bash(f'code --install-extension {extension[1]}')

bash('cp vscode/keybindings.json ~/.config/Code/User/keybindings.json')
bash('cp vscode/settings.json ~/.config/Code/User/settings.json')


log_section('Docker')

# Instruction from https://docs.docker.com/engine/install/ubuntu/
docker_keyring_path = '/usr/share/keyrings/docker-archive-keyring.gpg';
if not os.path.exists(docker_keyring_path):
    bash(f'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o {docker_keyring_path}')
docker_repo_configuration_file_path = '/etc/apt/sources.list.d/docker.list'
if not os.path.exists(docker_repo_configuration_file_path):
    bash(f'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee {docker_repo_configuration_file_path} > /dev/null')
    bash('sudo apt-get update')
bash('sudo apt-get install -y docker-ce docker-ce-cli containerd.io')
# Configure Docker to be run by non-root user
bash('sudo usermod -aG docker $USER')

docker_compose_bin_path = '/usr/local/bin/docker-compose'
docker_compose_path, _ = download('https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-linux-x86_64')
bash(f'sudo cp {docker_compose_path} {docker_compose_bin_path}')
bash(f'sudo chmod +x {docker_compose_bin_path}')


log_section('Git')

gitconfig_path = os.path.join(home_path, '.gitconfig')
bash(f'cp git/.gitconfig {gitconfig_path}')

git_repo_urls = [
    'git@github.com:daniellima/autopy.git',
    'git@github.com:daniellima/awesome-links-generator.git',
]

for repo_url in git_repo_urls:
    clone_git_repo(repo_url, code_path)


log_section('XFCE 4')

# Disable Xfce4 locking the screen after the VM is idle for sometime
# It's not necessary, since the Host SO will ask for password in the lock screen after being idle for sometime
# these next commands came from here: https://askubuntu.com/questions/259190/xubuntu-no-password-request-after-suspension
bash('xfconf-query -c xfce4-session -p /shutdown/LockScreen -s false')
bash('xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/lock-screen-suspend-hibernate -s false')
# disable screen saver lock screen
# came from here: https://askubuntu.com/a/1263959
bash('xfconf-query -c xfce4-screensaver -p /lock/enabled -s false')
# Disable window dragging with alt+click')
bash('xfconf-query -c xfwm4 -p /general/easy_click -s none')
# Windows Key open Application Menu (Whisker Menu)
bash('xfconf-query -c xfce4-keyboard-shortcuts -p /commands/custom/Super_L --create -t string -s xfce4-popup-whiskermenu')


log_section('Kubectl')

bash('sudo snap install kubectl --classic')
# Configure kubectl autocompletion
bash('kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null')


log_section('AWS CLI')

awscli_installer_dir_path = os.path.join(downloads_path, 'aws')
awscli_unzipped_path = os.path.join(awscli_installer_dir_path, 'aws')
create_folder(awscli_installer_dir_path)
if not os.path.exists('/usr/local/bin/aws'):
    awscli_zip_path, _ = download('https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip')
    bash(f'rm -rf {awscli_unzipped_path}')
    bash(f'unzip {awscli_zip_path} -d {awscli_installer_dir_path}')
    bash(f'sudo {awscli_unzipped_path}/install')


log_section('Lens')

lens_deb_path, _ = download('https://api.k8slens.dev/binaries/Lens-5.2.6-latest.20211104.1.amd64.deb')
bash(f'sudo apt-get install -y {lens_deb_path}')


log_section('Terraform')

clone_git_repo('https://github.com/tfutils/tfenv.git', downloads_path)

tfenv_repository_path = os.path.join(downloads_path, 'tfenv')
if not os.path.exists('/usr/local/bin/tfenv'):
    bash(f'sudo ln -s {tfenv_repository_path}/bin/tfenv /usr/local/bin')
if not os.path.exists('/usr/local/bin/terraform'):
    bash(f'sudo ln -s {tfenv_repository_path}/bin/terraform /usr/local/bin')


log_section('Redis')

# Apparently there is not a package to install just the redis-cli.
# So, we install the server package and disable the server installation
bash('sudo apt-get install -y redis-server')
bash('sudo systemctl disable redis-server')
bash('sudo systemctl stop redis-server')


log_section('Mongo DB')

# Instruction from https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/#install-mongodb-community-edition-using-deb-packages
bash(f'wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -')
mongodb_repo_configuration_file_path = '/etc/apt/sources.list.d/mongodb-org-5.0.list'
if not os.path.exists(mongodb_repo_configuration_file_path):
    bash(f'echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee {mongodb_repo_configuration_file_path}')
    bash('sudo apt-get update')
bash('sudo apt-get install -y mongodb-mongosh mongodb-org-tools')


log_section('Node')

bash('curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash')


log_section('.NET 6 SDK')

dotnet_deb_path, downloaded = download('https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb')
if downloaded:
    bash(f'sudo dpkg -i {dotnet_deb_path}')
    bash('sudo apt-get update')
bash('sudo apt-get install -y dotnet-sdk-6.0')


log_section('DBeaver')

dbeaver_deb_path, _ = download('https://dbeaver.io/files/22.1.0/dbeaver-ce_22.1.0_amd64.deb')
bash(f'sudo apt-get install -y {dbeaver_deb_path}')


log_section('Load local specific commands')

if not os.path.exists('local.py'):
    bash('cp local.sample.py local.py')
exec(open('local.py').read())