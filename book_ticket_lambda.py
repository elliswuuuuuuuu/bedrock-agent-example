# -*- coding: utf-8 -*-

import json
import time
import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF

s3 = boto3.client('s3')
bucket = os.environ.get('BUCKET_NAME')  #Name of bucket with data file and OpenAPI file
SENDER = os.environ.get('SENDER', "alexwuu@amazon.com") 

font_lib = "DejaVuSansCondensed.ttf"
s3.download_file(bucket, font_lib, "/tmp/"+font_lib)


def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']

def get_named_property(event, name):
    return next(item for item in event['requestBody']['content']['application/json']['properties'] if item['name'] == name)['value']


def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', '/tmp/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    # pdf.set_font("Arial", size=12)
    for key, value in data.items():
        print(key, value)
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=1, align="C")
    file_path = "/tmp/ticket.pdf"
    pdf.output(file_path)
    s3_client = boto3.client('s3')
    upload_path = "ticket.pdf"
    s3_client.upload_file(file_path, bucket, upload_path)
    return  file_path

def send_eamil(recipient: str, s3_file_path: str):
    sender = SENDER
    RECIPIENT = recipient

    AWS_REGION = "us-east-1"
    SUBJECT = "Ticket Info"
    
    BODY_TEXT = "Hello,\r\nTicket has been generated, please check out attachment."

    # Download the S3 file to a temporary location
    tmp_file_path = '/tmp/' + os.path.basename(s3_file_path)
    s3.download_file(bucket, s3_file_path, tmp_file_path)

    ATTACHMENT = tmp_file_path

    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <h1>Hello!</h1>
    <p>Ticket has been generated, please check out attachment.</p>
    </body>
    </html>
    """

    CHARSET = "utf-8"
    client = boto3.client('ses',region_name=AWS_REGION)
    msg = MIMEMultipart('mixed')

    msg['Subject'] = SUBJECT 
    msg['From'] = sender 
    msg['To'] = RECIPIENT

    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    att = MIMEApplication(open(ATTACHMENT, 'rb').read())

    att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
    msg.attach(msg_body)
    msg.attach(att)
    try:
        response = client.send_raw_email(
            Source=sender,
            Destinations=[
                RECIPIENT
            ],
            RawMessage={
                'Data':msg.as_string(),
            },
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {"errcode": e.response['Error']['Message']} 
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        return {"errcode": "0000", "MessageId": response['MessageId']} 

flight1 = [
    {"airline_name": "SUPARNA AIRLINES", "flight_number": "Y87587", "craft_type_name": "Aircraft 738(M)", "departure_time": "07:15", "arrival_time": "09:35", "departure_airport": "Shenzhen Baoan", "arrival_airport": "Shanghai Hongqiao", "price": 500},
    {"airline_name": "CHINA EASTERN AIRLINES", "flight_number": "MU5332", "craft_type_name": "Aircraft 32L(M)", "departure_time": "07:30", "arrival_time": "09:40", "departure_airport": "Shenzhen Baoan", "arrival_airport": "Shanghai Hongqiao", "price": 600},
    {"airline_name": "CHINA SOUTHERN AIRLINES", "flight_number": "CZ3625", "craft_type_name": "Aircraft 321(M)", "departure_time": "07:35", "arrival_time": "09:50", "departure_airport": "Shenzhen Baoan", "arrival_airport": "Shanghai Hongqiao", "price": 700}
]

flight2 = [
    {"airline_name": "SUPARNA AIRLINES", "flight_number": "Y87587", "craft_type_name": "Aircraft 738(M)", "departure_time": "07:15", "arrival_time": "09:35", "departure_airport": "Shenzhen Baoan", "arrival_airport": "Shanghai Hongqiao", "price": 800},
    {"airline_name": "CHINA EASTERN AIRLINES", "flight_number": "MU5332", "craft_type_name": "Aircraft 32L(M)", "departure_time": "07:30", "arrival_time": "09:40", "departure_airport": "Shenzhen Baoan", "arrival_airport": "Shanghai Hongqiao", "price": 900},
    {"airline_name": "CHINA SOUTHERN AIRLINES", "flight_number": "CZ3625", "craft_type_name": "Aircraft 321(M)", "departure_time": "07:35", "arrival_time": "09:50", "departure_airport": "Shenzhen Baoan", "arrival_airport": "Shanghai Hongqiao", "price": 1000}
]

data_flights = {
    "2024-02-22": flight1,
    "2024-02-23": flight2
}

def bookTicket(event):
    function_name = "getFlightInformation"
    print(f"calling method: {function_name}")
    print(f"Event: \n {json.dumps(event)}")

    flight_number = get_named_parameter(event, 'flight_number')
    
    data = {
        "airline_name": "SUPARNA AIRLINES",
        "flight_number": "Y87587",
        "craft_type_name": "Aircraft 738(M)",
        "departure_time": "07:15",
        "arrival_time": "09:35",
        "departure_airport": "Shenzhen Baoan",
        "arrival_airport": "Shanghai Hongqiao",
        "price": 500
    }
    file_path = create_pdf(data)

    result = {
                "input_args": {
                    "flight_number": flight_number
                },
                "status": "success",
                "results": {
                    "downloadUrl": f"s3://{bucket}/ticket.pdf"
                }
            }

    return result

def getFlightInformation(event):
    function_name = "getFlightInformation"
    print(f"calling method: {function_name}")
    print(f"Event: \n {json.dumps(event)}")

    departure_city = get_named_parameter(event, 'departure_city')
    arrival_city = get_named_parameter(event, 'arrival_city')
    departure_date = get_named_parameter(event, 'departure_date')
    
    data = flight1

    result = {
                "input_args": {
                    "departure_city": departure_city,
                    "arrival_city": arrival_city,
                    "departure_data": departure_date
                },
                "status": "success",
                "results": {
                    "text_info": data
                }
            }

    return result

def sendReservationEmail(event):
    #定义输出
    print("------------send email----------------")
    function_name = "sendReservationEmail"
    print(f"calling method: {function_name}")
    print(f"Event: \n {json.dumps(event)}")

    email_address = get_named_parameter(event, 'email_address')

    result = send_eamil(email_address, "ticket.pdf")

    res = {}
    res["input_args"] = {}
    res["input_args"]["email_address"] = email_address
    if result["errcode"] == "0000":
        res["status"] = "success"
        res["results"] = "邮件发送成功"
    else:
        res["status"] = "fail"
        res["results"] = f"{result['errcode']}\n邮件发送失败,请稍后尝试重新发送."
    print(res)
    return res


def lambda_handler(event, context):

    result = ''
    response_code = 200
    action_group = event['actionGroup']
    api_path = event['apiPath']
    
    print ("lambda_handler == > api_path: ",api_path)
    print ("Event:", event)
    
    if api_path == '/getFlightInformation':
        result = getFlightInformation(event)
    elif api_path == '/bookTicket':
        result = bookTicket(event)
    elif api_path == '/sendReservationEmail':
        result = sendReservationEmail(event) 
    else:
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"

    response_body = {
        'application/json': {
            'body': json.dumps(result)
        }
    }
    
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        # 'httpMethod': event['HTTPMETHOD'], 
        'httpMethod': event['httpMethod'], 
        'httpStatusCode': response_code,
        'responseBody': response_body,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }

    api_response = {'messageVersion': '1.0', 'response': action_response}
    print("api_response:", api_response)
        
    return api_response