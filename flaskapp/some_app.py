print("Hello world")
from flask import Flask, render_template

from flask_wtf import FlaskForm, RecaptchaField
# from wtforms import StringField, SubmitField, TextAreaField
from wtforms import StringField, SubmitField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired

from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY

app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfXBgksAAAAAIHzKu-_MNePxVi9Z67Z_ZZOiV9F'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfXBgksAAAAAEK2_3jlgo5_o304LE6yhbpSCxxs'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)

class NetForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    recaptcha = RecaptchaField()
    submit = SubmitField('send')

class DenoiseForm(FlaskForm):
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    filter_type = SelectField('Filter Type', choices=[
        ('gaussian', 'Gaussian Blur'),
        ('median', 'Median Filter'),
        ('bilateral', 'Bilateral Filter'),
        ('nlm', 'Non-Local Means')
    ], default='gaussian')
    strength = FloatField('Filter Strength', validators=[
        NumberRange(min=0.1, max=10.0)], default=1.0)
    submit = SubmitField('Process Image')

@app.route("/")
def hello():
    return "<html><head></head><body>Hello World!</body></html>"

@app.route("/data_to")
def data_to():
    some_pars = {'user':'Ivan','color':'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html', some_str=some_str, some_value=some_value, some_pars=some_pars)

@app.route("/net", methods=['GET', 'POST'])
def net():
    form = NetForm()
    filename = None
    neurodic = {}

    if form.validate_on_submit():

        # filename = os.path.join('./static', secure_filename(form.upload.data.filename))
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', secure_filename(form.upload.data.filename))
        form.upload.data.save(filename)
        # neurodic = {"status": "Neural network temporarily disabled"}
        import net as neuronet
        img = Image.open(filename)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        decode = neuronet.getresult([img])
        # fcount, fimage = neuronet.read_image_files(10,'./static')
        # decode = neuronet.getresult(fimage)
        for elem in decode:
            # neurodic[elem[0][1]] = elem[0][2]
            neurodic[elem[0][1]] = f"{elem[0][2]:.4f}"

        print(f"DEBUG: Processed image {filename}, result: {neurodic}")

    return render_template('net.html', form=form, image_name=filename, neurodic=neurodic)

from flask import request
from flask import Response
import base64
from PIL import Image
# import PIL.Image as Image
from io import BytesIO
import json

@app.route("/apinet", methods=['GET', 'POST'])
def apinet():
    neurodic = {}

    try:

        if request.mimetype != 'application/json':
            return json.dumps({"error": "Only JSON requests accepted"}), 400

        data = request.get_json()
        if not data or 'imagebin' not in data:
            return json.dumps({"error": "No image data provided"}), 400

        print("DEBUG: Received API request")

        filebytes = data['imagebin'].encode('utf-8')
        cfile = base64.b64decode(filebytes)
        img = Image.open(BytesIO(cfile))

        print("DEBUG: Image decoded successfully")

        import net as neuronet
        decode = neuronet.getresult([img])

        print(f"DEBUG: Neural network result: {decode}")

        neurodic = {}
        for elem in decode:
            neurodic[elem[0][1]] = str(elem[0][2])

        print(f"DEBUG: Returning result: {neurodic}")

        ret = json.dumps(neurodic)
        resp = Response(response=ret, status=200, mimetype="application/json")
        return resp

    except Exception as e:
        print(f"ERROR in apinet: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

        return json.dumps({"error": f"Internal server error: {str(e)}"}), 500

import lxml.etree as ET

@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
    xml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'xml', 'file.xml')
    xslt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'xml', 'file.xslt')
    dom = ET.parse(xml_path)
    xslt = ET.parse(xslt_path)
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

@app.route("/denoise", methods=['GET', 'POST'])
def denoise():
    form = DenoiseForm()
    original_image = None
    processed_image = None
    color_plot = None
    noise_plot = None

    if form.validate_on_submit():
        try:
            # Читаем загруженное изображение
            image_file = form.upload.data
            img_array = np.frombuffer(image_file.read(), np.uint8)
            original_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if original_image is None:
                flash('Error: Could not read image file', 'danger')
                return render_template('denoise.html', form=form)

            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

            filter_type = form.filter_type.data
            strength = form.strength.data

            if filter_type == 'gaussian':
                kernel_size = max(3, int(strength * 2) * 2 + 1)
                kernel_size = min(kernel_size, 31)
                processed_image = cv2.GaussianBlur(original_image, (kernel_size, kernel_size), strength)

            elif filter_type == 'median':
                kernel_size = max(3, int(strength * 2) * 2 + 1)
                kernel_size = min(kernel_size, 15)
                processed_image = cv2.medianBlur(original_image, kernel_size)

            elif filter_type == 'bilateral':
                d = int(strength * 5)
                d = min(d, 15)
                processed_image = cv2.bilateralFilter(original_image, d, d*2, d/2)

            elif filter_type == 'nlm':

                h = strength * 10
                h = min(h, 30)
                processed_image = cv2.fastNlMeansDenoisingColored(original_image, None, h, h, 7, 21)

            # Создаем график распределения цветов
            color_plot = create_color_histogram(original_image, processed_image)

            # Создаем график распределения шума
            noise_plot = create_noise_analysis(original_image, processed_image)

            # Сохраняем изображения для отображения
            original_image = save_image_to_base64(original_image)
            processed_image = save_image_to_base64(processed_image)

        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')

    return render_template('denoise.html',
                         form=form,
                         original_image=original_image,
                         processed_image=processed_image,
                         color_plot=color_plot,
                         noise_plot=noise_plot)

def create_color_histogram(original, processed):

    plt.figure(figsize=(12, 4))

    try:
        # График для оригинального изображения
        plt.subplot(1, 2, 1)
        colors = ('r', 'g', 'b')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([original], [i], None, [256], [0, 256])
            plt.plot(hist, color=color, alpha=0.7)
        plt.title('Original Image Color Distribution')
        plt.xlabel('Color Value')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.legend(['Red', 'Green', 'Blue'])

        # График для обработанного изображения
        plt.subplot(1, 2, 2)
        for i, color in enumerate(colors):
            hist = cv2.calcHist([processed], [i], None, [256], [0, 256])
            plt.plot(hist, color=color, alpha=0.7)
        plt.title('Processed Image Color Distribution')
        plt.xlabel('Color Value')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.legend(['Red', 'Green', 'Blue'])

        plt.tight_layout()
        return save_plot_to_base64()
    except Exception as e:
        print(f"Error creating color histogram: {e}")
        return None

def create_noise_analysis(original, processed):

    plt.figure(figsize=(12, 4))

    try:
        # Вычисляем разницу (шум)
        noise = cv2.absdiff(original, processed)

        # График распределения шума по каналам
        plt.subplot(1, 2, 1)
        colors = ('r', 'g', 'b')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([noise], [i], None, [256], [0, 256])
            plt.plot(hist, color=color, alpha=0.7)
        plt.title('Noise Distribution by Channel')
        plt.xlabel('Noise Intensity')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.legend(['Red', 'Green', 'Blue'])

        # График общего распределения шума
        plt.subplot(1, 2, 2)
        noise_gray = cv2.cvtColor(noise, cv2.COLOR_RGB2GRAY)
        plt.hist(noise_gray.ravel(), bins=50, alpha=0.7, color='purple', edgecolor='black')
        plt.title('Overall Noise Distribution')
        plt.xlabel('Noise Intensity')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        return save_plot_to_base64()
    except Exception as e:
        print(f"Error creating noise analysis: {e}")
        return None

def save_image_to_base64(image):

    try:
        from PIL import Image as PILImage
        from io import BytesIO

        img_pil = PILImage.fromarray(image)
        buffer = BytesIO()
        img_pil.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error saving image to base64: {e}")
        return None

def save_plot_to_base64():

    try:
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graphic = base64.b64encode(image_png).decode()
        plt.close()  # Важно закрыть figure
        return f"data:image/png;base64,{graphic}"
    except Exception as e:
        print(f"Error saving plot to base64: {e}")
        plt.close()
        return None

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
