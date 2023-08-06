elf_commander_python
====================

This Python package (elfcommander) creates a class named ElfCommander
to communcate with and control the Janelia Elf. The Elf uses two
hardware control devices, the mixed\_signal\_controller
modular\_device, and the bioshake_device. The
mixed\_signal\_controller both switches the valves and reads the
analog signals from the cylinder hall effect sensors. The
bioshake\_device controls the heater/shaker.

Authors:

    Peter Polidoro <polidorop@janelia.hhmi.org>

License:

    BSD

##Example Usage

[Example Config File](./example_config.yaml)

Open a terminal and enter:

```shell
source ~/virtualenvs/elfcommander/bin/activate
elfcommander example_calibration.yaml example_config.yaml
```

##Installation

[Setup Python](https://github.com/janelia-pypi/python_setup)

####Debian-based Linux Install Dependencies

Open a terminal and enter:

```shell
sudo apt-get install git python-pip python-virtualenv python-dev build-essential -y
```

###Linux and Mac OS X

Open a terminal and enter:

```shell
mkdir ~/git
cd ~/git
git clone https://github.com/janelia-idf/elf_config.git
git clone https://github.com/janelia-idf/elf.git
cd elf
git submodule init
git submodule update
cd ~
mkdir ~/virtualenvs
cd ~/virtualenvs
virtualenv elfcommander
source ~/virtualenvs/elfcommander/bin/activate
pip install elfcommander
```

On linux, you may need to add yourself to the group 'dialout' in order
to have write permissions on the USB port:

Open a terminal and enter:

```shell
sudo usermod -aG dialout $USER
sudo reboot
```

###Windows

Open a terminal and enter:

```shell
virtualenv C:\virtualenvs\elfcommander
C:\virtualenvs\elfcommander\Scripts\activate
pip install ipython
pip install elfcommander
```
