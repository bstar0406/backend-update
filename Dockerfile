FROM    python:3.9.10-slim-buster

#Installing the dependencies
RUN     apt-get update && \
        apt-get install -y  gcc make \
                            --no-install-recommends apt-utils build-essential net-tools \
                            build-essential libssl-dev libffi-dev python3-dev \
                            g++ unixodbc-dev \
                            curl \
                            gnupg

#Download the desired package(s) for SQL SERVER DRIVER 17
RUN     apt-get update && \
        apt-get install -y apt-transport-https && \
        curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
        curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
        apt-get update && \
        ACCEPT_EULA=Y apt-get install msodbcsql17 unixodbc-dev -y


#Setting python env
ENV     PYTHONDONTWRITEBYECODE=1
ENV     PYTHONNUNBUFFERED=1

#Build client library
WORKDIR /pac_new_backend
COPY    requirements.txt /pac_new_backend/
COPY    .env /pac_new_backend/
RUN     python -m pip install --upgrade pip setuptools wheel source
RUN     pip install -r requirements.txt

#Transfer project files into container image
COPY    . /pac_new_backend/