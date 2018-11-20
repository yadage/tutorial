FROM alpine
RUN apk add build-base
COPY . /code
WORKDIR /code
RUN g++ -o /code/message_writer message_writer.cxx
