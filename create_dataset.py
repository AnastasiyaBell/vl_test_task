import cv2
import face_recognition
import matplotlib.pyplot as plt
import requests
import vk_api
# %matplotlib inline

from io import BytesIO
from PIL import Image
from pathlib import Path

def main():

    login = input()
    password = input()
    vk_session = vk_api.VkApi(login, password)
    
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()
    country = vk.database.getCountries(code='KZ')['items'][0]['id']
    users_counter = 0
    offset = 0
    search_photo_counter = 1000
    while users_counter < 256:
        users_list = vk.users.search(country=country, count=search_photo_counter, offset=offset, has_photo=1)
        offset += search_photo_counter

        users_list_ids = []
        for i in users_list['items']:
            users_list_ids.append(i['id'])
        
        for id in users_list_ids:
            if vk.users.get(user_id=id)[0]['is_closed'] == False:
                users_profile_photos = vk.photos.get(owner_id=id, album_id='profile', count=1000)
                print(users_profile_photos)
                if users_profile_photos['count'] >= 3 and users_profile_photos['count'] <= 300:
                    images = []
                    photo_counter = 0
                    for frame in users_profile_photos['items']:
                        for copy in frame['sizes']:
                            if copy['height'] >= 50 and copy['width'] >= 50:
                                print("frame is ok")
                                fileRequest = requests.get(copy['url'])
                                doc = Image.open(BytesIO(fileRequest.content))
                                plt.imshow(doc)
                                plt.show()
                                doc.save("processed_photo.jpg")
                                image = face_recognition.load_image_file("processed_photo.jpg")
                                face_locations = []
                                face_locations = face_recognition.face_locations(image)
                                print("face_locations are ready", face_locations)
                                crop_counter = 0
                                crops = []
                                for crop in face_locations:
                                    if crop[2]-crop[0] >= 30 and crop[1]-crop[3] >= 30:
                                        crops.append(image[crop[0]:crop[2],crop[3]:crop[1]])
                                        plt.imshow(crops[crop_counter])
                                        plt.show()
                                        crop_counter += 1
                                if crop_counter >= 1 and crop_counter <= 5:
                                    images.append(crops)
                                    photo_counter += 1
                                break
                    if photo_counter >= 3:
                        users_counter += 1
                        root_directory = 'dataset_vk'
                        directory = Path(root_directory).joinpath(str(id))
                        Path(directory).mkdir(parents=True, exist_ok=True)
                        for im in range(len(images)):
                            for cr in range(len(images[im])):
                                image_name = 'prt_' + '{0:{fill}{align}9}_'.format(im, fill='0', align='>') + '{0:{fill}{align}9}'.format(cr, fill='0', align='>') + '.jpg'
                                Image.fromarray(images[im][cr]).save(Path(directory).joinpath(image_name))
    print("Count of appropriated profiles", users_counter)

if __name__ == '__main__':
    main()
