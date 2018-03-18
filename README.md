# IAA-image
Fetches container for using DKPro statistics with Python and IPython.

## Setup

The software is installed in a Docker container. If you do not have Docker already, you will need to install it.
* For OS X El Capitan 10.11 or newer, install [Docker-for-Mac](https://docs.docker.com/docker-for-mac/).
* Otherwise install [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_mac/)
* For Windows 10 Pro [detailed requirements](https://docs.docker.com/docker-for-windows/install/#what-to-know-before-you-install), install [Docker-for-Windows](https://docs.docker.com/docker-for-windows/).
* Otherwise install [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)
* For Ubuntu and other Linux distributions, install
[docker](https://docs.docker.com/engine/installation/linux/ubuntu/) and
[docker-compose](https://docs.docker.com/compose/install/).
  To [avoid having to use sudo when you use the docker command](https://docs.docker.com/install/linux/linux-postinstall/),
create a Unix group called docker and add users to it:
  1. `sudo groupadd docker`
  2. `sudo usermod -aG docker $USER`

Once installed, start the Docker application (if on a Mac), then go to the project directory and run:

1. `docker-compose pull`
1. `./run_iaa.sh`

Now you can run IPython:

1. `ipython`

You can try the sample code with:

1. `python ./quickstart.py`
1. `python ./testKrippendorff.py`

## Resources for DKPro Agreement Library

1. [DKPro Agreement Poster](https://dkpro.github.io/dkpro-statistics/dkpro-agreement-poster.pdf)
1. [A Brief Tutorial on Inter-Rater Agreement](https://dkpro.github.io/dkpro-statistics/inter-rater-agreement-tutorial.pdf)
1. [Getting Started with DKPro Agreement](https://dkpro.github.io/dkpro-statistics/dkpro-agreement-tutorial.pdf)
1. [COLING 2014 paper](http://anthology.aclweb.org/C/C14/C14-2023.pdf), which gives an overview of the implementation and its evaluation.
1. [DKPro API docs](https://dkpro.github.io/dkpro-statistics/releases/2.1.0/apidocs/index.html)
1. [DKPro Agreement source code](https://github.com/dkpro/dkpro-statistics)
