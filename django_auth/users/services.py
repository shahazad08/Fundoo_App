
"""This file contains details about services required
    i.e. Cloud Services  and Redis
"""

import boto3
import imghdr
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDictKeyError
import redis
import json
from django.http import JsonResponse


s3 = boto3.client('s3')  # Connection for S3
def upload_image(file, tag_file, valid_image):
    """This method is used to upload the images to Amazon s3 bucket"""
    res = {}
    try:
        if valid_image:
            key = tag_file
            s3.upload_fileobj(file, 'fundoobucket', Key=key)
            res['message'] = "Sucessfully Uploaded the Image"
            res['Sucess'] = True
            return JsonResponse(res, status=200)
        else:
            res['message'] = "Invalid Image File Uploaded"
            res['Sucess'] = False
            return JsonResponse(res, status=404)
    except MultiValueDictKeyError:
        res['message'] = "Select a Valid File"
        res['Sucess'] = False
        return JsonResponse(res, status=404)
    except Exception as e:
        print(e)
        return HttpResponse(e)


def image_delete(file, tag_file, valid_image):
    key = tag_file
    client.delete_object(Bucket='fundoobucket', Key=key)

    


r = redis.StrictRedis(host='localhost', port=6379, db=0)

class redis_information:
    """This class is used to set , get and delete data from Redis cache
    In addition to the changes above, the Redis class, a subclass of StrictRedis,
    overrides several other commands to provide backwards compatibility with older
    versions of redis-py

    """
    def set_token(self, key, value):
        if key and value:
            r.set(key, value)

    def get_token(self, key):
        value = r.get(key)
        if value:
            return value

