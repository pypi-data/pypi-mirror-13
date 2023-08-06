import pika
import json
import queue_utils.logger

# TODO: See the example at:
# http://pika.readthedocs.org/en/latest/examples/asynchronous_consumer_example.html
# This queue implementation could be expanded.


class Endpoint(queue_utils.logger.Logable):

    """
    An Endpoint defines a bidirectional connection to be used by a worker
    acting as either a producer, a consumer, or both.
    """

    def __init__(self, input_id, output_id, decode, encode):
        """
        input_id: The id to be used for the input port
        output_id: The id to be used for the ouput port
        decode: A method to be used to decode incomming messages
        encode: A method to be used to encode outgoing messages
        """

        id = '%s=>%s' % (input_id, output_id)

        queue_utils.logger.Logable.__init__(self, __name__, id)

        self._id = id
        self.input_id = input_id
        self.output_id = output_id

        # Set encoding/decoding scheme.
        self.decode = decode
        self.encode = encode

    def __str__(self):
        return str(self._id)

    def listen_on_input(self, func):
        raise NotImplementedError

    def send_to_output(self, payload):
        raise NotImplementedError

    def acknowlege_input(self, delivery_tag, is_nack):
        raise NotImplementedError


class RabbitMQQueue(Endpoint):

    """
    An endpoint defined by a RabbitMQ Queue channel.
    """

    def __init__(self,
                 url,
                 exchange,
                 input_id,
                 output_id,
                 encode=json.dumps,
                 decode=json.loads,
                 get_output_routing_key=None):
        """
        url: The URL used to identify the remote RabbitMQ server.
        """

        Endpoint.__init__(self, input_id, output_id, decode, encode)

        self._params = pika.URLParameters(url)
        self._params.socket_timeout = 5

        self._connection = pika.BlockingConnection(self._params)
        self._channel = self._connection.channel()

        # Declare the exchange.
        self._exchange = exchange
        self._channel.exchange_declare(exchange=exchange, type='direct')

        # Set the quality of service properties.
        self._channel.basic_qos(prefetch_count=1)

        # Store some send properties.
        self._send_properties = pika.BasicProperties(delivery_mode=2)

        if get_output_routing_key is None:
            self.get_output_routing_key = self._default_output_routing_key
        else:
            self.get_output_routing_key = get_output_routing_key

    def _create_queue_for_routing_key(self, routing_key):
        self.info("Creating queue for %s" % routing_key)

        # Declare the required queue
        self._channel.queue_declare(queue=routing_key, durable=True)
        # Bind the queue to the exchange.
        self._channel.queue_bind(exchange=self._exchange,
                                 queue=routing_key,
                                 routing_key=routing_key)

    def _default_output_routing_key(self, routing_key, payload):
        return routing_key

    def listen_on_input(self, func):
        """
        Listen on the endpoint, calling the specified function if something is
        received.
        """

        def json_func(ch, method, properties, payload):
            func(ch, method, properties, self.decode(payload))

        self._create_queue_for_routing_key(self.input_id)

        self.info("Start listening on queue %s" % self.input_id)
        # Install the channel handler.
        self._channel.basic_consume(json_func, queue=self.input_id)
        # Start listening on the channel.
        self._channel.start_consuming()

    def send_to_output(self, payload):
        """
        Send the payload on the queue.
        """
        r_key = self.get_output_routing_key(self.output_id, payload)
        self._create_queue_for_routing_key(r_key)

        self.info("Sending to %s" % r_key)

        result = self._channel.basic_publish(exchange=self._exchange,
                                             routing_key=r_key,
                                             body=self.encode(payload),
                                             properties=self._send_properties)

        self.info("result=%s" % result)

    def acknowlege_input(self, delivery_tag, is_nack):
        """
        Acknowlege the receipt of a message.
        """
        if is_nack:
            self.info("nack is not implemented")

        self._channel.basic_ack(delivery_tag=delivery_tag)

    def close(self):
        """
        Close the connection
        """
        self._connection.close()


class InputOutputEndpoint(Endpoint):

    """
    A basic enpoint that can be used for testing.
    """

    def __init__(self):
        Endpoint.__init__(self, "input", "output", None, None)
        self._func = None
        self._results = []
        self._acks = []

    def listen_on_input(self, func):
        self._func = func

    def send_to_output(self, payload):
        self._results.append(payload)

    def acknowlege_input(self, delivery_tag, is_nack):
        self._acks.append((delivery_tag, not is_nack))

    # Utility functions for testing.
    def push(self, payload, channel=None, method=None, properties=None):
        self._func(channel, method, properties, payload)

    def pull(self):
        return self._results
