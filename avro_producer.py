import argparse
import os
from uuid import uuid4

from six.moves import input

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import time


def main(args):
    topic = args.topic
    is_specific = args.specific == "true"

    if is_specific:
        schema = "user_specific.avsc"
    else:
        schema = "user_generic.avsc"

    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/{schema}") as f:
        schema_str = f.read()

    schema_registry_conf = {'url': args.schema_registry}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    # avro_conf = {
            # 'use.latest.version': False,
            # 'auto.register.schemas': True,
            # 'normalize.schemas': True,
            # }
    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str,
                                     # conf=avro_conf
                                     )

    string_serializer = StringSerializer('utf_8')

    producer_conf = {'bootstrap.servers': args.bootstrap_servers}

    producer = Producer(producer_conf)
    myuser = {
            "name2": "Arsenii",
            "favorite_number": 25,
            "favorite_color": "blue",
            }

    print("Producing user records to topic {}. ^C to exit.".format(topic))
    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        try:
            producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             value=avro_serializer(myuser, SerializationContext(topic, MessageField.VALUE))
                             )
            time.sleep(int(args.timeout))
        except KeyboardInterrupt:
            break

    print("\nFlushing records...")
    producer.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AvroSerializer example")
    parser.add_argument('-b', dest="bootstrap_servers", required=True,
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry", required=True,
                        help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="example_serde_avro",
                        help="Topic name")
    parser.add_argument('-p', dest="specific", default="true",
                        help="Avro specific record")
    parser.add_argument('--timeout', dest="timeout", default=1,
                        help="Timeout between messages")

    main(parser.parse_args())
