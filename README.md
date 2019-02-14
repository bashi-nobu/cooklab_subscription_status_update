## File

- lambda_function.py: Lambda関数
- module_load_function.py: Pythonモジュール


## Structure

30分おきにLambda関数をCloud Whachから実行し DB(rds)から定額課金ユーザーでかつ定額課金の有効期限(expired_at)が現在時間よりも過去の状態になっているレコードをpaymentsテーブルから取得する
そのレコードごとにsubscription idデータを使ってPayjpにアクセスし、最新の定額課金状況を確認する
ステータスがactiveになっていれば有効期間(current_period_end)を用いてexpired_atを更新する
もしステータスがactiveではない場合は該当するユーザーの usersテーブルのpay_regi_statusカラムを3に変更
15分がLambdaのタイムアウト時間のため、処理開始から13分経過時点で処理終了

