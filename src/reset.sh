# 初期化　データの吸出し後などに行う

# sensor data
# data_sensor.jsonを削除
dataf="../data/data_sensor.json"
command="rm $dataf"
echo $command
eval $command

# photo data
# 全ての写真データを削除
photof="./interface/photo/*"
command="rm $photof"
echo $command
eval $command
# 保存済み写真リストを空にする
savedphotof="../data/list_savedphoto.txt"
command="rm $savedphotof"
echo $command
eval $command
command="touch $savedphotof"
echo $command
eval $command
# 撮影済み写真リストを削除する
takenphotof="../data/list_takenphoto.txt"
command="rm $takenphotof"
echo $command
eval $command
takenphotof="../data/list_takenphoto2.txt"
command="rm $takenphotof"
echo $command
eval $command

# LED設定ファイルの存在を確認する。
ledf="../data/configure.txt"
if [ -e $ledf ]; then
	# 存在する場合
	echo "$ledf OK"
else
	command="echo '2,3' > $ledf"
	echo $command
	eval $command
fi
