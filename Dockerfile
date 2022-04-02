FROM python:3.8

ENV LANG C.UTF-8
ENV APP_HOME /usr/src/app/
WORKDIR $APP_HOME

RUN apt-get update -y 

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.dev.txt requirements.dev.txt
RUN pip install --no-cache-dir -r requirements.dev.txt

# Create a new user
RUN useradd --create-home appuser
USER appuser

# Copy our app over to the image
COPY ./ $APP_HOME

CMD ["bash"]
