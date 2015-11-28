import socket, json, threading, time


class Headset(object):
    """
    A MindWave Headset
    """

    class TgcListener(threading.Thread):
        """
        Listener for ThinkGears Connector (tgc).
        """
        def __init__(self, headset, *args, **kwargs):
            """Set up the listener device."""
            self.headset = headset
            self.running = True
            super(Headset.TgcListener, self).__init__(*args, **kwargs)

        def stop(self):
            self.running = False

        def run(self):
            """Run the listener thread."""
            s = self.headset.sock
            buf = []
            frag = ''
            pack_size = 1024
            while self.running:
                # Begin listening for packets
                #try:
                raw_str = frag + s.recv(pack_size)
                chunks = raw_str.split('\r')
                if len(chunks)>0:
                    frag = chunks.pop()
                    for c in chunks:
                        try:
                            self.parse_payload(c)
                        except:
                            print(c)

        def parse_payload(self, payload):
            """Parse the payload to determine an action."""
            d = json.loads(payload)
            for code,value in d.iteritems():
                if code == u'poorSignalLevel':
                    # Poor signal
                    old_poor_signal = self.headset.poor_signal
                    self.headset.poor_signal = value
                    if self.headset.poor_signal > 0:
                        if old_poor_signal == 0:
                            for handler in self.headset.poor_signal_handlers:
                                handler(self.headset, self.headset.poor_signal)
                    else:
                        if old_poor_signal > 0:
                            for handler in self.headset.good_signal_handlers:
                                handler(self.headset, self.headset.poor_signal)
                elif code == u'eSense':
                    self.headset.attention = value[u'attention']
                    self.headset.meditation = value[u'meditation']
                    for handler in self.headset.esense_handlers:
                        handler(self.headset, self.headset.attention, self.headset.meditation)
                elif code == u'eegPower':
                    # eegPower is kept in a dict
                    self.headset.power = value
                    for handler in self.headset.power_handlers:
                        handler(self.headset, self.headset.power)
                elif code == u'blinkStrength':
                    self.headset.blink = value
                    for handler in self.headset.blink_handlers:
                        handler(self.headset, self.headset.blink)
                elif code == u'mentalEffort':
                    self.headset.effort = value
                    for handler in self.headset.effort_handlers:
                        handler(self.headset, self.headset.effort)
                elif code == u'familiarity':
                    self.headset.familiarity = value
                    for handler in self.headset.familiarity_handlers:
                        handler(self.headset, self.headset.familiarity)
                elif code == u'rawEeg':
                    self.headset.raw_value = value
                    for handler in self.headset.raw_value_handlers:
                        handler(self.headset, self.headset.raw_value)
                elif code == u'rawEegMulti':
                    # multi-channel is kept in a dict
                    self.headset.raw_multi_value = value
                    for handler in self.headset.raw_multi_value_handlers:
                        handler(self.headset, self.headset.raw_multi_value)


    def __init__(self, host='127.0.0.1', port=13854, connect=True):
        """Initialize the  headset."""
        # Initialize headset values
        self.sock = None
        self.listener = None
        self.host = host
        self.port = port
        self.poor_signal = 255
        self.attention = 0
        self.meditation = 0
        self.power = {}
        self.effort = 0
        self.familiarity = 0
        self.blink = 0
        self.raw_value = 0
        self.raw_multi_value = {}
        self.status = None

        # Create event handler lists
        self.poor_signal_handlers = []
        self.good_signal_handlers = []
        self.esense_handlers = []
        self.power_handlers = []
        self.effort_handlers = []
        self.familiarity_handlers = []
        self.blink_handlers = []
        self.raw_value_handlers = []
        self.raw_multi_value_handlers = []

        # Open the socket
        if connect:
            self.connect()

    def connect(self):
        """Connect to the TGC."""
        if self.sock != None:
            self.disconnect()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        time.sleep(10)
        #s.sendall('{"appName":"MyApp", "appKey":"'+key+'"}')
        self.sock.sendall('{"enableRawOutput":true,"format":"Json"}')
        # Begin listening
        if not self.listener or not self.listener.isAlive():
            self.listener = self.TgcListener(self)
            self.listener.daemon = True
            self.listener.start()

    def disconnect(self):
        """Disconnect the device from the headset."""
        self.listener.stop()
        self.sock.close()
        self.sock = None

