import json
import logging

from tornado.web import RequestHandler
from ..apiHandlerBase import APIHandlerBase
from util.aredis_queue import QueueRequestTask
import asyncio
from util.dot_data import get_templete_dots, get_dots
from PIL import Image, UnidentifiedImageError
import io
import base64


class GetArchives(RequestHandler):
    def respond_to_client(self, data, r_type=None):
        self.set_header("Access-Content-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, "
                                                        "X-Requested-With, X-Requested-By, If-Modified-Since, "
                                                        "X-File-Name, Cache-Control, Token")
        self.set_header('Access-Control-Allow-Origin', '*')
        if r_type == "jpg" :
            self.set_header('Content-Type', 'image/jpeg')

        self.finish(data)
    def image_to_byte_array(self, image: Image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def byte_body_to_dict(self, body):
        data = body.split(b'\r\n')

        return {
            "Content_Disposition": data[1],
            "Content_Type": data[2],
            "Content_body": b''.join(data[4:-2])
        }

    # Convert Image to Base64
    def im_2_b64(self, image):
        buff = io.BytesIO()
        image.save(buff, format="JPEG")
        img_str = base64.b64encode(buff.getvalue())
        return img_str

    # Convert Base64 to Image
    def b64_2_img(self,data):
        buff = io.BytesIO(base64.b64decode(data))
        return Image.open(buff)

    async def post(self):
        """
        ---
        tags:
        - tool
        summary: upload pic
        description:
            "
            curl -X POST \
            http://127.0.0.1:8082/receive_img \
            -H 'cache-control: no-cache' \
            -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
            -F images=@178884.jpg \
            --output test.jpg
            "
        consumes:
        - multipart/form-data
        produces:
        - application/jpg
        parameters:
        -  in: formData
           name: images
           type: file
           description: The file to upload.
           content:
            application/jpg:
              schema:
                type: string
                format: binary


        responses:
            200:
              description: test
        """
        #
        data = self.byte_body_to_dict(self.request.body)

        image_data = data['Content_body']

        max_size = 720
        image_data = io.BytesIO(image_data)
        try:
            image = Image.open(image_data)


            width, height = image.size
            if width > max_size and width > height:
                image = image.resize((max_size, int(height*max_size/width)))
            elif height > max_size and height > width:
                image = image.resize((int(width*max_size/height), max_size))

            # b64_image = self.im_2_b64(image)
            # image = self.b64_2_img(b64_image)
            # img_str = self.image_to_byte_array(image)
            # self.finish(img_str)

            Task = QueueRequestTask(data={
                "img_base64": str(self.im_2_b64(image), "utf-8")
            }, task_type_label="img_filter")

            #
            await Task.to_worker()

            #
            worker_response = await Task.get_content()
            time = 0
            while worker_response is None and time < 500:
                worker_response = await Task.get_content()
                time += 1
                await asyncio.sleep(0.1)
            else:
                b64_image = json.loads(worker_response)["img_base64"]
                b64_image = b64_image.encode("utf-8")
                image = self.b64_2_img(b64_image)
                img_str = self.image_to_byte_array(image)
                self.respond_to_client(img_str,r_type="jpg")

        except UnidentifiedImageError as e:
            self.respond_to_client(json.dumps({
                "error": "??????????????????(???????????????????????????, ?????????jpg??????)",
                "detail": str(e)
            },ensure_ascii=False))
#
class dotsHandler(APIHandlerBase):

    async def post(self):
        """
        ---
        tags:
        - tool
        summary: ????????????????????????????????????

        description: ????????????????????????????????????
        produces:
        - application/json
        parameters:
        -   in: body
            name: body
            description: post data
            required: true
            schema:
                type: object
                properties:
                    story_id:
                        type: string
                        default: "1001"
                    dimension_num:
                        type: int
                        default: 2

        responses:
            200:
              description: test
        """
        body = json.loads(self.request.body)
        story_id = body.get("story_id", "1001")
        dimension_num = body.get("dimension_num", 2)

        # logging.warning(f"story_id: {story_id}")
        # logging.warning(f"dimension_num: {dimension_num}")
        # logging.warning(f"get_dots: {get_dots(dimension_num,story_id)}")
        # logging.warning(f"get_templete_dots: {get_templete_dots(dimension_num,story_id)}")
        self.write_json({
            "status": "200",
            "dots": get_dots(dimension_num,story_id),
            "templete_dots": get_templete_dots(dimension_num,story_id)
        })

