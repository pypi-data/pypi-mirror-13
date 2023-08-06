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
                self.info(
                    "Forwarding error: %s" % payload["error"])
                self.send(time_in, payload)
                self.acknowledge(ch, method)
                return

        # Check if the payload is valid.
        is_valid, error = self.is_valid_payload(payload)
        if not is_valid:
            self.error("The specified payload is invalid")
            self.forward_error(ch, method, payload, time_in, error)
            return

        # Do the work.
        results, error = self.do_work(payload)
        if error is not None:
            self.error("An error occurred when doing work")
            self.forward_error(ch, method, results, time_in, error)
            return

        # Send the results.
        send_error = self.send(time_in, results)

        # Only acknowledge the receipt of the message if the (processed) result
        # was sent successfully.
        if send_error is None:
            self.acknowledge(ch, method)
        else:
            self.info("Not sending acknowledgement")
            self.info("send_error=%s" % send_error)

        self.info("Done processing work unit")

    def forward_error(self, ch, method, payload, time_in, error):
        self.error(str(error))
        payload = self.add_error(payload, error)
        self.send(time_in, payload)
        self.acknowledge(ch, method, True)

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

        results, errors = self._work_method(payload)

        return results, errors

    def send(self, timestamp, payload):
        """
        Send the payload to the output port of the channel with which the
        worker is associated.
        """
        if not self.is_producer():
            self.info("Only a producer can send. Skipping")
            return None

        self.info("Sending payload")
        try:
            payload = self.update_trace(timestamp, payload)
            send_error = self._output.send_to_output(payload)
        except Exception as e:
            self.error("Error sending payload")
            self.error(e)
            return e

        return send_error

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

        if not isstr(payload):
            if 'trace' not in payload:
                payload['trace'] = []
            payload['trace'].append(self._id)

        trace = [time_in, time_out]
        return self.add_field(payload, 'trace_timestamps', trace)

    def add_error(self, payload, error):
        """
        Add the specified error to the payload.
        """
        if error is None:
            return payload

        return self.add_field(payload, 'error', error)

    def check_field(self, payload, field):
        """
        Check if a field exists, and create it if required.
        """
        if isstr(payload):
            self.info("Cannot add %s to string payload" % field)
            return payload

        if field not in payload:
            self.info("Creating %s in payload" % field)
            payload[field] = {}

        if self._id not in payload[field]:
            self.info("Creating %s in payload[%s]" % (self._id, field))
            payload[field][self._id] = []

        return payload

    def add_field(self, payload, field, value):
        self.info("Adding %s=%s to payload" % (field, value))

        if isstr(payload):
            self.info("Cannot add %s to string payload" % field)
            return payload

        payload = self.check_field(payload, field)
        payload[field][self._id].append(value)

        return payload
