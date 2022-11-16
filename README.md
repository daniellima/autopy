# Autopy

This project is a pet project with the intention of quickly configuring a new machine with all the changes I need.

In the past I used Ansible to configure my local machine, but with time I started to think that the complexity of ansible
is not worth it, including having to install ansible mannually. Ansible shines when configuring multiple remote machines, but
I want to just configure one local machine. Also, I am a developer and Ansible YAML language feels very limited and cumbersome.
Shell is a obvious alternative, but the syntax and semantics are years behind modern languages.

This project was then created to test my theory that for a single machine, and with just a bit of python, I could get 90% of what 
Ansible offers with 10% the effort:

- The main script just needs python3 and bash, nothing more.
- It is idempotent
- There is just 50 or so lines of 'framework' code. There is a lot of things that are already idempotent in shell and so don't need any ansible modules
- Everything is plain python, with the if's and for's builtin in the language. Don't need to [create a programming language in YAML](https://stackoverflow.com/questions/40127586/is-ansible-turing-complete)

## Manual Steps
Not everything is easily automated. These are the things I could not automate yet:

- Restart session to make docker group configuration take effect
- Change postman theme to black
- Change postman to use dual vertical panels
- run nvm install --lts 
  > NVM is an alias loaded in bashrc and I cannot find a way to launch it from python. Using bash -i to force the loading of .bashrc for some reason causes the python process to stop. See: https://unix.stackexchange.com/questions/101620/how-to-load-bashrc-from-bash-c)
- run npm install -g kafka-console (needs node installed, see item above)
- run npm install -g bull-repl (needs node installed, see item above)

## Improvements
- Create abstraction to install packages that require adding GPG keys and creating list files. It's sad, but you cannot simply apt-get install anything these days.