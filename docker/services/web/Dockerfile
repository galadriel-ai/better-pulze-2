FROM continuumio/miniconda3:23.3.1-0

RUN apt-get update && apt-get install -y gcc logrotate g++ libtidy-dev git libmagic1 tesseract-ocr

ADD requirements.txt /
RUN pip install -r requirements.txt

# Logrotate
COPY docker/logrotate_app_logs /etc/logrotate.d/log-file
RUN chmod 644 /etc/logrotate.d/log-file

# Create new user to not run in sudo mode
RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY . /home/appuser

RUN mkdir -p /root/.ssh
RUN echo "StrictHostKeyChecking no" >> /root/.ssh/config
