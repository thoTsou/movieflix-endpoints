FROM ubuntu:16.04
MAINTAINER THOTSOU <e17155@unipi.gr>
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install flask pymongo
RUN mkdir /app
COPY movieFlix_e17155.py /app/movieFlix_e17155.py
EXPOSE 5000
WORKDIR /app
ENTRYPOINT [ "python3","-u", "movieFlix_e17155.py" ]
