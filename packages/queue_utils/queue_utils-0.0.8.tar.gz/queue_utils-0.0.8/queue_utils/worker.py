import datetime
import queue_utils.logger
from six import string_types


def isstr(what):
    return isinstance(what, string_types)


class Worker(queue_utils.logger.Logable):

    """
    A Worker is connected to a bidirectional channel, listening on the input
    port, processing the message recieved, and sending the output to the output
    port. This allows a Worker to act as both a consumer and a producer when
    used with queueing paradigms.
    """

    def __init__(self, channel, work_method, payload_check=None, id=None):
        """
        channel: A bi-directional connection with a defined input and output.
        work_method: A hook which is used to process the message payload
                     after some initial checks have been performed.
        payload_check: A hook that can be used to check the validity of a
                       message payload.
        """
        queue_utils.logger.Logable.__init__(self, __name__, id)
        self._id = id

        self.info("Creating worker with channel %s" % channel)

        self._channel = channel
        self._work_method = work_method
        self._payload_check = payload_check

    def start(self):
        """
        Start the worker as a consumer of the input port. The method get_work
        is registered as a callback for processing incomming messages.
        """
        self.info("Starting worker")
        self._channel.listen_on_input(self.get_work)

    def get_work(self, ch, method, properties, payload):
        """
        A callback wich is used for processing incomming messages. Basic error
        checks are performed, before calling the work hook registered at
        construction.
        """

        time_in = datetime.datetime.now()

        try:
            payload_text = payload.keys()
        except:
            payload_text = payload[:min(20, len(payload))]
        self.info("Processing work unit with payload keys: %s" %
                  payload_text)

        # Simply forward an existing error.
        if "error" in payload:
            if payload["error"]:
                self.error(
                    "Forwarding error: %s" % payload["error"])
                self.send(time_in, payload)
                self.acknowledge(method)
                return

        # Check if the payload is valid.
        is_valid, error = self.is_valid_payload(payload)
        if not is_valid:
            if isstr(payload):
                payload = {'payload': payload}

            if "error" not in payload:
                payload["error"] = {}

            payload["error"][self._id] = error
            self.send(time_in, payload)
            self.acknowledge(method, True)
            return

        # Get the results of the worker.
        results, error = self.do_work(payload)

        # Send the results.
        self.send(time_in, results)

        # Only acknowledge the receipt of the message if there were no errors.
        if not error:
            self.acknowledge(method)

        self.info("Done processing work unit")

    def is_valid_payload(self, payload):
        """
        Check if the specified payload is valid. All payloads are considered
        valid by defaults, but a validity check can be included during
        construction.
        """
        # Checking if the payload is valid.
        self.info("Checking for valid payload")

        is_valid = True
        error = None

        if self._payload_check is None:
            return is_valid, error

        return self._payload_check(payload)

    def do_work(self, payload):
        """
        Call the work hook specified at construction.
        """
        self.info("Doing work")

        results, error = self._work_method(payload)

        return results, error

    def send(self, timestamp, payload):
        """
        Send the payload to the output port of the channel with which the
        worker is associated.
        """
        self.info("Sending payload")

        time_in = str(timestamp)
        time_out = str(datetime.datetime.now())

        if not isstr(payload):
            if 'trace' not in payload:
                payload['trace'] = []

            payload['trace'].append([self._id, time_in, time_out])

        self._channel.send_to_output(payload)

    def acknowledge(self, method, is_nack=False):
        """
        Acknowledge the processing on the input.
        """
        self.info("Sending acknowledgement (is_nack=%s)" % is_nack)

        if method is None:
            delivery_tag = None
        else:
            delivery_tag = method.delivery_tag
        self._channel.acknowlege_input(delivery_tag, is_nack)
