# docker-verizon-lte-extender-reboot
A Docker Container that uses a Python script to 
reboot a Verizon 4G LTE Network Extender (ASK-SFE116)
on a schedule

This Selenium script for Python will do a soft/safe reboot on a
Verizon 4G LTE Network Extender. My network extender has issues after
being powered on for over a week or so, and there is no way in the GUI
to schedule or automate reboots. This script logs into the web interface
and simulates clicking the soft reboot button.
Takes about 3-4 minutes to finish rebooting and restarting all services.
SKU: ASK-SFE116
FCC ID: H8N-ASK-SFE116

Developed in the following environment, known to be working:
    * Verizon Network Extender software version: GA5.11 - V0.5.011.1322
    * macOS 13.3 (Ventura)
    * Python 3.9.6
    * Selenium 4.8.3

Docker images hosted here:
   https://hub.docker.com/repository/docker/themolecularman/verizon-lte-extender-reboot/

Can be deployed in a Docker container using the Dockerfile.

Run the ./build_docker.sh script to build the Docker image. It is manually configured to build for the x86_64 (AMD64) architecture. Modify the top line in Dockerfile if you need to build it for other architectures.

How to deploy the Docker container:
 1) build the docker image yourself or check it out from DockerHub

```./build_docker.sh``` - build it yourself

```docker pull themolecularman/verizon-lte-extender-reboot``` - pull the image from Docker Hub

2) Create a new Docker container and specify the following environment variables:

```VERIZON_URL``` - URL (including HTTPS) for accessing the Verizon Extender's web interface. Ex: "https://192.168.1.108"

```VERIZON_PASSWORD``` - Password for Verizon exender
