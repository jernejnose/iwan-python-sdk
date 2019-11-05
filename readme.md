# Python SDK for iWan RPC Server
Python library to interface iWAN rpc server.
Compliant with API spec on https://iwan.wanchain.org/static/apidoc/docs.html

## Usage
### Clone repository
Clone repository and copy SDk to your project directory
```shell script
git clone https://github.com/jernejnose/iwan-python-sdk.git
cp cp iwan-python-sdk/iwan_api.py ./

```
### Code examples
```python
import iwan_api

testApi = api.ApiInstance(YOUR_API_KEY, YOUR_SECRET_KEY)
#by default it connects to 'wss://api.wanchain.org:8443/ws/v3/', you can change that by defining uri parameter
testApi.get_balance("0x2cc79fa3b80c5b9b02051facd02478ea88a78e2c")
```

## Notes
* Documentation and tests are yet to be implemented.
