from flask import Flask
#from redis import Redis
import os

app = Flask(__name__)
#redis = Redis(host=os.getenv("REDIS_HOST", 'redis'), port=6379)


@app.route('/')
def hello():
 #   redis.incr('hits')
  #  return 'Hello %s\n' % redis.get('hits')
     return '200\n'

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)