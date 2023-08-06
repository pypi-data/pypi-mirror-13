import oss2
import re

from .config import getConfigs,COMMON


def _get_endpoint(region):
    return 'http://oss-%s.aliyuncs.com' % region


def _get_bucket_client(obj=None):
    opt = getConfigs(COMMON, ['region', 'accesskeyid','accesskeysecret'])

    if obj:
        for k in obj:
            opt[k] = obj[k]

    if not opt or not opt.get('accesskeyid'):
        raise Exception('You need to login first')

    (bucket,key) = parse_osspath(opt.get('osspath'))

    auth = oss2.Auth(opt.get('accesskeyid'), opt.get('accesskeysecret'))
    bucket_client = oss2.Bucket(auth, _get_endpoint(opt.get('region')), bucket)
    return (bucket_client,key)


def check_client(opt=None):
    (client,key) = _get_bucket_client(opt)
    try:
        client.list_objects(key)
    except Exception as e:
        raise Exception(e.message)
    return 'ok'

def parse_osspath(oss_path):
    if not oss_path:
        return ("","")

    if oss_path.find('oss://')!=0:
        raise Exception('Invalid osspath, should start with "oss://"')

    oss_path = oss_path.lstrip('oss://')
    arr = oss_path.split('/',1)
    return (arr[0], arr[1])


def get_content(oss_path):
    (client,key) = _get_bucket_client({'osspath':oss_path})
    v = client.get_object(key).read()
    return v

def fetch_content_to_file(oss_path, file_path, progress_cb=None):
    (client,key) = _get_bucket_client({'osspath':oss_path})
    client.get_object_to_file(key, file_path, progress_callback=progress_cb)

def upload_file_to_oss(oss_path, file_path):
    (client,key) = _get_bucket_client({'osspath':oss_path})
    print(key, file_path)
    client.put_object_from_file(key, file_path)
