from PIL import Image
import os
import uuid
from django.contrib.staticfiles.templatetags.staticfiles import static
import hashlib


def create_share_image(slots, image):
    #
    # files = ['img/game/items/test02/avatar/audial01_01.png', 'img/game/items/test02/avatar/audial02_02.png',
    #          'img/game/avatar/M/03.png', 'img/game/items/test02/avatar/audial02_04.png', 'img/game/avatar/M/05.png']
    # files = slots

    # init_avatar = Image.open(share_avatars_path + '/img/game/avatar/' + init_avatar + '/whole_avatar.png')


    init_avatar = Image.new('RGBA', (4267, 8534))

    init_avatar_w, init_avatar_h = init_avatar.size

    h_prev = 0

    profile_slots_ordered_array = [x[1] for x in sorted(slots.items()) if type(x[1]) != int ]

    project_dir = os.path.realpath(os.getcwd())

    for index, file in enumerate(profile_slots_ordered_array):

        #p = os.path.abspath(file).replace('src/img', 'src/static/img')
        p = os.path.join(project_dir + '/static', file)
        img = Image.open(p)
        w, h = img.size

        # right hand
        if index == 3:
            img_area = (init_avatar_w - w, h_prev, init_avatar_w, h + h_prev)
        else:
            img_area = (0, h_prev, w, h + h_prev)

        if index != 2:
            h_prev = h + h_prev

        init_avatar.paste(img, img_area)

    init_avatar_w, init_avatar_h = init_avatar.size

    init_avatar_w = int(init_avatar_w)
    init_avatar_h = int(init_avatar_h)

    init_avatar = init_avatar.resize((init_avatar_w, init_avatar_h), Image.ANTIALIAS)

    init_avatar = init_avatar.resize((int(init_avatar_w / 14), int(init_avatar_h / 14)), Image.ANTIALIAS)

    blanc_img = Image.new('RGBA', (1300, 607))  # 1480

    b_w, b_h = blanc_img.size
    w, h = init_avatar.size

    blanc_img.paste(init_avatar, (int((b_w - w) / 2), 0, int((b_w + w) / 2), h))

    #Создание рамки у изображения
    # blanc_img = ImageOps.expand(blanc_img, border = 1, fill ='black')

    image_name = str(uuid.uuid4()).replace('-', '') + '.png'

    share_img_path = os.path.join(project_dir, "static/img/share_avatars")

    if not os.path.isdir(share_img_path):
        os.mkdir(share_img_path)

    blanc_img.save(share_img_path + '/' + image_name)

    if image is not None:
        try:
            remove_prev_profile_share_avatar(share_img_path + '/' + image)
        except Exception as e:
            pass


    return image_name



def get_hash_sum(file):
    hash_md5 = hashlib.md5()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def remove_prev_profile_share_avatar(file):
    os.remove(file)