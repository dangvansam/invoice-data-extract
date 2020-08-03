from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import  request, HttpResponse
from django.conf import settings
#from django.core.files.storage import FileSystemStorage
from .utils import binary2json
import json
from .models import Config
from .forms import ConfigForm
import  shutil
import os
from CRAFTpytorch.match_with_json import ocr
from CRAFTpytorch.preprocess import preprocess

# Create your views here.
def index(request):
    return render(request, 'home.html')

def upload(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Config.objects.filter(name = name).count() != 0:
                return render(request,"upload.html",{"form": form,"message": "filename already exist!"})
            else:
                form.save()
                image_name = form.cleaned_data['image']
                print('name:',form.cleaned_data['name'])
                print('image:',form.cleaned_data['image'])
                data = {'name':name, 'image_name':image_name}
                #return render(request, 'draw.html', context=data)
                return redirect("edit", config_name=name)
    else:
        form = ConfigForm()
    return render(request, 'upload.html', context={'form': form})

def upload_image(request):
    if request.method == 'POST':
        image_file = request.FILES['file']
    return render(request, 'upload_image.html')

def preprocess_image(request, config_name, filename, pp):
        config = Config.objects.get(name=config_name)
        config_filepath = settings.MAU_URL+config_name+'.json'
        img_config_filepath = settings.MAU_URL+str(config.image)
        print("config_filepath:",config_filepath)
        print("img_config_filepath:",img_config_filepath)
        #img_config_filepath = settings.MAU_URL+config_name+'.png'
        with open(config_filepath, encoding="UTF-8") as fi:
            json_config = json.load(fi)
        print(config)
        filename = str(filename)
        #print("in_filepath:",in_filepath)
        #out_filepath2 = settings.MEDIA_URL+out_filename2
        in_filepath = settings.MEDIA_URL+filename
        out_filepath2 = in_filepath.split('.',-1)[0] + "_result." + in_filepath.split('.',-1)[1]
        out_filename2 = filename.split('.',-1)[0] + "_result." + filename.split('.',-1)[1]
        print("out_filepath2:",out_filepath2)

        #pp = False
        if pp:
            out_filepath = preprocess(in_filepath, img_config_filepath)
            #out_filepath = preprocess(in_filepath, None, json_config_path=config_filepath)
        else:
            out_filepath = in_filepath
        ocr(out_filepath, config_filepath, out_filepath2)
        return render(request, "preprocess_image.html", {"config":config, "json_config":json_config, "filename":filename, "out_filename2":out_filename2})

def select_demo(request, config_name, filename, pp):
    return preprocess_image(request, config_name, filename, bool(pp))

def select(request, config_name):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return render(request, 'upload_image.html', {"config_name":config_name})
            
        pp = request.POST.get('checkbox')
        if not pp:
            pp = False
        else:
            pp = True
        print("Preprocess image:",pp)
        image_file = request.FILES['file']
        file_path = settings.MEDIA_URL+str(image_file)
        filename = str(image_file)
        with open(file_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        #saved file to /upload
        return preprocess_image(request, config_name, filename, pp)
    else:
        return render(request, 'upload_image.html', {"config_name":config_name})

def getlist(request):
    configs = Config.objects.all()
    return render(request, 'list.html', {'list_config':configs})

def detail(request, config_name):
    if request.method == "GET":
        config = Config.objects.get(name=config_name)
        with open(settings.MAU_URL+config_name+'.json', encoding="UTF-8") as fi:
            json_config = json.load(fi)
        return render(request, 'detail.html', context={'config':config, 'json_config': json_config})

def delete(request, config_name):
    del_obj = Config.objects.get(name=config_name)
    #print(del_obj)
    del_obj.delete()
    return redirect("getlist")

def edit(request, config_name):
    
    config = Config.objects.get(name=config_name)

    if request.method == "GET":
        # xem mẫu nếu mẫu có file config hiển thị file config
        if os.path.exists(settings.MAU_URL+config_name+'.json'):
            with open(settings.MAU_URL+config_name+'.json', encoding="UTF-8") as fi:
                json_config = json.load(fi)
            return render(request, 'edit.html', context={'config':config, 'json_config': json_config})
        # nếu không không hiển thị
        else:
            return render(request, 'edit.html', context={'config':config, 'json_config': None}) #name, image, 
    
    elif request.method == "POST":
        if request.is_ajax():
            data = binary2json(request.body)
            print(data)
            scale = data["scale"] #lấy tỉ lệ ảnh gốc và ảnh hiển thị trên trình duyệt khi người dùng tạo mẫu. để đưa tọa độ về kích thước ảnh gốc
            name_fields = data["rectnames"]
            boxs = data["rectangles"]
            boxs = [list(b.values()) for b in boxs]
            boxs_osize = []
            for b in boxs:
                boxs_osize.append([int(e/scale) for e in b])
            #boxs = boxs*scale
            boxs = [dict(zip(["x","y","width","height"],b)) for b in boxs]
            value_positions = data["value_positions"]
            num_lines = data["num_lines"]
            json_config = {"name_fields":name_fields, "boxs":boxs_osize, "value_positions":value_positions, "num_lines":num_lines}
            #lưu mẫu từ phía người dùng vừa tạo vào file json
            with open(settings.MAU_URL+config_name+'.json', 'w') as f:
                json.dump(json_config, f)

            image_path = str(config.image)
            print(settings.MEDIA_URL+image_path, settings.MAU_URL+image_path)
            shutil.copy(settings.MEDIA_URL+image_path, settings.MAU_URL+image_path)
            res_data = {"success":True}
            return HttpResponse(json.dumps(res_data), content_type='application/json')
        else:
            #khi người dùng upload file json lên
            print(request.FILES["file"].read())
            myfile = request.FILES['file'].read()
            json_config = binary2json(myfile)
            print(json_config)
            # trả về mẫu mà người dùng upload hiển thị trên trình duyệt
            # có thể chỉnh sửa sau đó lưu mẫu. nếu có mẫu cũ sẽ ghi đè mẫu cũ
            return render(request, 'edit.html', context={'config':config, 'json_config': json_config})

