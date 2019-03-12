# import boto3
# from django.utils.datastructures import MultiValueDictKeyError
# from django.http import HttpResponse
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
# from . import services
# import imghdr   # Determine the type of an image


# Using to write software that makes use of Amazon services like S3 and EC2.
# @require_POST
# def upload_profilenew(request):
#     res = {}
#     try:
#         if request.FILES['pic']:
#             file = request.FILES['pic']  # Uploading a Pic
#             print("Name of a File",file)
#             tag_file= request.POST.get('email')
#             valid_image=imghdr.what(file)
#             print("Image Extension",valid_image)
#             if valid_image:
#                 key = tag_file
#                 services.s3.upload_fileobj(file, 'fundoobucket', Key=key)
#                 res['message'] = "Sucessfully Uploaded the Image"
#                 res['Sucess'] = True
#                 return JsonResponse(res, status=200)
#             else:
#                 res['message'] = "Invalid File Uploaded"
#                 res['Sucess'] = False
#                 return JsonResponse(res, status=404)
#         else:
#             res['message'] = "Please select a valid file"
#             res['Sucess'] = False
#             return JsonResponse(res, status=404)
#     except MultiValueDictKeyError:
#         res['message'] = "Select a Valid File"
#         res['Sucess'] = False
#         return JsonResponse(res,status=404)
#
#     except Exception as e:
#         print(e)
#         return json()