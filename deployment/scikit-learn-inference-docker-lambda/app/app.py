import json
import numpy as np

def handler(event, context):
    print('Received event: ' + json.dumps(event, indent=2))

    x = np.asarray((2,3))
    print (x)

    return "a"