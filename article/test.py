from redis import StrictRedis
redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
redis.flushall()