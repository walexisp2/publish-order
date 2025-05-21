# -----------------------------------------------------------------#
# Instalación de Ubuntu                                            #
# -----------------------------------------------------------------#
FROM ubuntu:18.04 as base

# -----------------------------------------------------------------#
# Instalación de IBM MQ                                            #
# -----------------------------------------------------------------#
# The URL to download the MQ installer from in tar.gz format
# This URL will change for a corporate repository
ARG MQ_URL=https://www.dropbox.com/s/ag0wqdtaitgvir6/9.1.0.4-IBM-MQC-LinuxX64.tar.gz?dl=1

RUN export DEBIAN_FRONTEND=noninteractive \
  # Install additional packages required by MQ, this install process and the runtime scripts
  && apt-get update -y \
  && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
  # Download and extract the MQ installation files
  && export DIR_EXTRACT=/tmp/mq \
  && mkdir -p ${DIR_EXTRACT} \
  && cd ${DIR_EXTRACT} \
  && curl -LO $MQ_URL \
  # Fix a name change in the downloaded file
  # It may not be necessary with the corporate repository
  && mv 9.1.0.4-IBM-MQC-LinuxX64.tar.gz?dl=1 9.1.0.4-IBM-MQC-LinuxX64.tar.gz \
  && tar -zxvf ./*.tar.gz \
  # Recommended: Remove packages only needed by this script
  && apt-get purge -y \
    curl \
    ca-certificates \
  # Recommended: Remove any orphaned packages
  && apt-get autoremove -y --purge \
  # Find location of mqlicense.sh
  && export MQLICENSE=$(find ${DIR_EXTRACT} -name "mqlicense.sh") \
  # Accept the MQ license
  && ${MQLICENSE} -text_only -accept \
  # Generate deb packages from rmp packages
  && apt-get install -y --no-install-recommends \
    alien \
  && alien MQSeriesRuntime-*.rpm \
  && alien MQSeriesClient-*.rpm \
  && alien MQSeriesSDK-*.rpm \
  # Recommended: Create the mqm user ID with a fixed UID and group, so that the file permissions work between different images
  && useradd mqm \
  # Install MQ using the deb packages
  && dpkg -i mqseriesruntime_*.deb \
  && dpkg -i mqseriesclient_*.deb \
  && dpkg -i mqseriessdk_*.deb \
  # Install pymqi library because from the requirements file it doesn't work
  && apt-get install -y --no-install-recommends \
    python3.7 \
    python3-pip \
    python3-setuptools \
    python3.7-dev \
  && python3.7 -m pip install pip --upgrade \
  && python3.7 -m pip install wheel \
  && python3.7 -m pip install pymqi \
  # Recommended: Remove packages only needed by this script
  && apt-get purge -y \
    alien \
  # Recommended: Remove any orphaned packages
  && apt-get autoremove -y --purge \
  # Remove 32-bit libraries from 64-bit container
  && find /opt/mqm -type f -exec file {} \; \
    | awk -F: '/ELF 32-bit/{print $1}' \
    | xargs --no-run-if-empty rm -f \
  # Remove tar.gz files unpacked by RPM postinst scripts
  && find /opt/mqm -name '*.tar.gz' -delete \
  # Clean up all the downloaded files
  && rm -rf ${DIR_EXTRACT} \
  # Apply any bug fixes not included in base Ubuntu or MQ image.
  # Don't upgrade everything based on Docker best practices https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#run
  && apt-get upgrade -y sensible-utils \
  # End of bug fixes
  && rm -rf /var/lib/apt/lists/*

# Environment Variable Instance with MQ Component Installation Path
ENV LD_LIBRARY_PATH /opt/mqm/lib64/:${LD_LIBRARY_PATH}

# -----------------------------------------------------------------#
# Configuración del proyecto                                       #
# -----------------------------------------------------------------#

COPY _#{Build.Repository.Name}#/Artifact-#{Build.Repository.Name}#/ /app/project
WORKDIR /app/project

# -----------------------------------------------------------------#
# Instalación de pip y librerías requeridas                        #
# -----------------------------------------------------------------#
RUN pip install --upgrade pip
COPY pip.conf pip.conf
ENV PIP_CONFIG_FILE pip.conf
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

CMD ["python3.7","main.py"]