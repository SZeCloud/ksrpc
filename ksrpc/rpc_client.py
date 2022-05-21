# 客户端，用于处理请求
# 需要选择到底是http还是ws，还是nng一类的

from .utils.async_ import to_async, to_sync


class RpcClient:
    """是否优先从缓存中获取"""
    cache_get: bool = True
    """缓存超时时间，秒"""
    cache_expire: int = 86400
    """是否暴露为异步调用，async def函数中才能启用"""
    is_async = False

    def __init__(self,
                 module,
                 connection,
                 is_async=False
                 ):
        """

        Parameters
        ----------
        module: str
            模块名
        connection: Connection
            连接对象
        is_async: bool
            
        """
        self._connection = connection
        self._module = module
        self._methods = [module]
        self.is_async = is_async

    def __getattr__(self, method):
        self._methods.append(method)
        return self

    def __call__(self, *args, **kwargs):
        # 排序，参数顺序统一后，排序生成key便不会浪费了
        kwargs = dict(sorted(kwargs.items()))

        func = '.'.join(self._methods)
        # 用完后得重置，否则第二次用时不正确了
        self._methods = [self._module]
        # 指定外部调用方式是同步还是异步
        if self.is_async:
            f = to_async(self._connection.call)
        else:
            f = to_sync(self._connection.call)

        # 注意：这里没有指定输入输出格式，只有输入二进制，输出二进制的格式
        # 服务器可以支持多种格式是用于非python客户端
        return f(func, args, kwargs, cache_get=self.cache_get, cache_expire=self.cache_expire)

    def __len__(self):
        # 不知怎么回事，被主动调用了
        return 0
