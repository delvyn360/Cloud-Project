import sys
sys.path.append('backend')
import index
from config import app
debug=True
if __name__ == '__main__': 
    #app.run(host="localhost", port=9090, debug=debug) 
    app.run(debug=True,host="0.0.0.0", port=9000)