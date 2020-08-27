import cv2
import face_recognition
import matplotlib.pyplot as plt
import requests
import vk_api

# %matplotlib inline

from io import BytesIO
from PIL import Image
from PIL import UnidentifiedImageError
from pathlib import Path

class FilterUsersList:
    def __init__(self, country, min_photos, max_photos, users_count=10000000):
        login = input("Your vk login:")
        password = input("Your vk password:")
        vk_session = vk_api.VkApi(login, password)
        vk_session.auth(token_only=True)
        self.vk = vk_session.get_api()
 
        self.country = self.vk.database.getCountries(code=country)['items'][0]['id']
        self.users_count = users_count
        self.min_photos = min_photos
        self.max_photos = max_photos
        self.current_user = 0
        self.correct_users_counter = 0
        self.offset = 0
        self.users_list = {'count': 0, 'items': []}
        
    def __iter__(self):
        return self

    def __next__(self):
        while self.current_user < self.users_count:
            if not self.users_list['items']: 
                self.users_list = self.vk.users.search(                                           
                  country=self.country, count=1000,
                  offset=self.offset, has_photo=1)
                self.offset += 1000  
            for _ in range(len(self.users_list['items'])):
                elem = self.users_list['items'].pop()
                self.current_user += 1
                if not self.vk.users.get(user_id=elem['id'])[0]['is_closed']:
                    users_profile_photos = self.vk.photos.get(                           
                        owner_id=elem['id'], album_id='profile', count=1000)
                    if (users_profile_photos['count'] >= 3 
                            and users_profile_photos['count'] <= 300):
                        self.correct_users_counter += 1
                        return elem['id'], users_profile_photos
        raise StopIteration

def saving_profile_photos(root_directory, user_id, crops_from_images):
    directory = Path(root_directory).joinpath(str(user_id))             
    Path(directory).mkdir(parents=True, exist_ok=True)                  
    for im in range(len(crops_from_images)):                                       
        for cr in range(len(crops_from_images[im])):                               
            image_name = ('prt_'                                        
                        + '{0:{fill}{align}9}_'.format(im, fill='0', align='>')
                        + '{0:{fill}{align}9}'.format(cr, fill='0', align='>') + '.jpg')
            Image.fromarray(crops_from_images[im][cr]).save(Path(directory).joinpath(image_name))
    return

def get_crops_from_images(user_photos):
    images = []
    for frame in user_photos['items']:
        for copy in frame['sizes']:
            if copy['height'] >= 50 and copy['width'] >= 50:
                print("frame is ok")
                fileRequest = requests.get(copy['url'])
                try:
                    doc = Image.open(BytesIO(fileRequest.content))
                except UnidentifiedImageError:
                    print("PIL cannot identify image")
                    continue
                plt.imshow(doc)
                plt.show()
                try:
                    doc.save("processed_photo.jpg")
                except KeyError:
                    print("Incorrect key for mode")
                    continue
                except OSError:
                    print("OSError")
                    continue
                image = face_recognition.load_image_file("processed_photo.jpg")
                face_locations = []
                face_locations = face_recognition.face_locations(image, model='cnn')
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
                break
    return images
    

def main():

   #country = vk.database.getCountries(code='KZ')['items'][0]['id']
    country = 'KZ'
    root_directory = 'dataset_vk_cnn'
    Path(root_directory).mkdir(parents=True, exist_ok=True)    
    correct_users_photos = FilterUsersList(country, 3, 300)
    users_count = 0
    
    for user_id, user in correct_users_photos:
        images = get_crops_from_images(user)
        if len(images) >= 3:
            saving_profile_photos(root_directory, user_id, images)
            users_count += 1
            if users_count >= 256:
                break
       
if __name__ == '__main__':
    main()
