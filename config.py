import os

basedir = os.path.dirname(os.path.abspath(__file__))
app_name = os.environ['APP_NAME']

# Настройки API - Получите на https://my.telegram.org
api_id = os.environ['TG_API_ID']
api_hash = os.environ['TG_API_HASH']

target_group_id = int(os.environ['TG_TARGET_GROUP_ID'])

openrouter_api_key = os.environ['OPENROUTER_KEY']
model = os.environ['MODEL']

use_log_messages = (os.environ['USE_LOG_MESSAGES'] == '1')

use_only_targets = (os.environ['USE_ONLY_TARGETS'] == '1')
