FROM alpine
RUN apk add g++
COPY . /code
WORKDIR /code
RUN g++ -o /code/message_writer message_writer.cxx
