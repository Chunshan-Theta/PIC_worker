import json

from tornado.web import RequestHandler

from util.aredis_queue import QueueRequestTask
import asyncio
from util.text_cuter import lcut
from util.text_cleaner import del_html_tags, del_space
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
                "error": "圖片格式錯誤(目前檔名不能有中文, 只接受jpg圖檔)",
                "detail": str(e)
            },ensure_ascii=False))
#
class dotsHandler(RequestHandler):

    async def post(self):
        """
        ---
        tags:
        - tool
        summary: 取得個別故事之使用者分佈

        description: 取得個別故事之使用者分佈
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

        responses:
            200:
              description: test
        """
        body = json.loads(self.request.body)
        content = body.get("story_id", None)
        if content is None:
            self.write_json({
                "status":"400",
                "content": content,
                "data":"No content"
            })


        self.write_json({
            "status": "200",
            "dots": demo_data,
        })


demo_data = [('空瓶', [-537460098250.43677, 579663242779.7759]),
 ('Yuika', [153337777874.44647, -120846829563.4092]),
 ('芽', [-196436777621.83484, 209842028287.40485]),
 ('Gobe', [-109125851886.73157, 115692304401.82796]),
 ('Nickie', [-201397301292.61722, 165732077661.85202]),
 ('台中Diane', [344056127336.14844, -244815829627.9248]),
 ('鹿門', [379660767349.87134, -292895422154.6833]),
 ('Damara', [-123467040159.34955, 191878787168.16315]),
 ('艾麗莎', [-326316136855.21716, 347271469428.2792]),
 ('Belle', [-60555633540.13965, 167004855307.86447]),
 ('踢娜Tina', [1728740.9763999998, -209320.30799999996]),
 ('Carol', [52893803510.54843, -51294549841.494446]),
 ('王怡今', [-264001943232.65796, 336272990429.1996]),
 ('莯', [-172605887042.40405, 257897389677.3133]),
 ('海寧', [282821990030.3721, -218654812890.97363]),
 ('Mango', [-188048141744.95715, 161275127451.04877]),
 ('fifi', [-225790175623.88324, 346515638894.39]),
 ('Clare', [-139376369513.0464, 250358877998.54]),
 ('Lavendiya', [17945871.8068, -2932751.2600000002]),
 ('宏', [7907.136399999999, -450.864]),
 ('小雅', [-302110905882.1731, 429110951768.6279]),
 ('Sunny', [61149524173.722855, 32736383949.42195]),
 ('candylee', [230303294387.2328, -115003707870.8584]),
 ('Merai', [-461856571583.36, 600712370065.3768]),
 ('Rebecca', [31516855475.913994, -43463594728.46159]),
 ('六月淳', [85603381766.88043, -106381828537.82405]),
 ('KiKier', [175217426125.26205, -119063977933.11885]),
 ('ᵔᴥᵔ Je∞ie🌱', [-268.42760000000027, 7.640000000000002]),
 ('Joe', [17937981.686800003, -2932300.3960000006]),
 ('李饅頭', [71819748457.14761, -141729850576.8676]),
 ('Sin', [5875173174.867197, -1652310116.183197]),
 ('IRIS', [7632.096399999999, -443.224]),
 ('小海', [-56684293166.59999, 58440701394.95479]),
 ('楊米漿', [1205764594.5988, -332119862.95360005]),
 ('云喬', [-927.3356000000053, 312.0200000000005]),
 ('Nell', [-652.2956000000054, 304.3800000000005]),
 ('汝欣', [-400486261175.47034, 480574012915.5956]),
 ('Joanna紫', [327055598938.252, -252620937297.7]),
 ('Max', [-200980436505.52762, 236914219362.30084]),
 ('一葉蘭', [122064080828.84962, -33405740300.503643]),
 ('J❄️', [319629954700.17633, -238933360612.39594]),
 ('Vivien', [-285849245092.6287, 386397347357.47156]),
 ('小如', [-239451598474.7408, 339494743124.9148]),
 ('ICE', [-927.3356000000053, 312.0200000000005]),
 ('美君', [-322170899132.0823, 333827841705.75433]),
 ('Shandy', [-26642912149.09159, 12253526123.739193]),
 ('煦暖暖', [327840237503.54443, -248643780457.1376]),
 ('匡', [59081564785.43802, 8920080520.764774]),
 ('yalan', [-153831381883.6411, 112919530520.84232]),
 ('思嘉', [122359804292.07166, -9341988983.984833]),
 ('Ling', [-255263837493.61005, 373301796578.01965]),
 ('叮噹', [6.612399999999997, 0]),
 ('ee', [-73999570.1156, 17267901.5312]),
 ('Hanna', [-927.3356000000053, 312.0200000000005]),
 ('愛尼塔', [-937.7396000000053, 312.0200000000005]),
 ('晴晴', [196203035868.7484, -220475191463.09763]),
 ('任真', [-268.42760000000027, 7.640000000000002]),
 ('蘇蔓蔓', [-791959413340.6816, 797742042391.5968]),
 ('Chieh', [6.612399999999997, 0]),
 ('雨天', [-49873990236.191185, 22371236385.521584]),
 ('Super  Nina', [403959580022.7129, -417915580180.65125]),
 ('玫瑰人生', [-106632729590.12196, 153479129397.12958]),
 ('Jessie', [383677913546.5593, -334357354685.3969]),
 ('Yunxi', [-66048220274.352776, 48703749982.72798]),
 ('Szu', [-6516163862.163191, 12858465932.628796]),
 ('珮紋', [-117057895201.56989, 234839293430.9107]),
 ('Connie', [-141853265230.12994, 113318766572.25595]),
 ('Lily', [-55640256731.26716, 45842257870.76115]),
 ('Acupoftea', [6.612399999999997, 0]),
 ('April C', [-64857438277.48758, 51797929722.50877]),
 ('Lesley', [-34869306.892400004, 8054677.522400001]),
 ('白姍', [-127578082599.58597, 172561985957.87637]),
 ('Amber', [7896.7324, -450.864]),
 ('kt', [282976007234.0445, -218835365888.3729]),
 ('Toby', [147364552350.73962, -66791065777.99923]),
 ('依秀（Shelly)', [-454709928398.4751, 476486660983.8359]),
 ('Smile', [233937110680.10004, -154395267571.63446]),
 ('Yaya', [359485569836.156, -327230572227.2392]),
 ('炫炫', [55476711585.528915, 36619127955.42311]),
 ('阿茶', [188497367558.0529, -151183191192.0589]),
 ('Kiwi', [1149279207.9244, -320204478.8088]),
 ('Lala', [7533893722.651201, -3192839697.361601]),
 ('mango', [-24439503474.323997, 10681604310.545599]),
 ('Dora', [-333218142.1759999, 107757354.39199996]),
 ('默', [210559328990.7377, -195980051066.23486]),
 ('Adeline', [360020534937.4104, -260305276191.87283]),
 ('Lydia', [3191378226.1632004, -1181091046.8880002]),
 ('Zeida', [-305672498205.9883, 418854945717.7687]),
 ('Wenwen', [623577734.2959998, -147819936.3375999]),
 ('Amie', [496140789314.148, -458079810404.284]),
 ('Mila777', [8793680618.182047, -3288606179.6464524]),
 ('', [-326719570017.672, 347255360068.996]),
 ('韓韓韓', [7890.12, -450.864]),
 ('Irene', [1737293.7959999996, -210075.55199999994]),
 ('好', [7890.12, -450.864]),
 ('Miami', [7890.12, -450.864]),
 ('維霙', [253213683385.55682, -334858170484.56244]),
 ('豫', [-338321850.4399998, 108744313.06799994]),
 ('Angela', [17042194843.581596, -35504596131.563995]),
 ('Serena', [133105998338.54169, -15974226268.54567]),
 ('99', [-86522.52000000003, 7634.34]),
 ('wenwen', [51659746944.00369, 53880794148.20392]),
 ('小千', [324501228905.7639, -247403944482.1895]),
 ('簡式', [-8559.432000000004, 755.2440000000007]),
 ('ANGEL', [-412329042.2479999, 126012657.82319996]),
 ('Hellome', [-99180807300.11998, 84303620295.29999]),
 ('yaya', [1729403.676, -209624.68799999997]),
 ('Mel.', [44916527615.910416, -137697103320.8736]),
 ('yu lin chen', [1729403.676, -209624.68799999997]),
 ('Karen', [37659298122.26801, 83295886088.32799]),
 ('左', [-40618080928.89679, 63135126482.47919]),
 ('Apple', [-33808339.620000005, 8082515.414400001]),
 ('萌萌', [7928431972.719627, 99887135806.22757]),
 ('喜多米', [3182228377.5744, -1181387048.0832]),
 ('For', [1729403.676, -209624.68799999997]),
 ('shandy', [12842826.2424, -1946096.964]),
 ('小臻', [1729403.676, -209624.68799999997]),
 ('Daphne天使/色彩療法', [42008628449.1036, -38957873870.6712]),
 ('LALA', [260197804177.13162, -179297790835.83606]),
 ('Seaa', [-27665985128.803192, 11870894975.702396]),
 ('陳小怡', [-74007191.808, 17268344.7552]),
 ('Mel', [623570119.2159996, -147819493.11359987]),
 ('Iodf', [1223365025.5199997, -337480007.03999996]),
 ('lesley', [15126226703.216883, 30987792002.11193]),
 ('Angel', [-338313291.0079998, 108743557.82399993]),
 ('PIN', [-1188651683.9232008, 535151826.56320035]),
 ('Sara', [38537188423.1232, -23791574303.884796]),
 ('安柏', [29034548978.34721, -38720813262.67081]),
 ('susan', [45318486817.66562, -40587324110.62561]),
 ('Evelyn', [-287832540054.15356, 322069623021.38403]),
 ('Peaceful Cathy', [40337935528.31999, -24553525973.759995]),
 ('ling lo', [-42694676830.07999, 29110006929.59999]),
 ('宛宛', [40776397929.96001, -38630271723.12]),
 ('孟娟', [-330312380373.3601, 348663068171.88007]),
 ('Nicole', [-330312380373.3601, 348663068171.88007]),
 ('Leanne', [2128733780.1767962, -4473446458.439993]),
 ('ConniConniee', [1720806501.9599962, -3176873542.0799932]),
 ('JOJO', [-7724193207.494403, 16092069182.280006]),
 ('微笑貓貓', [-97400730.24000004, 353077647.1200001]),
 ('Susuj', [316531.90799999976, -2025804.2111999982])]

# class cleanHandler(APIHandlerBase):
#
#     async def post(self):
#         """
#         ---
#         tags:
#         - tool
#         summary: 文字清理
#         description: 文字清理
#         produces:
#         - application/json
#         parameters:
#         -   in: body
#             name: body
#             description: post data
#             required: true
#             schema:
#                 type: object
#                 properties:
#                     content:
#                         type: string
#                         default: "一些中 文內 容<br>"
#
#         responses:
#             200:
#               description: test
#         """
#         body = json.loads(self.request.body)
#         content = body.get("content", None)
#         if content is None:
#             self.write_json({
#                 "status":"400",
#                 "content": content,
#                 "data":"No content"
#             })
#
#         #
#         content_formated = content[:]
#         for del_script in [del_space,del_html_tags]:
#             content_formated = del_script(content_formated)
#
#         #
#         self.write_json({
#             "status": "200",
#             "content": content,
#             "clean": content_formated
#         })
