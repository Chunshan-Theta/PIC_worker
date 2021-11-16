#worker-pic
implement model from https://github.com/bryandlee/animegan2-pytorch

### Run server
```commandline
sudo docker-compose build
sudo docker-compose up -d
```

### Swagger
```commandline
http://127.0.0.1:8082/api/doc/
```

# api
### draw a pic

```commandline
curl -X POST \
http://<server_name>:8082/receive_img \
-H 'cache-control: no-cache' \
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
-F images=@<pic_name>.jpg \
--output <output_pic_name>.jpg
```