# mindwave-python

Linux and Mac-friendly Python parser to connect and interact with multiple NeuroSky MindWave headsets from one machine.

Based on code from Moonshot Lab at Barkley (https://github.com/BarkleyUS/mindwave-python). I added a new class to read and parse data from the ThinkGears Connector (TGC).

## Basic Usage

A connection to the headset is established by creating a new `Headset` object.

### TGC Connection

Make sure the [TGC](http://developer.neurosky.com/docs/doku.php?id=thinkgear_connector_tgc) is running and your headet has been paired.

    import mindwave_tgc

    headset = mindwave.Headset()

This automatically starts the data-reading and parsing thread. To disconnect and stop the thread:

    headset.disconnect()

### Serial Connection

Find the MindWave device(s) on your machine. On a Mac, it looks like this:

    import mindwave_serial

    headset = mindwave.Headset('/dev/tty.MindWave', '625f')

Pass in the device path and the headset ID printed inside the battery case.

It's recommended to wait at least a couple seconds before connecting the dongle to the headset:

    import mindwave, time

    headset = mindwave.Headset('/dev/tty.MindWave', '625f')
    time.sleep(2)

    headset.connect()
    print "Connecting..."

    while headset.status != 'connected':
        time.sleep(0.5)
        if headset.status == 'standby':
            headset.connect()
            print "Retrying connect..."
    print "Connected."

    while True:
        print "Attention: %s, Meditation: %s" % (headset.attention, headset.meditation)

For the MindWave Mobile bluetooth headsets, it's unnecessary to use the `connect()` or `disconnect()` methods. If your operating system automatically creates a serial port for the bluetooth device, there's also no need to specify a headset ID. Just pass the serial device path as a parameter when you create a new `Headset` object and you're good to go.

#### Auto-connect

The library can also auto-connect the dongle to the first available headset, rather than specifying a headset ID.

    import mindwave, time

    headset = mindwave.Headset('/dev/tty.MindWave')
    time.sleep(2)
    headset.connect()

Use `headset.autoconnect()` to auto-connect explicitly, regardless of whether or not a headset ID was specified.


##### Multiple headsets

The library can handle multiple devices used simultaneously.

    import mindwave, time

    h1 = mindwave.Headset('/dev/tty.MindWave', '625f')
    h2 = mindwave.Headset('/dev/tty.MindWave2', 'a662')
    time.sleep(2)

    h1.connect()
    print "Connecting h1..."
    while h1.status != 'connected':
        time.sleep(0.5)
        if h1.status == 'standby':
            h1.connect()
            print "Retrying connect..."
    print "Connected h1."

    h2.connect()
    print "Connecting h2..."
    while h2.status != 'connected':
        time.sleep(0.5)
        if h2.status == 'standby':
            h2.connect()
            print "Retrying connect..."
    print "Connected h2."

    while True:
        print "Attention 1: %s, Meditation 1: %s" % (h1.attention, h1.meditation)
        print "Attention 2: %s, Meditation 2: %s" % (h2.attention, h2.meditation)


## Adding event handlers

The library provides hooks for certain events to allow for the attachment of custom handlers.

    def on_blink(headset, blink_strength):
        print "Blink detected. Strength: %s" % blink_strength

    headset.blink_handlers.append(on_blink)


# API

## Available properties

`headset.` **device** - The device path of the dongle on the system. (serial only)

`headset.` **headset_id** - The ID of the connected headset. (serial only)

`headset.` **poor_signal** - The "poor signal" reading of the headset connection. This indicates how poorly the headset is reading EEG waves, 0 being the best reading and 255 being the worst. Try readjusting the headset if this value is too high.

`headset.` **attention** - The last-read attention value from the headset.

`headset.` **meditation** - The last-read meditation value from the headset.

`headset.` **blink** - The last-read blink strength from the headset.

`headset.` **power** - A dict with the 8 power bands last-read from the headset. (tgc only)

`headset.` **effort** - The last-read effort value from the headset. (tgc only, not available for all devices)

`headset.` **familiarity** - The last-read familiarity value from the headset. (tgc only, not available for all devices)

`headset.` **raw_multi_value** - A dict with the multi-channel raw values last-read from the headset. (tgc only, not available for all devices)

`headset.` **status** - The current status of the headset: `connected`, `scanning`, or `standby` (serial only)


## Available methods

`headset.` **connect** `([headset_id])` - Connect to the specified headset ID. If no headset was specified, the dongle will auto-connect to the first available. (serial)

`headset.` **connect** `()` - Connect to the headset. (tgc)

`headset.` **autoconnect** `()` - Auto-connect to the first available headset, regardless of any headset ID specified. (serial only)

`headset.` **disconnect** `()` - Disconnect from the headset.


## Event hooks

`headset.` **poor_signal_handlers** `[]` - Handlers are fired whenever a poor signal is detected. Expects handlers with the prototype `my_function(headset, poor_signal)` and passes in the current headset object and poor signal value.

`headset.` **good_signal_handlers** `[]` - Handlers are fired whenever a good signal is detected. Expects handlers with the prototype `my_function(headset, poor_signal)` and passes in the current headset object and poor signal value.

`headset.` **attention_handlers** `[]` - Handlers are fired whenever an attention value is received. Expects handlers with the prototype `my_function(headset, attention)` and passes in the current headset object and attention value.

`headset.` **meditation_handlers** `[]` - Handlers are fired whenever an meditation value is received. Expects handlers with the prototype `my_function(headset, meditation)` and passes in the current headset object and meditation value.

`headset.` **blink_handlers** `[]` - Handlers are fired whenever a blink is detected. Expects handlers with the prototype `my_function(headset, blink_strength)` and passes in the current headset object and blink strength value.

`headset.` **connected_handlers** `[]` - Handlers are fired whenever the headset is connected. Expects handlers with the prototype `my_function(headset)` and passes in the current headset object. (serial only)

`headset.` **notfound_handlers** `[]` - Handlers are fired whenever the headset specified cannot be found. Expects handlers with the prototype `my_function(headset, not_found_id)` and passes in the current headset object and the headset id that could not be found. (serial only)

`headset.` **disconnected_handlers** `[]` - Handlers are fired whenever the headset is disconnected. Expects handlers with the prototype `my_function(headset)` and passes in the current headset object. (serial only)

`headset.` **request_denied_handlers** `[]` - Handlers are fired whenever a request to the dongle is denied (connect/disconnect/autoconnect). Expects handlers with the prototype `my_function(headset)` and passes in the current headset object. (serial only)

`headset.` **scanning_handlers** `[]` - Handlers are fired whenever the dongle begins scanning for a headset. Expects handlers with the prototype `my_function(headset)` and passes in the current headset object. (serial only)

`headset.` **standby_handlers** `[]` - Handlers are fired whenever the dongle goes into standby (not connected to a headset). Expects handlers with the prototype `my_function(headset)` and passes in the current headset object. (serial only)

