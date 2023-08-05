from nose.tools import ok_, eq_, nottest
from dropbot_dx import SerialProxy 


def test_state_update():
    '''
    Test setting state fields through `update_state` method.
    '''
    proxy = SerialProxy() 

    states = [(light, magnet) for light in [True, False]
              for magnet in [True, False]]

    for light, magnet in states:
        yield test_state_update_single, proxy, light, magnet


@nottest
def test_state_update_single(proxy, light, magnet):
    ok_(proxy.update_state(light_enabled=light, magnet_engaged=magnet))
    state = proxy.state
    eq_(state.light_enabled, light)
    eq_(state.magnet_engaged, magnet)
