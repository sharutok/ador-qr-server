from main_app.models import AccessModel
from main_app.sequelizers import AccessModelSequelizers

from rest_framework.response import Response
from rest_framework.decorators import api_view
from utils_app.models import FileUploadPDF
from utils_app.views import generate_presigned_url_actual_pdf
from utils_app.sequelizers import FileUploadPDFSequelizers
from rest_framework.pagination import PageNumberPagination
from login_app.models import AdminUsers
from login_app.sequelizers import AdminUsersSerializers

from django.db import connection

@api_view(['GET'])
def get_data(request):
    try:
        paginator = PageNumberPagination()
        paginator.page_size = 10
        search=request.GET['search']
        
        uploaded_date_order= 'fd1.created_at asc' if request.GET['uploaded_date'] == 'true' else 'fd1.created_at desc'

        sql='''select
                *,to_char(created_at::timestamp at TIME zone 'UTC' at TIME zone 'Asia/Kolkata','DD-MM-YYYY') created_at,
                fd1.id
                from
                    file_data fd1
                left join (
                    select
                        fd.id, 
                        array_agg(am.email_id),
                        coalesce(count(fd.id),'0') as no_of_times_view
                    from
                        file_data fd
                    join access_model am on
                        fd.id::text = am.file_name
                    group by
                        fd.id,am.file_name ) t2 on
                    fd1.id::text = t2.id::text
                    where batch_number ilike '%{}%' or fd1.file_name ilike '%{}%'
                    order by {};'''.format(search,search,uploaded_date_order)


        obj=run_query_for_select(sql)
        result_page = paginator.paginate_queryset(obj, request)
        return paginator.get_paginated_response(result_page)
    except Exception as e:
        return Response({'status_code':400})

@api_view(['POST'])
def download_original_pdf(request):
    try:
        _id=request.data['_id']
        print(_id)
        queryset_email = FileUploadPDF.objects.filter(id=str(_id))
        if queryset_email.exists():
            sequelizers=AccessModelSequelizers(data=request.data)
            if sequelizers.is_valid():
                sequelizers.save()
                link=generate_presigned_url_actual_pdf(_id)
                return Response({"data":link,'status_code':200})
            else:
                print('not valid')
                return Response(False)
        else:
                print('there is no such documents')
                return Response({'mess':'there is no such documents','status':400})
    except Exception as e:
        print("error in download_original_pdf",e)
        return Response(False)


































def run_query_for_select(sql_query):
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        rows = [
            dict(zip([col[0] for col in cursor.description], row)) for row in results
        ]
    return rows