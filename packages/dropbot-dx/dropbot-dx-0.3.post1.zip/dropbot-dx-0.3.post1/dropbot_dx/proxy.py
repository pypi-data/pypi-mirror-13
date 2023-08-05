from path_helpers import path


try:
    from base_node_rpc.proxy import ConfigMixinBase, StateMixinBase
    from .node import (Proxy as _Proxy, I2cProxy as _I2cProxy,
                       SerialProxy as _SerialProxy)
    from .config import Config
    from .state import State


    class ConfigMixin(ConfigMixinBase):
        @property
        def config_class(self):
            return Config


    class StateMixin(StateMixinBase):
        @property
        def state_class(self):
            return State


    class ProxyMixin(ConfigMixin, StateMixin):
        '''
        Mixin class to add share common functionality between `Proxy`,
        `SerialProxy`, etc. classes.
        '''
        host_package_name = str(path(__file__).parent.name.replace('_', '-'))

        def __del__(self):
            self.update_state(light_enabled=False, magnet_engaged=False)
            super(ProxyMixin, self).__del__()


    class Proxy(ProxyMixin, _Proxy):
        pass

    class I2cProxy(ProxyMixin, _I2cProxy):
        pass

    class SerialProxy(ProxyMixin, _SerialProxy):
        pass
except (ImportError, TypeError):
    Proxy = None
    I2cProxy = None
    SerialProxy = None
