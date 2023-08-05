# vim:set ft=dockerfile:
FROM ${image_name}:${image_version}
MAINTAINER ${maintainer}

LABEL Description="${description}" Vendor="${vendor}" Version="${version}"

# Configure hostname and user for services 
%for key,value in environment.items():
ENV ${key} ${value}
% endfor 

% if image_name.lower() in ['centos', 'fedora']:
# Setup sudo
RUN yum install -y sudo
# Don't require terminal when using sudo with root
RUN echo 'Defaults:root !requiretty' > /etc/sudoers.d/999-birdhouse
% endif

# Set current home
ENV HOME /root

% if git_url:
# Load sources from github
RUN mkdir -p /opt/birdhouse && curl -ksL ${git_url}/archive/${git_branch}.tar.gz | tar -xzC /opt/birdhouse --strip-components=1
% else:
# Copy application sources
COPY ${source} /opt/birdhouse
% endif

% if subdir:
WORKDIR /opt/birdhouse/${subdir}
% else:
# cd into application
WORKDIR /opt/birdhouse
% endif

% if buildout_cfg:
# Overwrite buildout.cfg in source folder
COPY ${buildout_cfg} buildout.cfg
% endif

# Provide custom.cfg with settings for docker image
COPY .docker.cfg custom.cfg

# Install system dependencies
RUN bash bootstrap.sh -i && bash requirements.sh

# Set conda enviroment
ENV ANACONDA_HOME /opt/conda
ENV CONDA_ENVS_DIR /opt/conda/envs

# Run install
RUN make clean install 

# Volume for data, cache, logfiles, ...
RUN chown -R $USER $CONDA_ENVS_DIR/birdhouse
RUN mkdir -p $CONDA_ENVS_DIR/birdhouse/var/lib && mv $CONDA_ENVS_DIR/birdhouse/var/lib /data && ln -s /data $CONDA_ENVS_DIR/birdhouse/var/lib
RUN chown -R $USER /data
VOLUME /data

% if expose:
# Ports used in birdhouse
EXPOSE ${expose}
% endif

# Start supervisor in foreground
ENV DAEMON_OPTS --nodaemon --user $USER

# Start service ...
CMD ${command}

