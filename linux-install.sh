#!/bin/bash

# Create the destination directory
mkdir $HOME/Diffusion-Browser

# Store the current directory in a variable
current_dir=$(pwd)

# Store the home directory of the user in a variable
home_dir=$HOME

# Use the 'cp' command to copy the contents of the current directory to the home directory
# The '-r' flag specifies to copy the contents recursively, so that any subdirectories and their contents are also copied
cp -r $current_dir/* $home_dir/Diffusion-Browser

# Create the .desktop file
cd ~/.local/share/applications
cp ~/Diffusion-Browser/Diffusion-Browser.desktop ~/.local/share/applications


# Print a message to indicate that the copy is complete
echo "Installation complete!"
