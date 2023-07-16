import boto3
import json
from urllib.parse import parse_qs
import requests
import base64


def base64_to_bytes(base64_string):
    try:
        # Decode the base64 string to bytes
        decoded_bytes = base64.b64decode(base64_string)
        return decoded_bytes
    except Exception as e:
        print('Error decoding base64 string:', str(e))
        return None
        
def lambda_handler(event, context):
    
    try:
        
        s3_client = boto3.client('s3')
        rekognition = boto3.client('rekognition', region_name="us-east-1")   
        
        data = str(event['body'])
        parsed_values = parse_qs(data)
        index_name = parsed_values['index'][0]
        image = parsed_values['image'][0]    
        image_metadata = str(image).split(",",1)[0]
        image = str(image).split(",",1)[1]
        
        
        image_bytes = base64.b64decode(image)
        
        if image_bytes is None:
            return {
            'statusCode': 200,
            'body': "Something went wrong"
            }
        
        lable_response = rekognition.detect_labels(
        Image={
            'Bytes': image_bytes
        },
        MaxLabels=10,
        MinConfidence=75
        )
        
        
        face_response = rekognition.detect_faces(
        Image={
            'Bytes': image_bytes
        },
        Attributes=['ALL']
        )       
        
        text_response = rekognition.detect_text(
        Image={
            'Bytes': image_bytes
        }
        )
        
        merged_object = {**lable_response, **face_response, **text_response}
        
        key_to_remove = 'ResponseMetadata'
        if key_to_remove in merged_object:
            del merged_object[key_to_remove]
            
        merged_object['image_blob'] = image
        merged_object['image_start'] = image_metadata
    
        final_doc = json.dumps(merged_object)
        
        endpoint = 'https://<endpoint>/' +str(index_name) + '/_doc'
        username = '<username>'
        password = '<password>'
        
        headers = {
        'Content-Type': 'application/json'
        }

        response =  requests.post(endpoint, auth=(username,password), headers=headers, data=final_doc)
        

        return {
            'statusCode': 200,
            'body': str(response.text)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
        
