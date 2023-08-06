import re
from rest_framework.status import *

SUCCESS = 0
FAILED = 1
DEFAULT_MSG = {
    SUCCESS:'SUCCESS',
    FAILED:'FAILED'
}

for st, code in locals().copy().items():
    if st.startswith('HTTP') and isinstance(code, int):
        _,msg = re.search(r'HTTP_(\d+)_([\w_]+)', st).groups()
        DEFAULT_MSG.update({code:msg})    
