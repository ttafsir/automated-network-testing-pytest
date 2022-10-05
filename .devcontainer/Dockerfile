FROM python:3.9-slim-buster AS base-image

# ensure virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements files for Python and Ansible
COPY requirements-all.txt requirements.txt
COPY requirements.yml requirements.yml

# Install Python and Ansible requirements
RUN pip install -r requirements.txt
RUN ansible-galaxy install -r requirements.yml

# copy artifacts from base image build the runtime image
FROM python:3.9-slim-buster AS build-image
COPY --from=base-image /opt/venv /opt/venv
COPY --from=base-image /root/.ansible /root/.ansible

ENV PROJECTS_DIR /projects
WORKDIR /projects

# Do not generate .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turn off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Ansible configuration
ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV ANSIBLE_RETRY_FILES_ENABLED=False
ENV ANSIBLE_SSH_PIPELINING=True
ENV TERM='xterm-256color'

# install system package
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get -y install --no-install-recommends \
    git \
    wget \
    make \
    wget \
    curl \
    iputils-ping \
    ssh && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Install ZSH
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -t https://github.com/denysdovhan/spaceship-prompt \
    -a 'SPACESHIP_PROMPT_ADD_NEWLINE="false"' \
    -a 'SPACESHIP_PROMPT_SEPARATE_LINE="false"' \
    -p git \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions \
    -p https://github.com/zsh-users/zsh-syntax-highlighting

# ensure virtualenv
ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["/bin/zsh"]
