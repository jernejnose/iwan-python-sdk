# Python SDK for iWan RPC Server
Python library to interface iWAN rpc server.
Compliant with API spec on https://iwan.wanchain.org/static/apidoc/docs.html

## Usage
```python
import iwan_api

testApi = iwan_api.ApiInstance(YOUR_API_KEY, YOUR_SECRET_KEY)
#by default it connects to 'wss://api.wanchain.org:8443/ws/v3/', you can change that by defining uri parameter
testApi.get_balance("0x2cc79fa3b80c5b9b02051facd02478ea88a78e2c")
```