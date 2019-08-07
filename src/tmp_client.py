import time
import datetime

""" original modules """
import MyClient

""" DEFINE """
ipaddress = '192.168.2.103'
port = '12345'

if __name__=='__main__':
    client = MyClient.MyClient(ipaddress, port)
    while True:
        dt_now = datetime.datetime.now()
        data = dt_now.strftime('%Y-%m-%d_%H-%M-%S')
        params = {'nowtime':data}
        print('send:',params)
        client.send(params)
        time.sleep(1)
