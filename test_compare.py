from PIL import Image
import json
import base64

print('=== 原图 ===')
with Image.open(r'g:\AI code\trae\comfyui出图查看器\dist\[booru.plus]+pygmalion2011.png') as img:
    if 'chara' in img.info:
        chara_data = base64.b64decode(img.info['chara'])
        chara_raw = json.loads(chara_data.decode('utf-8'))
        
        print('顶层字段:')
        for key, value in chara_raw.items():
            if key == 'data':
                continue
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + '...'
            print(f'  {key}: {repr(value)}')
        
        print('\ndata 子对象:')
        if 'data' in chara_raw:
            for key, value in chara_raw['data'].items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + '...'
                print(f'  {key}: {repr(value)}')

print('\n=== 修改后的图 ===')
with Image.open(r'g:\AI code\trae\comfyui出图查看器\dist\[booru.plus]+pygmalion2011 - 副本.png') as img:
    if 'chara' in img.info:
        chara_data = base64.b64decode(img.info['chara'])
        chara_raw = json.loads(chara_data.decode('utf-8'))
        
        print('顶层字段:')
        for key, value in chara_raw.items():
            if key == 'data':
                continue
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + '...'
            print(f'  {key}: {repr(value)}')
        
        print('\ndata 子对象:')
        if 'data' in chara_raw:
            for key, value in chara_raw['data'].items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + '...'
                print(f'  {key}: {repr(value)}')
