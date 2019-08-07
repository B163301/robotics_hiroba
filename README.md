# ロボティクス広場用

## flow_LEDpi.json
http endpointです。

- http GETでLEDの点灯消灯時刻の設定を受け取る
- 一時間に一度、現在時刻と設定時刻を照らし合わせ、該当時刻にはon/off命令を、非該当時刻にはnoneを出す

## flow_SENSORpi.json
http endpointです。

- http GETでセンサ値の要求を受け、保存していたセンサ値を読み出し、返す
- arduinoからのJSONファイルを受け取り、保存する

## flow_CAMERApi.json
http endpointです。

- http GETで画像の要求を受け、画像を返す
- http GETでシャッタ命令を受け、画像を撮影する
