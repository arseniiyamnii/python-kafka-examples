FROM python:3.9.18 as scratch
ARG KAFKA_BOOTSTRAP=127.0.0.1:9092
ARG SCHEMA_REGISTRY=http://127.0.0.1:8081
ARG TOPIC=my-topic
ARG SPECIFIC=true
COPY requirements.txt /scripts/
WORKDIR /scripts
RUN pip3 install -r requirements.txt

COPY avro_producer.py /scripts/
COPY avro_consumer.py /scripts/
COPY ./avro /scripts/avro/

FROM scratch as producer
CMD python avro_producer.py -b $KAFKA_BOOTSTRAP -s $SCHEMA_REGISTRY -t $TOPIC -p $SPECIFIC --timeout 1

FROM scratch as consumer
ARG GROUP=my-group
CMD python avro_consumer.py -b $KAFKA_BOOTSTRAP -s $SCHEMA_REGISTRY -t $TOPIC -g $GROUP -p $SPECIFIC
