import requests
import os
import sys
import json

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


def get_current_ip():
    s = requests.get("http://ipinfo.io/ip")
    return s.content.decode('utf-8')

config = open_api_models.Config(
    access_key_id = os.getenv("ALICLOUD_ACCESS_KEY_ID"),
    access_key_secret = os.getenv("ALICLOUD_ACCESS_KEY_SECRET")
)
config.endpoint = f'alidns.cn-hangzhou.aliyuncs.com'
client = Alidns20150109Client(config)

def get_domain_record(domain_name, RR):
    describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
        domain_name=domain_name,
        rrkey_word=RR
    )
    runtime = util_models.RuntimeOptions()
    try:
        res = client.describe_domain_records_with_options(describe_domain_records_request, runtime).to_map()["body"]['DomainRecords']['Record']
        # print(res)
        for x in res:
            if x["RR"] == RR:
                return x
    except Exception as error:
        print(error)
        return None

def add_domain_record(domain_name, RR, value):
    add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
            domain_name=domain_name,
            rr=RR,
            type='A',
            value=value,
            ttl=600
        )
    runtime = util_models.RuntimeOptions()
    try:
        client.add_domain_record_with_options(add_domain_record_request, runtime)
    except Exception as error:
        print(error)

def update_domain_record(RR, record_id, value):
    update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
        record_id=record_id,
        rr=RR,
        type='A',
        value=value
    )
    runtime = util_models.RuntimeOptions()
    try:
        client.update_domain_record_with_options(update_domain_record_request, runtime)
    except Exception as error:
        print(error)

if __name__ == "__main__":
    domain_name = sys.argv[1]
    rr_record = sys.argv[2]
    current_ip = get_current_ip()
    print(current_ip)
    current_record = get_domain_record(domain_name, rr_record)
    print(current_record)
    if current_record == None:
        add_domain_record(domain_name, rr_record, current_ip)
        exit(0)
    record_id = current_record["RecordId"]
    record_ip = current_record["Value"]
    if record_ip != current_ip:
        update_domain_record(rr_record, record_id, current_ip)
