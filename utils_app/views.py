from rest_framework.response import Response
from rest_framework.decorators import api_view
from utils_app.sequelizers import FileUploadPDFSequelizers
from utils_app.models import FileUploadPDF
import fitz
from PIL import Image
import pytesseract
import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import boto3
import qrcode
from dotenv import load_dotenv
from datetime import datetime


S3_BUCKET_NAME=os.getenv("S3_BUCKET_NAME")

overlay_resize=[]
background_position=[]

# import datetime
load_dotenv()
current_directory = os.path.dirname(os.path.abspath(__file__))

@api_view(['POST'])
def pdf_process(request):
    try:
        file_type=(request.data['file_type']).lower().replace(" ","_")
        match file_type:
            case "test_certificate":
                overlay_resize.extend([120,120])
                background_position.extend([1400, 400])
            case "test_report":
                overlay_resize.extend([90,90])
                background_position.extend([1000,200])
            case _:
                overlay_resize.extend([120,120])
                background_position.extend([1400, 400])
                
        request.data['file_type']=file_type
        sequelizers=FileUploadPDFSequelizers(data=request.data)
        if sequelizers.is_valid():
            obj=sequelizers.save()
            return_value=compute(obj)
        return Response({'status_code':200,'data':return_value})
    except Exception as e:
        print("error in pdf_procesS",e)
        return Response({'status_code':400})

@api_view(['POST'])
def read_text_from_prd(request):
    try:
        sequelizers=FileUploadPDFSequelizers(data=request.data)
        if sequelizers.is_valid():
            obj=sequelizers.save()
            return_value=compute_1(obj)
        return Response({'status_code':200,'data':return_value})
    except Exception as e:
        print(e)
        return Response({'status_code':400})

@api_view(['GET'])
def download_orignal_pdf(request):
    try:
        id=request.GET['id']
        file_name=request.GET['file_name']
        link=generate_presigned_url_actual_pdf(id)
        return Response({'data':link,'status_code':200})    
    except Exception as e:
        print('error in download_orignal_pdf',e)
        return Response({'status_code':400})    


@api_view(['GET'])
def download_embedded_pdf(request):
    try:
        id=request.GET['id']
        link=generate_presigned_url_embedded_pdf(id)
        return Response({'data':link,'status_code':200})    
    except Exception as e:
        print('error in generate_presigned_url_embedded_pdf')
        return Response({'status_code':400})    

@api_view(['GET'])
def download_embedded_img(request):
    try:
        id=request.GET['id']
        link=generate_presigned_url_embedded_img(id)
        return Response({'data':link,'status_code':200})    
    except Exception as e:
        print('error in generate_presigned_url_embedded_pdf')
        return Response({'status_code':400})    

# ------------------------------------------------------------------------------------------------------------

def compute_1(obj):
    try:
        #STEP 1 convert pdf to img
        image_name=pdf_to_image(obj)    
        
        #STEP 2 convert text to img
        ocr_text=image_to_text(image_name)
        os.remove(os.path.join(current_directory,'../dump-output',"{}.png".format(str(obj.pdf_loc).split('/')[1])))
        
        # os.remove(os.path.join(current_directory,'../media/qr-code-test-certificate-inhouse-original-pdf/{}'.format(obj.id),"{}".format(str(obj.file_name))))
        FileUploadPDF.objects.filter(id=obj.id).delete()
        return ocr_text
    except Exception as e:
        print(e)


def compute(obj):
    try:
        #STEP 1 convert pdf to img
        image_name=pdf_to_image(obj)
    
        #STEP 2 generate qr code
        generate_qr(obj.id)
        
        #STEP 2 embed QRCode to img
        embbed_qr_to_image(image_name)
        
        #STEP 2 convert img to pdf
        convert_to_pdf(image_name)
        
        upload_file_to_s3(obj)
        
        os.remove(os.path.join(current_directory,'../dump-output',"{}.pdf".format(str(obj.id))))
    except Exception as e:
        print(e)


def pdf_to_image(obj):
    file_path=obj.pdf_loc
    img_name=obj.id
    try:
        original_pdf_file_path = os.path.join(current_directory, "../media", str(file_path))
        doc = fitz.open(original_pdf_file_path)  
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
            
            file_path_dump_output=os.path.join('dump-output', "{}.png".format(img_name))
            pix.save(file_path_dump_output)

        print('converted pdf to image ✔️')
        return "{}.png".format(img_name)
    except Exception as e :
        print('error in pdf_to_image')


def embbed_qr_to_image(background_path):
    try:
        background = Image.open(os.path.join(current_directory,'../dump-output',background_path))
        overlay_image_path = "qr_code.png"
        overlay = Image.open(overlay_image_path)
        
        overlay = overlay.resize((int(overlay_resize[0]), int(overlay_resize[1])), Image.Resampling.LANCZOS) 
        overlay = overlay.convert("RGBA")
        overlay_with_transparency = Image.new("RGBA", overlay.size)

        for x in range(overlay.width):
            for y in range(overlay.height):
                r, g, b, a = overlay.getpixel((x, y))
                overlay_with_transparency.putpixel((x, y), (r, g, b, int(a * 1)))

        background.paste(overlay_with_transparency, (int(background_position[0]),int(background_position[1])), overlay_with_transparency)
        background.save(os.path.join(current_directory,'../dump-output','{}'.format(background_path)), "PNG")
        print('added QR CODE on image ✔️')
        overlay_resize.clear()
        background_position.clear()
        
    except Exception as e:
        print('error in embbed_qr_to_image',e)


def image_to_text(img):
    year_range=[]
    
    for x in range(0,-6,-1):
        year_range.append(int(str(int(datetime.today().strftime('%Y'))+int(x))[2:]))
        
    for x in range(5):
        year_range.append(int(str(int(datetime.today().strftime('%Y'))+int(x+1))[2:]))
    year_range.sort(reverse=False)

    
    image_path = img
    img = Image.open(os.path.join(current_directory,'../dump-output',image_path))
    text = pytesseract.image_to_string(img)
    list_of_text=text.split(" ")

    only_int=[]
    for text in list_of_text:
        text_compose=text.replace('\n','')
        try:
            if type(int(text_compose))==int and len(text_compose)>3:
                only_int.append(text_compose)
        except Exception as e:
            continue
    print(text_compose)
    _val=[]
    for x in only_int:
        if (int(x[0:3][-2:]) in year_range):
            _val.append(x)
    print(_val)
    return _val


def convert_to_pdf(image_path):
    try:    
        img = ImageReader(os.path.join(current_directory,'../dump-output',image_path))
        img_width, img_height = img.getSize()
        _=image_path.split('.')[:1][0]
        output_pdf_path='{}.pdf'.format(_)
        print(output_pdf_path)
        pdf_canvas = canvas.Canvas(os.path.join(current_directory,'../dump-output',output_pdf_path), pagesize=(img_width, img_height))
        pdf_canvas.drawImage(img, 0, 0, width=img_width, height=img_height)
        pdf_canvas.save()
        print('converted img to pdf ✔️')
    except Exception as e:
        print('error in convert_to_pdf',e)


def generate_qr(id):
    qr = qrcode.QRCode(version=3, box_size=10, border=1, error_correction=qrcode.constants.ERROR_CORRECT_H)
    link=os.getenv("URL_LINK")
    data = "{}/share/{}".format(link,id)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_code.png")


def upload_file_to_s3(obj):
    try:
        s3 = boto3.client('s3')
        

        current_directory = os.path.dirname(os.path.abspath(__file__))

        original_pdf_file_path = os.path.join(current_directory,'../media',str(obj.pdf_loc))
        s3.upload_file(original_pdf_file_path,S3_BUCKET_NAME ,"{}/{}/{}".format(str(obj.pdf_loc).split('/')[0],str(obj.pdf_loc).split('/')[1],str(obj.pdf_loc).split('/')[2]) )

        
        embedded_pdf_file_path=os.path.join(current_directory,'../dump-output',"{}.pdf".format(str(obj.pdf_loc).split('/')[1]))
        embedded_img_file_path=os.path.join(current_directory,'../dump-output',"{}.png".format(str(obj.pdf_loc).split('/')[1]))

        s3.upload_file(embedded_pdf_file_path,S3_BUCKET_NAME,"{}/{}.pdf".format('qr-code-test-certificate-inhouse-embeded-pdf',str(obj.pdf_loc).split('/')[1]))
        s3.upload_file(embedded_img_file_path,S3_BUCKET_NAME,"{}/{}.png".format('qr-code-test-certificate-inhouse-embeded-pdf',str(obj.pdf_loc).split('/')[1]))
        

        # delete the img file created
        # os.remove(os.path.join(current_directory,'../dump-output',"{}.png".format(str(obj.pdf_loc).split('/')[1])))
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False
    else:
        print(f"File uploaded successfully")
        return True



def generate_presigned_url_actual_pdf(id):
    s3_client = boto3.client('s3')
    s3_url = 's3://{}/qr-code-test-certificate-inhouse-original-pdf/{}/{}'.format(S3_BUCKET_NAME,id,get_file_name(id))
    split_url = s3_url.split('/')
    bucket_name = split_url[2]
    object_key = '/'.join(split_url[3:])
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=300
    )   
    return presigned_url



def generate_presigned_url_embedded_pdf(id):
    s3_url = 's3://{}/qr-code-test-certificate-inhouse-embeded-pdf/{}.pdf'.format(S3_BUCKET_NAME,id)
    split_url = s3_url.split('/')
    bucket_name = split_url[2]
    object_key = '/'.join(split_url[3:])
    s3_client = boto3.client('s3')
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key,
            # 'ResponseContentType': 'application/pdf'
            },
        ExpiresIn=3000
    )
    return presigned_url

def generate_presigned_url_embedded_img(id):
    s3_url = 's3://{}/qr-code-test-certificate-inhouse-embeded-pdf/{}.png'.format(S3_BUCKET_NAME,id)
    split_url = s3_url.split('/')
    bucket_name = split_url[2]
    object_key = '/'.join(split_url[3:])
    s3_client = boto3.client('s3')
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key,
            'ResponseContentType': 'image/png'
            },
        ExpiresIn=3000
    )
    return presigned_url


def get_file_name(id):
    try:
        s3 = boto3.client('s3')
        bucket_name = S3_BUCKET_NAME
        prefix = 'qr-code-test-certificate-inhouse-original-pdf/{}/'.format(id)
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' in response:
            for obj in response['Contents']:
                val=(obj['Key'].split('/')[-1:][0])
                print(val)
                return val
        else:
            print("No objects found in the specified S3 bucket and prefix.")
            return False
    except Exception as e:
        print('error in getting file name',e)


