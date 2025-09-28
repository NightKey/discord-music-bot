#!bin/bash

echo $'\033]30;Discord Music Bot Installer\007'

cd "$(dirname "$0")"

python -m pip install virtualenv
x-terminal-emulator -e run.sh "$@"
