import logging
import time

from arduino_rpc.protobuf import resolve_field_values

from .. import SerialProxy


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    proxy = SerialProxy()

    print '# Properties #\n'
    print proxy.properties

    print '\n' + (72 * '-') + '\n'

    print '# Config #\n'
    print proxy.config

    print '\n' + (72 * '-') + '\n'

    # Turn on light and move magnet to engaged position.
    proxy.update_state(magnet_engaged=True, light_enabled=True)
    print '# State #\n'
    print proxy.state

    print '\n'

    for i in xrange(5, 0, -1):
        print '\rClosing in %d...' % i,
        time.sleep(1)

    print '\rDone.            '
