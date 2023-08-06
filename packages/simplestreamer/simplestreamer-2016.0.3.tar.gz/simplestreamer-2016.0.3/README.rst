# simplestreamer

This is a tiny (< 150 loc) peer-to-peer data-streaming library designed for high-frequency status data.
It uses pickle underneath to serialize the data, so you can dump any python object through it.

You can install it with
``pip install simplestreamer``

Here is a quick example of how to use it. Hopefully it is self-explanatory enough.

node 1 code: ::

    # just dumps time data into the streamer at 100 hz
    import simplestreamer
    import time

    streamer = simplestreamer.SimpleStreamer(5200)

    while True:
        streamer.send_data({"current time.time()": time.time()})
        time.sleep(0.01)


node 2 (and 3, and 4, and so on) code: ::

    # subscribes to the stream from node 1 and periodically reads the data
    import simplestreamer
    import time

    streamer = simplestreamer.SimpleStreamer(5201)
    streamer.subscribe("127.0.0.1", 5200, "streamer 1")
    # You can optionally configure the rate at which the remote streamer sends you data
    #streamer.subscribe("127.0.0.1", 5200, "streamer 1", updates_per_sec=1.5)

    while True:
        print(streamer.get_data("streamer 1"))
        time.sleep(0.5)

