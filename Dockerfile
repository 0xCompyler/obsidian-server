FROM python:3.8
# Run commands from /app directory inside container
WORKDIR /app
# Copy requirements from local to docker image
COPY requirements.txt /app
# Install the dependencies in the docker image
RUN pip3 install -r requirements.txt --no-cache-dir && python -m nltk.downloader stopwords
# Copy everything from the current dir to the image
COPY . .
EXPOSE 8000