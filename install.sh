#!/bin/bash

# Download and install Miniconda, then create gnuradio environment

# Set download URL and file name
URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh"
INSTALLER="Miniconda3-latest-Linux-x86_64.sh"

# Download Miniconda installer
echo "Downloading Miniconda installer..."
wget $URL -O $INSTALLER

# Check if download was successful
if [ ! -f "$INSTALLER" ]; then
    echo "Failed to download Miniconda installer"
    read -p "Press any key to continue..."
    exit 1
fi

# Install Miniconda
echo "Installing Miniconda..."
bash $INSTALLER -b -p $HOME/miniconda3

# Check if installation was successful
if [ ! -f "$HOME/miniconda3/bin/conda" ]; then
    echo "Miniconda installation failed"
    read -p "Press any key to continue..."
    exit 1
fi

# Initialize conda
echo "Initializing conda..."
$HOME/miniconda3/bin/conda init bash

# Create gnuradio environment
echo "Creating gnuradio environment..."
$HOME/miniconda3/bin/conda create -n gnuradio python=3.9 -y

# Check if environment was created successfully
if ! $HOME/miniconda3/bin/conda info --envs | grep -q gnuradio; then
    echo "Failed to create gnuradio environment"
    read -p "Press any key to continue..."
    exit 1
fi

# Activate the environment and install GNU Radio packages
echo "Activating gnuradio environment and installing packages..."
source $HOME/miniconda3/bin/activate gnuradio
$HOME/miniconda3/bin/conda install -c conda-forge gnuradio gnuradio-iio -y

echo "Installation completed successfully!"
echo "To activate the gnuradio environment, run: conda activate gnuradio"
read -p "Press any key to continue..."