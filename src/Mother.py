# マザープログラム
import datetime
import argparse
from MyClient import MyClient
from make_viewer import make_img_viewer_html
from make_figure import output_figure_html
import time
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import json
from collections import OrderedDict

# THIS CODE IS
# データ要求・データ受け取り・保存を自動で行う。


def get_args():
    parser = argparse.ArgumentParser(description='Mother')
    parser.add_argument('--delay_sensor', type=int, default=60, help='second')
    parser.add_argument('--delay_photo1', type=int, default=3600, help='second')
    parser.add_argument('--ip_sensor', type=str, default='192.168.24.64', help='IP address for Sensor raspberry pi')
    parser.add_argument('--ip_camera1', type=str, default='192.168.24.64', help='IP address for Camera1 raspberry pi')
    parser.add_argument('--ip_camera2', type=str, default='192.168.24.65', help='IP address for camera2 raspberry pi')
    parser.add_argument('--port', type=str, default='1880', help='Port for node-red of raspberry pi')
    parser.add_argument('--outf_sensor', type=str, default='../data/data_sensor.json', help='Output file of sensor data')
    parser.add_argument('--outf_fig_sensor', type=str, default='../src/interface/fig_sensor.html', help='Output file of figure of sensor ')
    parser.add_argument('--limit_point', type=int, default=20, help='Limit number of data point ')
    parser.add_argument('--outf_viewer', type=str, default='../src/interface/img_viewer.html', help='Output file of image viewer')
    parser.add_argument('--outdir_viewer', type=str, default='./photo/', help='Output directory of image viewer')
    parser.add_argument('--tmp_viewer', type=str, default='../src/tmp_img_viewer.txt', help='Template file of image viewer')
    parser.add_argument('--outf_savedphoto', type=str, default='../data/list_savedphoto.txt', help='Input file of name list of saved photo file')
    parser.add_argument('--outdir_photo', type=str, default='../src/interface/photo/', help='Output directory of photo file')
    return parser.parse_args()


def unescape(s):
    """
    Parameters
    ----------
    s : str

    Returns
    -------
    s : str
    """
    html_escapes = {'&quot;': '"',
                    '&#x2F;': '/'}
    for code, char in html_escapes.items():
        s = s.replace(code, char)
    return s


def save_sensor(outf, client):
    """
    Parameters
    ----------
    outf : str
    client : MyClient
    """
    print('save_sensor')
    # センサ値
    data_sensor = client.send({}, page='/getdata')
    if data_sensor is not None:
        data_sensor = data_sensor.decode()
        data_sensor = unescape(data_sensor)
        data_sensor = json.loads(data_sensor, object_pairs_hook=OrderedDict)
        if os.path.exists(outf):
            with open(outf, 'r') as f:
                old_data_sensor = json.load(f)
        else:
            print('\tthere are not old data')
            old_data_sensor = {}
        old_data_sensor.update(data_sensor)
        with open(outf, 'w') as f:
            json.dump(old_data_sensor, f, indent=4)
    else:
        print('\tdid not get data')


def save_camera(outf, outdir, client, page='getimg'):
    """
    Parameters
    ----------
    outf : str
        マザーに保存済みの画像ファイル名一覧のtxt file
    outdir : str
        Mother側の画像保存先ディレクトリ名
    client : MyClient Class
    page : str
        接続先ページ
    """

    def extract_datetimeoriginal(img):
        """
        Parameters
        ----------
        img: 
            GETコマンドに返信されてきたバイナリデータ

        Returns
        -------
        photoname: str
            撮影日時をYYYYMMDDHHMMSS形式の文字列で表したもの
        """
        img_bin = io.BytesIO(img)
        pil_img = Image.open(img_bin)
        modified_bin = io.BytesIO()
        pil_img.save(modified_bin, format='JPEG')
        exif = pil_img._getexif()
        for id, value in exif.items():
            if TAGS.get(id) == 'DateTimeOriginal':
                datestr = value
        datestr = datestr.replace(':', '')
        datestr = datestr.replace('-', '')
        photoname = datestr.replace(' ', '')
        return photoname

    print('save_camera')
    img = client.send({}, page)
    if img is not None:
        if img != b'None':
            photoname = extract_datetimeoriginal(img)
            print('\tgot {}'.format(photoname))
            filename = '{}photo_{}_{}.jpeg'.format(outdir, client.clientname, photoname)
            with open(filename, 'wb') as f:  # 画像を保存
                f.write(img)
            with open(outf, 'a') as f:  # 保存済み画像ファイル名を追記
                f.write(filename + '\n')
            return 'continue'
        else:
            print('\tcould not get(end)')
            return 'end'
    else:
        print('\tcould not get(error)')
        return 'error'


def take_camera(client, page='/shutter'):
    """
    client : str
        カメララズパイのMyClient
    page : str
        接続先ページ
    """
    print('take_camera')
    client.send({}, page)


if __name__ == '__main__':
    args = get_args()
    dt_before = datetime.datetime.now()
    sensor = MyClient(args.ip_sensor, args.port, clientname='sensor')
    camera1 = MyClient(args.ip_camera1, args.port, clientname='camera1')
    camera2 = MyClient(args.ip_camera2, args.port, clientname='camera2')
    while True:
        print('\n-----')
        dt_now = datetime.datetime.now()
        delta = dt_now - dt_before
        if (delta.total_seconds() > args.delay_photo1) or (delta.total_seconds() < 20):
            take_camera(camera1, page='/shutter1')
            # take_camera(camera2, page='/shutter2')
            dt_before = dt_now
        save_sensor(args.outf_sensor, sensor)
        output_figure_html(args.outf_sensor, args.outf_fig_sensor, args.limit_point)
        status = 'continue'
        while status == 'continue':
            status = save_camera(args.outf_savedphoto,
                                 args.outdir_photo,
                                 camera1,
                                 '/getimg1')
#        save_camera(args.outf_savedphoto,
#                    args.outdir_photo,
#                    camera2,
#                    '/getimg2')
        make_img_viewer_html(args.outf_savedphoto,
                             args.tmp_viewer,
                             args.outf_viewer,
                             args.outdir_viewer)
        time.sleep(args.delay_sensor)
