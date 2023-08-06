'''Constants used across the BatchCompute SDK package in general.
'''
import sys
import logging

# A dictionary to map numeric state to string state.
STATE_MAP = [
    'Init', 'Waiting', 'Running',
    'Finished', 'Failed', 'Stopped'
]

# BatchCompute endpoint information.
ENDPOINT_INFO = {
    'cn-qingdao': 'batchcompute.cn-qingdao.aliyuncs.com',
    'cn-hangzhou': 'batchcompute.aliyuncs.com',
    'cn-shenzhen': 'batchcompute.cn-shenzhen.aliyuncs.com'
}
SERVICE_PORT = 80 
SECURITY_SERVICE_PORT = 443
CN_HANGZHOU = ENDPOINT_INFO['cn-hangzhou']
CN_QINGDAO = ENDPOINT_INFO['cn-qingdao']
CN_SHENZHEN = ENDPOINT_INFO['cn-shenzhen']

# Api version supported by BatchCompute.
API_VERSION = '2015-11-11'

# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

# Definition of descriptor types.
if PY2:
    STRING = (str, unicode)
    NUMBER = (int, long)

if PY3:
    STRING = (str, bytes)
    NUMBER = (int, )
TIME = (int, ) + STRING
COLLECTION = (list, tuple)

# Log configuration
LOG_LEVEL = logging.WARNING
LOG_FILE_NAME = 'batchcompute_python_sdk.LOG'
LOG_FORMATTER = "[%(asctime)s]\t[%(levelname)s]\t[%(thread)d]\t[%(pathname)s:%(lineno)d]\t%(message)s"
LOG_HANDLER = None
ALL_LOGS= {} 

# Default values
DEFAULT_LIST_ITEM = 100
