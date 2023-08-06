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

    def __init__(self, id, input, output, work_method, payload_check=None):
        """
        channel: A bi-directional connection with a defined input and output.
        work_method: A hook which is used to process the message payload
                     after some initial checks have been performed.
        payload_check: A hook that can be used to check the validity of a
                       message payload.
        """
        queue_utils.logger.Logable.__init__(self, __name__, id)
        self._id = id

        self._input = input
        self._output = output

        self.info("Creating worker %s" % str(self))

        self._work_method = work_method
        self._payload_check = payload_check

    def __str__(self):
        s = '%s:' % self._id
        if self._input:
            s = s + 'Consume(%s)' % self._input
        if self._output:
            s = s + 'Produce(%s)' % self._output

        return s

    def is_consumer(self):
        return self._input is not None

    def is_producer(self):
        return self._output is not None

    def start_consuming(self):
        """
        Start the worker as a consumer of the input port. The method get_work
        is registered as a callback for processing incomming messages.
        """
        self.info("Starting worker")
        self._input.listen_on_input(self.get_work)

    def get_work(self, ch, method, properties, payload):
        """
        A callback wich is used for processing incomming messages. Basic error
        checks are performed, before calling the work hook registered at
        construction.
        """

        time_in = datetime.datetime.now()

        try:
            payload_desc = 'payload keys'
            payload_text = payload.keys()
        except:
            payload_desc = 'payload'
            payload_text = payload[:min(20, len(payload))]
        self.info("Processing work unit with %s: %s" %
                  (payload_desc, payload_text))

        # Simply forward an existing error.
        if "error" in payload:
            if payload["error"]:
                self.error(
                    "Forwarding error: %s" % payload["error"])
                self.send(time_in, payload)
                self.acknowledge(ch, method)
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
            self.acknowledge(ch, method, True)
            return

        # Get the results of the worker.
        results, error = self.do_work(payload)

        # Send the results.
        self.send(time_in, results)

        # Only acknowledge the receipt of the message if there were no errors.
        if not error:
            self.acknowledge(ch, method)

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
        if not self.is_producer():
            self.error("Only a producer can send")
            return False

        self.info("Sending payload")

        payload, trace = self.update_trace(timestamp, payload)

        self._output.send_to_output(payload)

        return True

    def acknowledge(self, channel, method, is_nack=False):
        """
        Acknowledge the processing on the input.
        """
        self.info("Sending acknowledgement (is_nack=%s)" % is_nack)

        if method is None:
            delivery_tag = None
        else:
            delivery_tag = method.delivery_tag
        self._input.acknowlege_input(channel, delivery_tag, is_nack)

    def update_trace(self, timestamp, payload):
        """
        Add the trace info to the payload.
        """
        time_in = str(timestamp)
        time_out = str(datetime.datetime.now())

        trace = [self._id, time_in, time_out]
        try:
            if 'trace' not in payload:
                payload['trace'] = []

            payload['trace'].append(trace)
            trace = payload['trace']
        except:
            pass

        return payload, trace
