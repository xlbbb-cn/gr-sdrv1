
import threading

class io_ctx(object):
    '''保存全局变量'''
    _instance = None  # 用于存储唯一的实例
    _lock = threading.Lock()  # 添加一个锁

    def __new__(cls):
        with cls._lock:  # 在创建实例时加锁
            if cls._instance is None:
                cls._instance = super(io_ctx, cls).__new__(cls)
                cls._instance.context = {}
        return cls._instance
    
    def query_context(self, key):
        # 读取操作可以不加锁，如果context的读写是原子性的，或者可以接受脏读。
        # 对于字典的读写，Python GIL在单进程内提供了部分保护，但跨线程非原子操作仍需注意。
        # 如果需要严格的一致性读，也需要加锁。
        if key in self.context:
            return self.context[key]
        else:
            return None
        
    def set_context(self, key, value):
        with self._lock:  # 写入操作加锁
            self.context[key] = value
            return value


    @property
    def phy_name(self):
        return "nrf9022-phy"
    
    @property
    def rxstream_name(self):
        return "avc_rxstream"
    
    @property
    def txstream_name(self):
        return "avc_txstream"