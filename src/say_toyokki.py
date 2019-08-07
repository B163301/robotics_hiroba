import plotly.offline as offline
import plotly.graph_objs as go
import numpy as np
import json
import os
import argparse
import MyClient


###############################################################################
# THIS CODE IS
# TOYOKKIに喋らせる
###############################################################################


def get_args():
    parser = argparse.ArgumentParser(description='データの図化')
    parser.add_argument('--inf', type=str, default='../data/data_sensor.json',
                        help='センサデータのjsonファイル')
    parser.add_argument('--mode', type=str, default='PH',
                        help='Humidity, temperature, PH, CO2')
    return parser.parse_args()


def load(filename):
    """
    JSON形式のファイルを読み込む

    Returns
    -------
    data : numpy.array of float
        センサ数 x データ点数
    dtime : numpy.array of str
        長さ=データ点数
    header : numpy.array of str
        長さ=センサ数
    """
    data = None
    dtime = None
    header = None
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        if len(data) == 0:
            return None, None, None
        dtime = [x for x in data.keys()]
        dtime = sorted(dtime)
        print(dtime)
        data = [data[x] for x in dtime]
        header = list(data[0].keys())
        data = [[float(d[h]) for d in data] for h in header]
        # YYYY/MM/DD/hh/mm/ss形式→MM/DD hh:mm形式
        dtime = ['{0[0]}/{0[1]} {0[2]}:{0[3]}'.format(x.split('/')[1:-1]) for x in dtime]
        data = np.array(data)
        dtime = np.array(dtime)
    return data[:, 0], dtime[0], header


if __name__ == '__main__':
    args = get_args()
    data, dtime, header = load(args.inf)
    idx = header.index(args.mode)
    if idx is not None:
        message = data[idx]
        print(message)
        client = MyClient.MyClient('192.168.24.61', '54333')
        params = {args.mode: message}
        body = client.send(params, page='')
