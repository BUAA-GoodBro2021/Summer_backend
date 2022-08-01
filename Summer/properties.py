# 邮件信息
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 腾讯QQ邮箱SMTP服务器地址
EMAIL_PORT = 25  # SMTP服务器端口号
EMAIL_HOST_USER = '3044039051@qq.com'  # 发送邮件的QQ邮箱
EMAIL_HOST_PASSWORD = 'zosulotgxochdehe'  # 授权码
EMAIL_USE_TLS = False  # 与SMTP服务器通信时，是否启动TLS链接（安全链接）默认False
EMAIL_FROM_NAME = 'Super2021'

# 对象存储信息
bucket_secret_id = 'AKIDNZVAYfV5NO9dqmTv5zcz4sPggPr2yc07'
bucket_secret_key = 'sTnqc7LJ0Q2NREl10h8IBn8CyTigNo31'
bucket_app_id = '-1309504341'
bucket_region = 'ap-beijing'
bucket_access = 'public-read'

# MySQL数据库配置
mysql_ENGINE = 'django.db.backends.mysql'
mysql_NAME = 'summer'
mysql_USER = 'buaa2021'
mysql_PASSWORD = 'buaa(2021)'
mysql_HOST = 'rm-wz974lh9hz3g6w0k5ko.mysql.rds.aliyuncs.com'
mysql_PORT = '3306'

# Redis数据库配置
redis_BACKEND = "django_redis.cache.RedisCache"
redis_HOST = "152.136.213.16"
redis_TIMEOUT = 3600 * 24 * 3  # 缓存保存时间，单位秒，默认300
redis_MAX_ENTRIES = 600  # 缓存最大数据条数
redis_CULL_FREQUENCY = 3  # 缓存条数到达最大值时，删除1/x的缓存数据
redis_CLIENT_CLASS = "django_redis.client.DefaultClient"
redis_PASSWORD = "super2021"
redis_PORT = 6379

# 查看IP地址
aliyun_appcode = '1437a6fc99dc4078bfe01338d7132c2c'  # 开通服务后 买家中心-查看AppCode

# token加密所需的密钥
TOKEN_SECRET_KEY = 'django-insecure-t$d4)i^$r0kzrn&b1ch0xcgh9^u+0a0ob98^jkg3lu2y6yq(w0'

# 默认图片地址
default_favorite_url = 'https://global-1309504341.cos.ap-beijing.myqcloud.com/default-favorite.jpg'
default_avatar_url = 'https://global-1309504341.cos.ap-beijing.myqcloud.com/default.jpg'
default_avatar_url_match = 'https://random-avatar-1309504341.cos.ap-beijing.myqcloud.com/'

# 环境路由
local_base_url = "http://127.0.0.1:8000"
production_base_url = "https://summer.super2021.com"
