import requests
import os
from io import BytesIO
import base64

RENDER_URL = "https://web-service-lab1.onrender.com"

print(f"Testing application at: {RENDER_URL}")

print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))
if os.path.exists('./static'):
    print("Files in static directory:", os.listdir('./static'))
else:
    print("Static directory does not exist")

try:
    r = requests.get(f'{RENDER_URL}/')
    print(f"Main page status: {r.status_code}")
    if r.status_code == 200:
        print("✓ Main page is working")
    else:
        print(f"✗ Main page error: {r.text}")
except Exception as e:
    print(f"✗ Main page request failed: {e}")

try:
    r = requests.get(f'{RENDER_URL}/data_to')
    print(f"Data page status: {r.status_code}")
    if r.status_code == 200:
        print("✓ Data page is working")
    else:
        print(f"✗ Data page error: {r.text}")
except Exception as e:
    print(f"✗ Data page request failed: {e}")

try:
    r = requests.get(f'{RENDER_URL}/net')
    print(f"Net page status: {r.status_code}")
    if r.status_code == 200:
        print("✓ Net page is working")
    else:
        print(f"✗ Net page error: {r.text}")
except Exception as e:
    print(f"✗ Net page request failed: {e}")

try:
    r = requests.get(f'{RENDER_URL}/denoise')
    print(f"Denoise page status: {r.status_code}")
    if r.status_code == 200:
        print("✓ Denoise page is working")
    else:
        print(f"✗ Denoise page error: {r.status_code}")
except Exception as e:
    print(f"✗ Denoise page request failed: {e}")

try:
    img_data = None
    path = os.path.join('./flaskapp/static','image0008.png')

    if os.path.exists(path):
        print("Testing denoise functionality with image...")

        with open(path, 'rb') as fh:
            files = {'upload': ('test_image.png', fh, 'image/png')}
            data = {'filter_type': 'gaussian', 'strength': '1.5'}

            res = requests.post(f'{RENDER_URL}/denoise', files=files, data=data, timeout=120)

            if res.ok:
                print("✓ Denoise form submission successful")
                if 'Original Image' in res.text and 'Processed Image' in res.text:
                    print("✓ Denoise processing completed successfully")
                else:
                    print("⚠ Denoise response received but content may be incomplete")
            else:
                print(f"✗ Denoise form submission failed: {res.status_code}")
    else:
        print(f"✗ Test image not found at: {path}")

except Exception as e:
    print(f"✗ Denoise functionality test failed: {e}")

try:
    img_data = None
    path = os.path.join('./flaskapp/static','image0008.png')

    if os.path.exists(path):
        with open(path, 'rb') as fh:
            img_data = fh.read()
            b64 = base64.b64encode(img_data)

        jsondata = {'imagebin': b64.decode('utf-8')}
        print("Sending image to API...")

        res = requests.post(f'{RENDER_URL}/apinet', json=jsondata, timeout=150)
        if res.ok:
            print("✓ API Response successful:")
            print(res.json())
        else:
            print(f"✗ API Error: {res.status_code} - {res.text}")
    else:
        print(f"✗ Test image not found at: {path}")

except Exception as e:
    print(f"✗ API request failed: {e}")


try:
    r = requests.get(f'{RENDER_URL}/apixml', timeout=150)
    print(f"XML API status: {r.status_code}")
    if r.status_code == 200:
        print("✓ XML API is working")
        # print(r.text)
    else:
        print(f"✗ XML API error: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ XML API request failed: {e}")
    exit(1)

print("\n" + "="*50)
print("Testing completed!")
