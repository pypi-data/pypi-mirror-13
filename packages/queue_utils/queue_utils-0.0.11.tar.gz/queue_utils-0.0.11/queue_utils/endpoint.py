import pika
import json
import queue_utils.logger

# TODO: See the example at:
# http://pika.readthedocs.org/en/latest/examples/asynchronous_consumer_example.html
# This queue implementation could be expanded.


class Endpoint(queue_utils.logger.Logable):

    """
    An Endpoint defines a connection to be used by a worker acting as either a
    producer, a consumer, or both.
    """

    def __init__(self, id, decode, encode):
        """
        id: The id to be used for the endpoint port
        decode: A method to be used to decode incomming messages
        encode: A method to be used to encode outgoing messages
        """

        queue_utils.logger.Logable.__init__(self, id)

        self.name = id
        # Set encoding/decoding scheme.
        self.decode = decode
        self.encode = encode

    def __str__(self):
        return str(self.name)

    def listen_on_input(self, func):
        raise NotImplementedError

    def send_to_output(self, payload):
        raise NotImplementedError

    def acknowlege_input(self, channel, delivery_tag, is_nack):
        raise NotImplementedError


class RabbitMQQueue(Endpoint):

    """
    An endpoint defined by a RabbitMQ Queue channel.
    """

    def __init__(self,
                 url,
                 exchange,
                 queue_name,
                 decode=json.loads,
                 encode=json.dumps):
        """
        url: The URL used to identify the remote RabbitMQ server.
        """

        Endpoint.__init__(self, queue_name, decode, encode)

        self._params = pika.URLParameters(url)
        self._params.socket_timeout = 5

        channel = self.get_channel("Construction")

        # Declare the exchange.
        self._exchange = exchange
        channel.exchange_declare(exchange=exchange,
                                 durable=True,
                                 exchange_type='direct')

        # Store some send properties.
        # Use delivery_mode=2 to ensure delivery.
        self._send_properties = pika.BasicProperties(delivery_mode=2)

        # Close the connection to the server.
        channel.connection.close()

    def get_channel(self, reason):
        """
        Open a connection and get a channel as defined by the parameters.
        """
        self.info("Creating channel: %s" % reason)
        connection = pika.BlockingConnection(self._params)
        channel = connection.channel()

        return channel

    def create_queue(self, channel, queue_name):
        self.info("Creating queue for %s" % queue_name)

        # Declare the required queue as durable.
        channel.queue_declare(queue=queue_name, durable=True)

        # Bind the queue to the exchange. Use the queue_name as the routing
        # key.
        channel.queue_bind(exchange=self._exchange,
                           queue=queue_name,
                           routing_key=queue_name)

    def listen_on_input(self, func):
        """
        Listen on the endpoint, calling the specified function if something is
        received.
        """

        def decode_func(ch, method, properties, payload):
            try:
                func(ch, method, properties, self.decode(payload))
            except Exception as e:
                self.error("Error decoding payload. Forwarding")
                self.error("%s:%s" % (type(e), e))
                func(ch, method, properties, payload)

        # Get a connection to the queue
        channel = self.get_channel("Listening")

        # Ensure that the input queue exists.
        self.create_queue(channel, self.name)

        # Set the quality of service properties.
        channel.basic_qos(prefetch_count=1)

        # Install the channel handler.
        channel.basic_consume(decode_func, queue=self.name)
        # Start listening on the channel.
        channel.start_consuming()

        self.info("Closing the connection")
        channel.connection.close()

    def send_to_output(self, payload):
        """
        Send the payload on the queue.
        """
        # Get a connection to the queue
        channel = self.get_channel("Sending")

        self.create_queue(channel, self.name)

        channel.basic_publish(exchange=self._exchange,
                              routing_key=self.name,
                              body=self.encode(payload),
                              properties=self._send_properties)
        channel.connection.close()

    def acknowlege_input(self, channel, delivery_tag, is_nack):
        """
        Acknowlege the receipt of a message.
        """
        ack = 'ack'
        if is_nack:
            # Check if nack is supported.
            if channel.connection.basic_nack_supported:
                ack = 'nack'
            else:
                self.info("nack is not implemented for this connection. \
                           Using ack instead.")
                is_nack = False

        self.info("Sending %s for delivery_tag %s" % (ack, str(delivery_tag)))
        if is_nack:
            channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
        else:
            channel.basic_ack(delivery_tag=delivery_tag)


class InputOutputEndpoint(Endpoint):

    """
    A basic enpoint that can be used for testing.
    """

    def __init__(self):
        Endpoint.__init__(self, "output", None, None)
        self._func = None
        self._results = []
        self._acks = []

    def listen_on_input(self, func):
        self._func = func

    def send_to_output(self, payload):
        self._results.append(payload)

    def acknowlege_input(self, channel, delivery_tag, is_nack):
        self._acks.append((delivery_tag, not is_nack))

    # Utility functions for testing.
    def push(self, payload, channel=None, method=None, properties=None):
        self._func(channel, method, properties, payload)

    def pull(self):
        return self._results
