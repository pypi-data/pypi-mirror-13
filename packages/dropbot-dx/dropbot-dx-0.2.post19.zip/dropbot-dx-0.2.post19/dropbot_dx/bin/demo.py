import logging
import time

from arduino_rpc.protobuf import resolve_field_values

from .. import SerialProxy


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    proxy = SerialProxy()

    print '# Config #\n'
    print resolve_field_values(proxy.config, set_default=True)[['full_name',
                                                                'value']]

    print '\n' + (72 * '-') + '\n'

    # Turn on light and move magnet to engaged position.
    proxy.update_state(magnet_engaged=True, light_enabled=True)
    print '# State #\n'
    print resolve_field_values(proxy.state, set_default=True)[['full_name',
                                                            'value']]

    print '\n'

    for i in xrange(5, 0, -1):
        print '\rClosing in %d...' % i,
        time.sleep(1)

    print '\rDone.            '
