# マザープログラム
import datetime
import argparse
from MyClient import MyClient
from make_viewer import make_img_viewer_html
from make_figure import output_figure_html
import time
import os
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
    parser.add_argument('--outf_viewer', type=str, default='../src/interface/img_viewer.html', help='Output file of image viewer')
    parser.add_argument('--outdir_viewer', type=str, default='./photo/', help='Output directory of image viewer')
    parser.add_argument('--tmp_viewer', type=str, default='../src/tmp_img_viewer.txt', help='Template file of image viewer')
    parser.add_argument('--inf_takenphoto1', type=str, default='../data/list_takenphoto1.txt', help='Input file of name list of taken photo file on raspberry pi')
    parser.add_argument('--inf_takenphoto2', type=str, default='../data/list_takenphoto2.txt', help='Input file of name list of taken photo file on raspberry pi')
    parser.add_argument('--outf_savedphoto', type=str, default='../data/list_savedphoto.txt', help='Input file of name list of saved photo file')
    parser.add_argument('--outdir_photo', type=str, default='../src/interface/photo/', help='Output directory of photo file')
    parser.add_argument('--outdir_photo1', type=str, default='../data/photo1/', help='DEBUG mode; Output directory of photo file on raspberry pi')
    parser.add_argument('--outdir_photo2', type=str, default='../data/photo2/', help='DEBUG mode; Output directory of photo file on raspberry pi')
    parser.add_argument('--debug', action='store_true')
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


def save_camera(inf, outf, outdir, client, page='getimg'):
    """
    Parameters
    ----------
    inf : str
        新たに撮影された画像ファイル名一覧のtxt file
    outf : str
        マザーに保存済みの画像ファイル名一覧のtxt file
    outdir : str
        Mother側の画像保存先ディレクトリ名
    client : MyClient Class
    page : str
        接続先ページ
    """
    print('save_camera')
    if os.path.exists(inf):
        with open(inf, 'r') as f:
            photonames = f.read().split('\n')[:-1]  # 新たに撮影された画像ファイル名一覧
        flag_rm = True
        for photoname in photonames:
            img = client.send({'name': photoname}, page)
            if img is not None:
                print('\tgot {}'.format(photoname))
                filename = '{}photo_{}_{}.jpeg'.format(outdir, client.clientname, photoname)
                with open(filename, 'wb') as f:  # 画像を保存
                    f.write(img)
                with open(outf, 'a') as f:  # 保存済み画像ファイル名を追記
                    f.write(filename + '\n')
            else:
                print('\tcould not get {}'.format(photoname))
                flag_rm = False
        if flag_rm:
            os.remove(inf)
    else:
        print('\ttakenphoto does not exist')


def take_camera(client, photoname, outf, debug, outdir='', page='/shutter'):
    """
    client : str
        カメララズパイのMyClient
    photoname : str
        新たに撮影する画像名
    outf : str
        新たに撮影された画像ファイル名一覧のtxt file
    debug : bool
        Trueならば、撮影した画像の代わりのファイルを用意
    outdir : str
        Raspberry Pi側の画像保存先ディレクトリ名。debug Trueのときのみ必要。
    page : str
        接続先ページ
    """
    print('take_camera {}'.format(photoname))
    client.send({'name': photoname}, page)
    if debug:
        filename = '{}photo_{}.jpeg'.format(outdir, photoname)
        with open(filename, 'w') as f:
            f.write('test')
    with open(outf, 'a') as f:
        f.write(photoname + '\n')


if __name__ == '__main__':
    args = get_args()
    dt_before = datetime.datetime.now()
    sensor = MyClient(args.ip_sensor, args.port, clientname='sensor')
    camera1 = MyClient(args.ip_camera1, args.port, clientname='camera1')
    camera2 = MyClient(args.ip_camera2, args.port, clientname='camera2')
    while True:
        print('\n-----')
        dt_now = datetime.datetime.now()
        # if True:
        delta = dt_now - dt_before
        if (delta.total_seconds() > args.delay_photo1) or (delta.total_seconds() < 20):
            dt_now_str = dt_now.strftime('%Y%m%d%H%M%S')
            take_camera(camera1, dt_now_str, args.inf_takenphoto1, args.debug, outdir=args.outdir_photo1, page='/shutter1')
            # take_camera(camera2, dt_now_str, args.inf_takenphoto2, args.debug, outdir=args.outdir_photo2, page='/shutter2')
            dt_before = dt_now
        save_sensor(args.outf_sensor, sensor)
        output_figure_html(args.outf_sensor, args.outf_fig_sensor)
        save_camera(args.inf_takenphoto1,
                    args.outf_savedphoto,
                    args.outdir_photo,
                    camera1,
                    '/getimg1')
#         save_camera(args.inf_takenphoto2,
#                     args.outf_savedphoto,
#                     args.outdir_photo,
#                     camera2,
#                     '/getimg2')
        make_img_viewer_html(args.outf_savedphoto,
                             args.tmp_viewer,
                             args.outf_viewer,
                             args.outdir_viewer)
        time.sleep(args.delay_sensor)
