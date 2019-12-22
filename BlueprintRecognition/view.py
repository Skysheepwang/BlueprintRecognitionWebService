import os
import json
import requests
import zipfile
from datetime import datetime

from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import render

from wand.image import Image
from PIL import Image as Image_PIL


def index(request):
    if request.method == 'POST':
        # Save the uploaded pdf file into /blueprints
        fe = request.FILES.get('file', None)
        if fe:
            time_now = datetime.now()
            filename = time_now.strftime('%Y-%m-%d %H-%M-%S_') + fe.name
            pdf_path = 'blueprints/' + filename
            jpg_path = 'media/' + filename
            
            if(fe.name[-4:] == '.pdf'):
                with open(pdf_path, 'wb') as f:
                    for chunk in fe.chunks():
                        f.write(chunk)
                # Turn pdf file to jpg
                with Image(filename=pdf_path, resolution=400) as img:
                    with img.convert('jpg') as converted:
                        converted.save(filename=jpg_path[:-4] + '.jpg')
            elif(fe.name[-4:] == '.jpg'):
                with open(jpg_path, 'wb') as f:
                    for chunk in fe.chunks():
                        f.write(chunk)
            else:
                # Wrong file format
                pass

            return HttpResponse(filename)

    # Using ?name=FILENAME&method=METHOD to POST image and get json
    blueprint_name = str(request.GET.get('name', '0'))
    name = blueprint_name[:-4] # remove '.jpg'
    method = str(request.GET.get('method', '0'))
    if (blueprint_name != '0'):
        if (method == 'space'):
            result_json = post_space(name)
            return HttpResponse(result_json)
        elif (method == 'text'):
            result_json = post_text(name)
            return HttpResponse(result_json)
        else:
            # wrong attr
            return HttpResponse('Wrong attr')
    else:
        # Using filenames in /blueprints to render table
        filenames = []
        for _, _, files in os.walk('./media'):
            filenames = files
        # Check if is processed
        json_names = []
        for _, _, files in os.walk('./jsons'):
            json_names = files
        files = []
        for f in filenames:
            # TODO 字符串匹配 判断method类型
            file_dist = {}
            file_dist["filename"] = f
            if f[:-4] + '_space.json' in json_names:
                file_dist["button_type_space"] = "btn btn-success"
            else:
                file_dist["button_type_space"] = "btn btn-primary"
            if f[:-4] + '_text.json' in json_names:
                file_dist["button_type_text"] = "btn btn-success"
            else:
                file_dist["button_type_text"] = "btn btn-primary"
            files.append(file_dist)

        return render(request, 'index.html', {"files": files})


def result(request):
    # Using ?name=FILENAME&method=METHOD
    blueprint_name = str(request.GET.get('name', '0'))
    method = str(request.GET.get('method', '0'))

    if (method == '0'):
        # TODO Show process time
        if (blueprint_name != '0'):
            # upload_time = '-'
            member_process_time = ''
            space_process_time = ''
            text_process_time = ''

            edge_group_number = ''
            edge_number = ''
            solid_wall_number = ''
            text_number = ''

            try:
                with open('jsons/'+blueprint_name[:-4]+'_space.json', 'r') as f:
                    result = json.load(f)
                edge_group_number = str(len(result["Edge_groups"]))
                edge_number = str(len(result["Edges"]))
                solid_wall_number = str(len(result['solid_walls']['others']) +
                                        len(result['solid_walls']['rectangle']) +
                                        len(result['solid_walls']['square']))
            except FileNotFoundError:
                # Blueprint is not processed yet
                space_process_time = '未处理'
                edge_group_number = '未处理'
                edge_number = '未处理'
                solid_wall_number = '未处理'

            try:
                with open('jsons/'+blueprint_name[:-4]+'_text.json', 'r', encoding='UTF-8') as f:
                    result = json.load(f)
                text_number = str(len(result["TextDetections"]))
            except FileNotFoundError:
                # Blueprint is not processed yet
                text_process_time = '未处理'
                text_number = '未处理'

            return render(request, 'view.html', {"filename": blueprint_name, "member_time":member_process_time,
                                                "space_time": space_process_time, "text_time": text_process_time,
                                                "edge_group_num": edge_group_number, "edge_num": edge_number,
                                                "solid_wall_num": solid_wall_number, "text_num": text_number})
    elif (method == 'member'):
        return result_member(request, blueprint_name)
    elif (method == 'space'):
        return result_space(request, blueprint_name)
    elif (method == 'text'):
        return result_text(request, blueprint_name)
    else:
        # Wrong Attributes
        return render(request, 'view.html', {"filename": blueprint_name})


def result_member(request, blueprint_name):
    return render(request, 'view_member.html', {"filename": blueprint_name})


def result_space(request, blueprint_name):
    # Draw edges and solid_walls using already saved json
    if (blueprint_name != '0'):
        try:
            with open('jsons/'+blueprint_name[:-4]+'_space.json', 'r') as f:
                result = json.load(f)
            squares = result['solid_walls']['square']
            edges = result['Edges']
            edge_group = result['Edge_groups']
            rects = []
            rects_edges = []
            grouped_edges = []
            # Get coordinate of the left-top point and the length and width
            for square in squares:
                rect = []
                rect.append(square[0][0])
                rect.append(square[0][1])
                rect.append(square[1][0] - square[0][0])
                rect.append(square[1][1] - square[0][1])
                rects.append(rect)

            for edge in edges:
                rect = []
                rect.append(edge[0][0])
                rect.append(edge[0][1])
                # Thicker if result is in 1-width line or point
                if edge[0][0] == edge[1][0]:
                    rect.append(6)
                else:
                    rect.append(edge[1][0] - edge[0][0])
                if edge[0][1] == edge[1][1]:
                    rect.append(6)
                else:
                    rect.append(edge[1][1] - edge[0][1])
                rects_edges.append(rect)

            for group in edge_group:
                edge_g = []
                for i in group:
                    edge_g.append(rects_edges[i])
                grouped_edges.append(edge_g)

            try:
                img = Image_PIL.open('media/'+blueprint_name[:-4]+'.jpg')
                width = img.size[0]
                height = img.size[1]
            except FileNotFoundError:
                # Blueprint is not transfered to .jpg
                
                return render(request, 'view.html')

            return render(request, 'view_space.html', 
                    {"rects": rects, "edges": rects_edges, "grouped_edges": grouped_edges, "filename": blueprint_name[:-4],
                    "width": width, "height": height})
        except FileNotFoundError:
            # Blueprint is not processed yet
             
            return render(request, 'view.html')


def result_text(request, blueprint_name):
    # TODO wrong bounding boxes
    if (blueprint_name != '0'):
        try:
            with open('jsons/'+blueprint_name[:-4]+'_text.json', 'r', encoding='UTF-8') as f:
                result = json.load(f)

            # Get path for drawing polygon in RaphaelJS
            polygon_path = []
            for res in result['TextDetections']:
                path = "M"
                for point in res['Polygon']:
                    path += str(point['X']) + " " + str(point['Y']) + " L"
                path = path[:-1]
                path += "Z"
                # Draw the text if including Chinese
                path_text = {}
                path_text['path'] = path
                path_text['start'] = res['Polygon'][0]
                #if is_Chinese(res['DetectedText']):
                if True:
                    path_text['text'] = res['DetectedText']
                else:
                    path_text['text'] = '0'
                polygon_path.append(path_text)

            try:
                img = Image_PIL.open('media/'+blueprint_name[:-4]+'.jpg')
                width = img.size[0]
                height = img.size[1]
            except FileNotFoundError:
                # Blueprint is not transfered to .jpg
                
                return render(request, 'view.html')

            return render(request, 'view_text.html', 
                    {"paths": polygon_path, "result": result['TextDetections'], "filename": blueprint_name[:-4],
                    "width": width, "height": height})

        except FileNotFoundError:
            # Blueprint is not processed yet
             
            return render(request, 'view.html')


def download(request):
    # JSON File Download
    blueprint_name = str(request.GET.get('name', '0'))

    if (blueprint_name != '0'):
        json_name_member = blueprint_name[:-4] + '_member.json'
        json_name_space = blueprint_name[:-4] + '_space.json'
        json_name_text = blueprint_name[:-4] + '_text.json'
        zip_file_name = blueprint_name[:-4] + '.zip'

        # Re-zip every download requests
        # May add zip files cache further
        with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
            try:
                zip_file.write('jsons/' + json_name_member)
            except FileNotFoundError: 
                pass
            try:
                zip_file.write('jsons/' + json_name_space)
            except FileNotFoundError: 
                pass
            try:
                zip_file.write('jsons/' + json_name_text)
            except FileNotFoundError: 
                pass
            zip_file.write('blueprints/' + blueprint_name)
            zip_file.write('media/' + blueprint_name[:-4] + '.jpg')
            
        zip_file = open(zip_file_name, 'rb')
        response = FileResponse(zip_file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition']='attachment;filename="'+ zip_file_name + '"'
        return response 


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def post_space(name):
    url = 'http://166.111.80.235:2929/get_info'
    with open('media/' + name +'.jpg', 'rb') as f:
        r = requests.post(url, files={'img': f})

    with open('jsons/' + name + '_space.json', 'wb') as f:
        f.write(r.content)

    return 'OK'


def post_text(name):
    url = 'http://s.thu.la:3080/ocr'
    with open('media/' + name +'.jpg', 'rb') as f:
        r = requests.post(url, files={'image': f})

    with open('jsons/' + name + '_text.json', 'wb') as f:
        f.write(r.content)

    return 'OK'
