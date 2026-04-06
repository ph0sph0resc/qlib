# data/client.py 模块文档

## 文件概述

此文件实现了Qlib客户端与服务器之间的网络通信功能，通过socket.io实现请求-响应模式，支持获取日历、标的物和特征数据。

## 类与函数

### Client 类

**继承关系**:
- 无直接父类

**主要属性**:
- `sio`: socket.io客户端对象
- `server_host`: 服务器主机地址
- `server_port`: 服务器端口号
- `logger`: 模块日志记录器

**主要方法**:

```python
def __init__(self, host, port)
```
- 初始化客户端连接
- 参数：
  - host: 服务器主机地址
  - port: 服务器端口号
- 建立socket.io客户端并绑定连接/断开回调

```python
def connect_server(self)
```
- 连接到服务器
- 建立WebSocket连接：ws://host:port
- 处理连接错误并记录日志

```python
def disconnect(self)
```
- 从服务器断开连接
- 使用socket.io的disconnect()方法
- 处理断开错误

```python
def send_request(self, request_type, request_content, msg_queue, msg_proc_func=None)
```
- 发送请求到服务器并等待响应
- 参数：
  - request_type: 请求类型（calendar/instrument/feature）
  - request_content: 请求内容（dict格式）
  - msg_queue: 消息队列队（queue.Queue）
  - msg_proc_func: 响应处理函数（可选）
- 请求头信息包含qlib版本号
- 建立请求-响应回调处理
- 发送请求并等待响应
- 使用msg_proc_func处理响应数据

## 流程图

### 客户端请求流程

````
用户请求
    ↓
Client.send_request()
    ↓
连接服务器
    ↓
发送请求（JSON格式）
    ↓
等待响应
    ↓
msg_proc_func处理响应
    ↓
返回数据到msg_queue
```

### 请求-响应格式

```json
// 请求头
{
    "version": "x.x.x",
    "body": {
        // 实际请求内容
    }
}

// 响应
{
    "status": 0,  // 0:成功, 非0:失败
    "result": ..., // 实际数据
    "detailed_info": "..." // 详细信息
}
```

## 与其他模块的关系

### 依赖模块
- **socket.io**: WebSocket客户端库
- **json**: JSON数据序列化
- **qlib**: 版本信息获取
- **queue**: 消息队列

### 被导入模块
- **qlib.data**: 用于Provider类调用

## 设计模式

### 请求-响应模式

采用异步WebSocket通信：

````
客户端
    ↓
连接服务器
    ↓
发送请求
    ↓
注册回调
    ↓
等待响应
    ↓
处理回调
```

### 错误处理模式

```python
try:
    连接和通信
except ConnectionError:
    记录连接错误
    抛出异常到队列
```

## 使用示例

### 基础使用

```python
from qlib.data.client import Client
import queue

# 创建客户端
client = Client(host="localhost", port=9000)
msg_queue = queue.Queue()

# 发送日历请求
def process_calendar(response):
    return [pd.Timestamp(c) for c in response]

client.send_request(
    request_type="calendar",
    request_content={
        "start_time": "2020-01-01",
        "end_time": "2020-12-31",
        "freq": "day"
    },
    msg_queue=msg_queue,
    msg_proc_func=process_calendar
)

# 获取响应
calendar = msg_queue.get(timeout=30)
```

## 扩展点

### 自定义消息处理

```python
def custom_process(response_content):
    # 自定义响应处理逻辑
    if isinstance(response_content, dict):
        return process_dict(response_content)
    elif isinstance(response_content, list):
        return process_list(response_content)
    return response_content

client.send_request(
    request_type="feature",
    request_content={...},
    msg_queue=msg_queue,
    msg_proc_func=custom_process
)
```

### 超时设置

```python
import socketio

# 配置socket.io超时
sio = socketio.Client(reconnection_attempts=3, reconnection_delay=5)
```

## 注意事项

1. **连接管理**: 每次请求都会重新连接-发送-断开
2. **线程安全**: 使用queue.Queue保证线程安全
3. **超时处理**: 需要设置合适的超时时间
4. **版本兼容**: 请求头包含版本信息，服务器可验证兼容性
5. **错误处理**: 连接和通信错误会被记录并传播
6. **回调机制**: 使用msg_proc_func灵活处理响应
7. **JSON序列化**: 所有请求内容使用JSON序列化
8. **WebSocket协议**: 使用ws://协议进行通信

## 相关文件

- **qlib/data/data.py**: Provider类使用Client
- **qlib/contrib/risk**: 风险管理服务器实现
- **socket.io**: WebSocket客户端库
