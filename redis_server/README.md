# redis 

run server with docker-compose
```
services:
    redis:
        image: redis
        volumes:
            - ./redis_server/redis.conf:/usr/local/etc/redis/redis.conf
        ports:
            - "6379"
```