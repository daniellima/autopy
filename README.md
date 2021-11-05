# Autopy

#TODO

- Install VS Code with snap
- Ensure this script don't depends on anything besides plain python3
- Or make autopy instalable via pip (use poetry if this is the case)
- Maybe this script should install autopy by itself and then import it
- Generate SSH Key
- Reuse code that is repeated at least three times
- change hostname
- Add timeout. One apt install command got stuck and blocked the entire installation 
    - Waiting for cache lock: Could not get lock /var/lib/dpkg/lock-frontend. It is held by process 8268 (unattended-upgr)
- Deactivate unnatend_upgrades. Don't want to stop my develpment environment for hours because of a update
    - https://askubuntu.com/questions/934807/unattended-upgrades-status
- Adicionar cor no output
- Colocar linhas de log mais agradáveis. Ou mudar para ser só print mesmo
- stop using sudo on the commands. If sudo is needed, I must call `sudo python3 configure.py`
- instalar SOPS https://github.com/mozilla/sops/releases