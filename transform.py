
import os
import sys
import cv2
import time
import json
import random
import argparse
import requests
import numpy as np
import psutil
import shutil
from urllib.request import urlretrieve


# def argument_parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--ApiKey", type=str, default='')
#     return parser

def main(clothPath, poseFileName):
    # parser = argument_parser()
    # args = parser.parse_args()

    # ApiKey = args.ApiKey
    ApiKey = 'hb-s9MceKiq7gSAwUJtAJSBCccOgTnSterE'
    poseName = poseFileName
    clothName = "cloth.jpg"
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(cur_dir, 'static/images')
    pose_path = os.path.join(data_dir, poseName)
    cloth_path = getImageFromPath(clothPath)
    # cloth_path = os.path.join(data_dir, clothName)

    out_pose_path = os.path.join(data_dir, 'out_pose.jpg') # The output is in jpg format
    out_img_path = os.path.join(data_dir, 'out_img.jpg') # The output is in jpg format
    out_mask_path = os.path.join(data_dir, 'out_mask.jpg') # The output is in jpg format
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ApiKey}"
    }

    ################### Step 1. Get an upload link, which can be used to upload images ###################
    uuid = ''
    clothUrl = ''
    maskUrl = ''
    poseUrl = ''

    params = {
        "user_img_name": poseName,
        "cloth_img_name": clothName,
        "category": "1",
        "caption": "red, t-shirt"
    }
    session = requests.session()
    ret = requests.post(f"https://heybeauty.ai/api/create-task", 
        headers=headers, data=json.dumps(params))

    res = 0
    if ret.status_code==200:
        if 'data' in ret.json():
            print(ret.json())
            data = ret.json()['data']
            uuid = data['uuid']
            clothUrl = data['cloth_img_url']
            maskUrl = data['mask_img_url']
            poseUrl = data['user_img_url']
            """
                {'code': 0, 'message': 'ok', 
                'data': 
                    {'uuid': 'v5qg9qlwlgvfug', 'user_uuid': 'cuz64hlvw0ccei', 
                    'created_at': '2024-05-25T02:03:31.192Z', 
                    'updated_at': '2024-05-25T02:03:31.192Z', 
                    'user_img_url': 'https://selfit-dep', 
                    'cloth_img_url': 'https://selfit-deploy-', 
                    'mask_img_url': 'https://selfit-deploy-', 
                    'tryon_img_url': '', 'status': 'created', 'dress_type': 'upper_body', 
                    'inf_id': 12709, 'caption': 'red, t-shirt', 'err_msg': '', 'source': 'api', 
                    'idm_category': '1', 'bmi': 22.2, 'skin': -100, 'user_ip': '183.192.100.3'}}
            """
            print("currnet uuid: ", uuid, " Please remember this ID! Otherwise, the task cannot be queried")
        else:
            """
            {
                "code": 500,
                "msg": "Hacker access detected！"
            }
            """
            print(ret.json())
            data = ret.json()
            print("fail info is, ", data)
            exit(0)
    ################### Step 1. Get an upload link, which can be used to upload images ###################
    

    ################### Step 2. Upload pictures ###################
    with open(cloth_path, 'rb') as file:
        response = requests.put(clothUrl, data=file)
        if response.status_code == 200:
            print(response)
        else:
            raise Exception('upload failed！')
    with open(pose_path, 'rb') as file:
        response = requests.put(poseUrl, data=file)
        if response.status_code == 200:
            print(response)
        else:
            raise Exception('upload failed！')
    ################### Step 2. Upload pictures ###################
    
    
    ################### Step 3: Publish the task, and coins will start to be consumed at this time ###################

    params = {'task_uuid':uuid}
    session = requests.session()
    ret = requests.post(f"https://heybeauty.ai/api/submit-task", 
        headers=headers, data=json.dumps(params))
    if ret.status_code==200:
        print(ret.json())
        if 'data' in ret.json():
            '''
                {'code': 0, 'message': 'ok', 
                'data': {'uuid': 'ficctzlwlgyol7', 'user_uuid': 'cuz64hlvw0ccei', 
                'created_at': '2024-05-25T02:06:02.491Z', 
                'updated_at': '2024-05-25T02:06:02.491Z', 
                'user_img_url': 'https://selfit-deploy-1256039085.cos.accelerate.myqcloud.com/ClothData/Users/ovB-x639B8QwdfF7kQYS9QKdK6u8/FastInfs/12710/pose/1_pose.jpg', 
                'cloth_img_url': 'https://selfit-deploy-1256039085.cos.accelerate.myqcloud.com/ClothData/Users/ovB-x639B8QwdfF7kQYS9QKdK6u8/FastInfs/12710/cloth/2_cloth.jpg', 
                'mask_img_url': '', 'tryon_img_url': '', 'status': 'submitted', 
                'dress_type': 'upper_body', 'inf_id': '12710', 'caption': 'red, t-shirt', 
                'err_msg': '', 'source': 'api', 'tryon_type': None, 'idm_category': 1, 
                'height': None, 'weight': None, 'bmi': 22.2, 'skin': -100, 
                'cloth_id': None, 'user_ip': '183.192.100.3'}}
            '''
            print('public task successfully!')
        else:
            print('public task failed')
            exit(0)
    else:
        exit(0)
    ################### Step 3: Publish the task, and points will start to be deducted at this time ###################
    
    
    out_pose_path = os.path.join(data_dir, 'out_pose.jpg') # The output is in jpg format
    out_img_path = os.path.join(data_dir, 'out_img.jpg') # The output is in jpg format
    out_mask_path = os.path.join(data_dir, 'out_mask.jpg') # The output is in jpg format
    
    
    ################ Step 4: Continuously query task status ################
    # task is supported to finished in 20 seconds at most time
    # Sometimes you need to queue, which may take more than 40 seconds
    # Sometimes the computer does not turn on, and it takes 10 minutes to complete.
    for _ in range(30):
        time.sleep(18)
        params = {'task_uuid':uuid}
        session = requests.session()
        ret = requests.post(f"https://heybeauty.ai/api/get-task-info", 
            headers=headers, data=json.dumps(params))
        if ret.status_code==200:
            print(ret.json())
            if 'data' in ret.json():
                data = ret.json()['data']
                """
                    {'code': 0, 'message': 'ok', 
                    'data': {'uuid': 'f54gu1lwlh7xhu', 'user_uuid': 'cuz64hlvw0ccei', 
                    'created_at': '2024-05-25T02:13:13.938Z', 
                    'updated_at': '2024-05-25T02:13:34.190Z', 
                    'user_img_url': '',
                    'cloth_img_url': '',
                    'mask_img_url': '',
                    'tryon_img_url': '',
                    'status': 'successed', 'dress_type': 'upper_body', 'inf_id': '12717', 
                    'caption': 'red, t-shirt', 'err_msg': None, 'source': 'api', 
                    'tryon_type': None, 'idm_category': 1, 'height': None, 'weight': None, 
                    'bmi': 22.2, 'skin': -100, 'cloth_id': None, 'user_ip': '183.192.100.3'}}
                """
                # In fact, you only need to pay attention to these 3 fields
                print("The current task status is: ", data['status'])

                if data['status']=='successed':
                    print(data['user_img_url'])
                    urlretrieve(data['user_img_url'], out_pose_path)
                    urlretrieve(data['tryon_img_url'], out_img_path)
                    urlretrieve(data['mask_img_url'], out_mask_path)
                    print(f"The task has been completed！", flush=True)
                    break
                elif data['status']=='processing':
                    print(f"The task is being queued for execution", flush=True)
                elif data['status']=='failed':
                    err_msg = data['err_msg']
                    print(f"Task failed, error message reported:{err_msg}", flush=True)
                    break
    ################ Step 4: Continuously query task status ################

def is_url(path):
    return path.startswith('http://') or path.startswith('https://')

def getImageFromPath(image_path):
    if is_url(image_path):
         # Create the destination directory if it doesn't exist
        destination_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images')
        os.makedirs(destination_dir, exist_ok=True)
        
        # Generate a unique filename in the destination directory
        filename = "cloth.jpg"
        destination_path = os.path.join(destination_dir, filename)

        # Send a GET request to the image URL
        response = requests.get(image_path)
        # Check if the request was successful
        if response.status_code == 200:
            with open(destination_path, 'wb') as file:
                file.write(response.content)
             # Return the path to the stored image
            return destination_path

    # Check if the provided path exists and is a file
    if os.path.isfile(image_path):
        # Create the destination directory if it doesn't exist
        destination_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images')
        os.makedirs(destination_dir, exist_ok=True)
        
        # Generate a unique filename in the destination directory
        filename = "cloth.jpg"
        destination_path = os.path.join(destination_dir, filename)
        
        # Copy the image file to the destination directory
        shutil.copyfile(image_path, destination_path)
        
        # Return the path to the stored image
        return destination_path
    else:
        raise FileNotFoundError(f"No such file: '{image_path}'")

def deleteImage(imageName):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(cur_dir, 'static/images')
    image_path = os.path.join(data_dir, imageName)
    try:
        os.remove(image_path)
        print(f"Deleted image: {image_path}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error deleting image: {e}")

if __name__ == '__main__':
    main()
    # Wait for the main function to complete
    print("Waiting for main function to complete...")
    while True:
        time.sleep(5)  # Adjust sleep time as needed
        # Check if the main function is still running
        if not any(p.name() == 'MainProcess' for p in psutil.process_iter()):
            break

    print("Main function completed. Exiting...")
