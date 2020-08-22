import vk_api

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
    users_list = vk.users.search(country=country, count=10, has_photo=1)
    users_list_ids = []
    for user in users_list['items']:
        users_list_ids.append(user['id'])
    
    for id in users_list_ids:
        if vk.users.get(user_id=id)[0]['is_closed'] == False:
            users_profile_photos = vk.photos.get(owner_id=id, album_id='profile', count=1000)
            #print(profile_photos)
            for user in users_profile_photos:
                if user['count'] >= 3 and user['count'] <= 300:
                    for frame in user['items']:
                        for copy in frame['sizes']:
                            if copy['height'] >= 50 and copy['width'] >= 50:
                                

if __name__ == '__main__':
    main()
