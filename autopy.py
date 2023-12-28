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

def clone_git_repo(repo_url, clone_path, repo_folder_name=None):
    if repo_folder_name is None:
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
    "zsh",
    "make",
    "fzf",
    "python3-pip",
    "python3-venv",
    "python3-distutils", # fix this bug related to ubuntu jammy and python3.10: https://github.com/pre-commit/pre-commit/issues/2336 as recommended here: https://github.com/deadsnakes/python3.10-jammy
    "libffi-dev", # needed for python to properly import _ctypes package. See: https://stackoverflow.com/a/48045929
    "libpq-dev", # to install psycopg from source
    "build-essential",  #
    "zlib1g-dev",       #
    "libssl-dev",       #
    "libbz2-dev",       # A bunch of libs so that python can work properly
    "libreadline-dev",  #
    "libsqlite3-dev",   #
    "liblzma-dev",      #
    "postgresql-client",#
    "tree",
]
bash(f'sudo apt-get install -y {" ".join(apps)}')


log_section('Postman')

# Stopped using the snap install because it's really outdated
# See: https://github.com/postmanlabs/postman-app-support/issues/9573
# bash('sudo snap install postman')
postman_download_path, _ = download('https://dl.pstmn.io/download/latest/linux64', 'postman-linux-x64.tar.gz')
bash(f'tar -zxvf {postman_download_path} -C {configuration_path}')
with open('postman/postman.desktop', 'r') as f:
    content = f.read()
content = content.replace('{{POSTMANPATH}}', configuration_path)
with open(f'{home_path}/.local/share/applications/postman.desktop', 'w') as f:
    f.write(content)


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
    ('C#', 'ms-dotnettools.csharp'),
    ('Go', 'golang.go')
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
bash('sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin')
# Configure Docker to be run by non-root user
bash('sudo usermod -aG docker $USER')


log_section('Git')

gitconfig_path = os.path.join(home_path, '.gitconfig')
bash(f'cp git/.gitconfig {gitconfig_path}')

git_repo_urls = [
    'git@github.com:daniellima/autopy.git',
    'git@github.com:daniellima/awesome-links-generator.git',
    'git@github.com:daniellima/snippets.git'
]

for repo_url in git_repo_urls:
    clone_git_repo(repo_url, code_path)


# log_section('XFCE 4')


# # Disable Xfce4 locking the screen after the VM is idle for sometime
# # It's not necessary, since the Host SO will ask for password in the lock screen after being idle for sometime
# # these next commands came from here: https://askubuntu.com/questions/259190/xubuntu-no-password-request-after-suspension
# bash('xfconf-query -c xfce4-session -p /shutdown/LockScreen -s false')
# bash('xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/lock-screen-suspend-hibernate -s false')
# # disable screen saver lock screen
# # came from here: https://askubuntu.com/a/1263959
# bash('xfconf-query -c xfce4-screensaver -p /lock/enabled -s false')
# # Disable window dragging with alt+click')
# bash('xfconf-query -c xfwm4 -p /general/easy_click -s none')


log_section('Kubectl')

bash('sudo rm /etc/apt/keyrings/kubernetes-archive-keyring.gpg') # gpg will ask for confirmation if overwriting file. Instead of using --yes, which can be dangerous since I don't know all the questions it does, it's better to delete the file
bash('curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg')
bash('echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list')
bash('sudo apt-get update')
bash('sudo apt-get install -y kubectl')

kubectx_path, _ = download("https://github.com/ahmetb/kubectx/raw/master/kubectx")
bash(f'sudo mv {kubectx_path} /usr/local/bin')
bash(f'sudo chmod +x /usr/local/bin/kubectx')

kubens_path, _ = download("https://github.com/ahmetb/kubectx/raw/master/kubens")
bash(f'sudo mv {kubens_path} /usr/local/bin')
bash(f'sudo chmod +x /usr/local/bin/kubens')


log_section('AWS CLI')

awscli_installer_dir_path = os.path.join(downloads_path, 'aws')
awscli_unzipped_path = os.path.join(awscli_installer_dir_path, 'aws')
create_folder(awscli_installer_dir_path)
if not os.path.exists('/usr/local/bin/aws'):
    awscli_zip_path, _ = download('https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip')
    bash(f'rm -rf {awscli_unzipped_path}')
    bash(f'unzip {awscli_zip_path} -d {awscli_installer_dir_path}')
    bash(f'sudo {awscli_unzipped_path}/install')


log_section('Redis')

# Apparently there is not a package to install just the redis-cli.
# So, we install the server package and disable the server installation
bash('sudo apt-get install -y redis-server')
bash('sudo systemctl disable redis-server')
bash('sudo systemctl stop redis-server')


log_section('Mongo DB')

# Instruction from https://www.mongodb.com/docs/v5.0/tutorial/install-mongodb-on-ubuntu/
bash('sudo rm /usr/share/keyrings/mongodb-server-5.0.gpg') # gpg will ask for confirmation if overwriting file. Instead of using --yes, which can be dangerous since I don't know all the questions it does, it's better to delete the file
bash(f'curl -fsSL https://pgp.mongodb.com/server-5.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-5.0.gpg --dearmor')
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

dbeaver_deb_path, _ = download('https://dbeaver.io/files/22.2.4/dbeaver-ce_22.2.4_amd64.deb')
bash(f'sudo apt-get install -y {dbeaver_deb_path}')


log_section('Download Go')

go_tar_path, _ = download('https://go.dev/dl/go1.20.2.linux-amd64.tar.gz')
bash('sudo rm -rf /usr/local/go')
bash(f'sudo tar -C /usr/local -xzf {go_tar_path}')


log_section('Install Brave Browser')

bash('sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg')
brave_configuration_file_path = '/etc/apt/sources.list.d/brave-browser-release.list'
if not os.path.exists(brave_configuration_file_path):
    bash(f'echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee {brave_configuration_file_path}')
    bash('sudo apt-get update')
bash('sudo apt install -y brave-browser')


log_section('Install Bitwarden')

path, _ = download('https://vault.bitwarden.com/download/?app=desktop&platform=linux&variant=deb', 'bitwarden.deb')
bash(f'sudo apt-get install -y {path}')

log_section('Terraform')

clone_git_repo('https://github.com/tfutils/tfenv.git', downloads_path)

tfenv_repository_path = os.path.join(downloads_path, 'tfenv')
if not os.path.exists('/usr/local/bin/tfenv'):
    bash(f'sudo ln -s {tfenv_repository_path}/bin/tfenv /usr/local/bin')
if not os.path.exists('/usr/local/bin/terraform'):
    bash(f'sudo ln -s {tfenv_repository_path}/bin/terraform /usr/local/bin')

bash('go install github.com/terraform-docs/terraform-docs@v0.16.0')


log_section('Install Terragrunt')

terragrunt_path, _ = download("https://github.com/gruntwork-io/terragrunt/releases/download/v0.48.4/terragrunt_linux_amd64")
bash(f'sudo mv {terragrunt_path} /usr/local/bin/terragrunt')
bash(f'sudo chmod +x /usr/local/bin/terragrunt')


log_section('Install kops')

kops_path, _ = download("https://github.com/kubernetes/kops/releases/download/v1.25.3/kops-linux-amd64")
bash(f'sudo mv {kops_path} /usr/local/bin/kops')
bash(f'sudo chmod +x /usr/local/bin/kops')


log_section('Install K6')

bash('sudo gpg -k') # Ensure that GPG folder is created. See: https://k6.io/docs/getting-started/installation/troubleshooting/#error-importing-k6s-gpg-key
bash('sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69')
source_list_file = '/etc/apt/sources.list.d/k6.list'
if not os.path.exists(source_list_file):
    bash(f'echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee {source_list_file}')
    bash('sudo apt-get update')
bash('sudo apt-get install k6')


log_section('Install Kind')

bash('go install sigs.k8s.io/kind@v0.16.0')


log_section('Install Tilt')

bash('curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash')


log_section('Install pre-commit')

bash('sudo pip3 install pre-commit')


log_section("Install go-migrate")

bash('go install -tags \'postgres\' github.com/golang-migrate/migrate/v4/cmd/migrate@v4.15.2')


log_section('Install Helm')

bash('sudo snap install helm --classic')

log_section('Install aws2-wrap')

bash('sudo pip3 install aws2-wrap')

log_section('Install Hashicorp Vault')

bash('wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg >/dev/null')
vault_configuration_file_path = '/etc/apt/sources.list.d/hashicorp.list'
if not os.path.exists(vault_configuration_file_path):
    bash(f'echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee {vault_configuration_file_path}')
    bash('sudo apt-get update')
bash('sudo apt install -y vault')

log_section('Install Hashicorp Boundary')

boundary_configuration_file_path = '/etc/apt/sources.list.d/hashicorp.list'
if not os.path.exists(boundary_configuration_file_path):
    bash(f'echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee {boundary_configuration_file_path}')
    bash('sudo apt-get update')
bash('sudo apt install -y boundary')

log_section('Install poetry')

bash('curl -sSL https://install.python-poetry.org | python3 -')
if not os.path.exists('/usr/local/bin/poetry'):
    bash('sudo ln -s ~/.local/share/pypoetry/venv/bin/poetry /usr/local/bin')

bash('poetry config virtualenvs.in-project true')


log_section('Pyenv')

if not os.path.exists(os.path.join(home_path, '.pyenv')):
    bash('curl https://pyenv.run | bash')

bash('echo \'export PYENV_ROOT="$HOME/.pyenv"\' >> ~/.zshrc')
bash('echo \'[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"\' >> ~/.zshrc')
bash('echo \'eval "$(pyenv init -)"\' >> ~/.zshrc')


log_section('Load local specific commands')

if not os.path.exists('local.py'):
    bash('cp local.sample.py local.py')

exec(open('local.py').read())