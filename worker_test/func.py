import torch
from torchvision import transforms
from torchvision.utils import save_image
from PIL import Image

# img = Image.open("test.png").convert('RGB')
# print(img)
# convert_tensor = transforms.ToTensor()
# img = convert_tensor(img)
# img = torch.unsqueeze(img,0)

pretrained_options = ["celeba_distill", "face_paint_512_v1", "face_paint_512_v2", "paprika"]
now_model = "face_paint_512_v2"
model = torch.hub.load("bryandlee/animegan2-pytorch:main", "generator", pretrained=now_model)


def draw_pic(img, draw_type:str="face_paint_512_v1"):
    print(f"draw......")
    global now_model, model
    if now_model != draw_type:
        print(f"loading model {draw_type}......")
        model = torch.hub.load("bryandlee/animegan2-pytorch:main", "generator", pretrained=draw_type)
        now_model = draw_type[:]

    #
    img = img.convert('RGB')
    convert_tensor = transforms.ToTensor()
    img = convert_tensor(img)
    img = torch.unsqueeze(img, 0)
    out = model(img)
    save_image(out, f'output.png')
    return Image.open(f'output.png')

# for pretrained_model in pretrained_options:
#     model = torch.hub.load("bryandlee/animegan2-pytorch:main", "generator", pretrained=pretrained_model)
#     out = model(img)
#     save_image(out, f'output-{pretrained_model}.png')


