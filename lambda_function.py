import boto3
import os
import sys
import zipfile
import time
import module_load_function as mlf
from pprint import pprint
s3 = boto3.resource('s3')
rds = boto3.client('rds')
sys.path.append('/tmp')
mlf.load_ssl_auth('cooklab-recommend', s3)
mlf.load_pymysql('cooklab-payjp-subscription-status-update', s3)
mlf.load_payjp('cooklab-payjp-subscription-status-update', s3)
import pymysql
from datetime import datetime
import datetime
import payjp
start_time = time.time()

def get_db_data(rds):
  host = os.environ.get('DB_HOST')
  user = os.environ.get('DB_IAM_USER')
  db_name = os.environ.get('DB_NAME')
  password = rds.generate_db_auth_token(DBHostname=host, Port=3306, DBUsername=user)
  ssl = {'ca': '/tmp/rds-ca-2015-root.pem'}
  dt_now = datetime.datetime.now()
  mysql_connection = pymysql.connect(host=host, user=user, password=password, db=db_name, charset='utf8', cursorclass=pymysql.cursors.DictCursor, ssl=ssl)
  with mysql_connection.cursor() as cursor:
    sql = "SELECT * FROM `payments`, `users` WHERE payments.subscription_id is not NULL and payments.expires_at < %s and users.pay_regi_status = %s  order by payments.id"
    cursor.execute(sql,(dt_now, 2))
    mysql_connection.commit()
    results=cursor.fetchall()
  return results, mysql_connection

def update_subscription_status(rds):
  results, mysql_connection = get_db_data(rds)
  for r in results:
    if (time.time() - start_time) > 780:
      exit()
    try:
      payjp.api_key = os.environ.get('PAYJP_API_KEY')
      response = payjp.Subscription.retrieve(r['subscription_id'])
      if response['status'] == 'active':
        new_expires_at = datetime.datetime.fromtimestamp(response['current_period_end'])
        with mysql_connection.cursor() as cursor:
          sql = "UPDATE `payments` SET expires_at = %s  WHERE id = %s"
          cursor.execute(sql, (new_expires_at, r['id']))
          mysql_connection.commit()
      else:
        with mysql_connection.cursor() as cursor:
          sql = "UPDATE `users` SET pay_regi_status = %s  WHERE id = %s"
          cursor.execute(sql, ( 3, r['user_id']))
          mysql_connection.commit()
    except:
      continue
  mysql_connection.close()

def lambda_handler(event, context):
  update_subscription_status(rds)
