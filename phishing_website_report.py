import requests
import os
import json
import re

domainName = 'kucoin-vip.com'


# https://www.coresentinel.com/phishing-take-phishing-site-offline/

# 抓host 和 registar
def collect_info_by_api(domainName):
    params = {
        'apiKey': 'at_1vNQiWuLq8CJgmE7Q4bQcVwgnGKVL',
        'domainName': domainName,
        'outputFormat': 'JSON'
    }
    base_url = f'https://www.whoisxmlapi.com/whoisserver/WhoisService'
    response = requests.get(base_url, params)
    response_data = response.json()
    # print(response_data)
    print(response_data['WhoisRecord']['registrant'])
    print(response_data['WhoisRecord']['contactEmail'])

    params = {
        'apiKey': 'at_1vNQiWuLq8CJgmE7Q4bQcVwgnGKVL',
        'domainName': domainName,
        'type': '_all',
        'outputFormat': 'JSON'
    }

    dns_lookup_url = f'https://www.whoisxmlapi.com/whoisserver/DNSService'
    # https://www.icann.org/compliance/complaint
    response = requests.get(dns_lookup_url, params=params)
    response_data = response.json()
    print(response_data)


def get_info_by_command(domainName):
    emails = []
    with os.popen(f'whois {domainName}') as fh:
        for line in fh.readlines():
            if '@' in line and 'abuse' in line.lower():
                email_regex = re.compile(r':.*@.*')
                email_finds = email_regex.findall(line)
                if len(email_finds) > 0:
                    email = email_finds[0]
                    email = email.replace(':', "")
                    email = email.replace(' ', '')
                    if email not in emails:
                        emails.append(email)
    print('registar abuse email address:', emails)
    return emails[0]


def extract_email(str):
    emails = []
    regex = re.compile(r'''[\w.+-]+@[\w-]+\.[\w.-]+''')
    emails_re = regex.findall(str)
    for email in emails_re:
        if email not in emails:
            emails.append(email)
    return emails


def get_host_abuse_emails(domain='www.kucoin-vip.com'):
    # get host ip
    # get ip's hoster
    # usage https://api-ninjas.com/profile https://www.whatismyip.com/api-documentation/

    apiKey = 'vJU1245BlXNzD85pW257Mw==9Dv5t6oKZLep0Yng'
    params = {
        'domain': domain,
    }
    headers = {'X-Api-Key': apiKey}
    # 先查 dns
    site_ip_endpoint = f'https://api.api-ninjas.com/v1/dnslookup'
    response = requests.get(site_ip_endpoint, params=params, headers=headers)
    site_ip = response.json()[0]['value']
    # 通过 dns获取的ip 查host
    whatismyip_apiKey = 'd780e472ed4f1ccb7247548f3302851d'
    ip_whois_endpoint = f'https://api.whatismyip.com/whois.php'
    params_whois = {
        'key': whatismyip_apiKey,
        'input': site_ip,
        'output': 'json'
    }

    response = requests.get(ip_whois_endpoint, params=params_whois)
    response_str = response.content.decode('utf-8')
    emails = extract_email(response_str)
    print('host abuse email address:', emails)


get_info_by_command(domainName)
get_host_abuse_emails()

# 提交公开的报告网站 部分 https://www.coresentinel.com/phishing-take-phishing-site-offline/

# 向相关方发送邮件
