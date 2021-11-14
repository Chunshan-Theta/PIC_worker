import os
from util.aredis_queue import QueueRespondsTask
import asyncio
import base64
from util import Job
from func import draw_pic
import io
from PIL import Image


# Convert Image to Base64
def im_2_b64( image):
    buff = io.BytesIO()
    image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue())
    return img_str


# Convert Base64 to Image
def b64_2_img(data):
    buff = io.BytesIO(base64.b64decode(data))
    return Image.open(buff)


async def main():
    while True:
        QRTask = QueueRespondsTask(task_name)
        task = await QRTask.get_content()
        if task is None:
            print(f"task line is empty")
            await asyncio.sleep(1)
            continue

        #
        obj = task.get("obj", None)
        request_id = task.get("request_id", None)
        job_obj = Job(request_id=request_id, content=obj)
        b64_img = job_obj.content["img_base64"].encode("utf-8")
        image = b64_2_img(b64_img)
        new_image = draw_pic(image)

        #
        await QRTask.to_master({
            "img_base64": str(im_2_b64(new_image), "utf-8")
        }, job_obj.request_id)


task_name = os.getenv("task_name", "img_filter")
print(f"Get work from: {task_name}")
asyncio.run(main())
