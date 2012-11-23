#!/bin/bash
# env.sh
# Run this script to configure the environment and start a subshell.

# Add source directory to path.
PATH=$(pwd)/emu:$PATH

PS1='(emu) $ ' bash -i
