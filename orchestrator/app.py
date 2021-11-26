import pandas as pd
import json
import requests
import os

from utils import expand_config_template

def build_scenarios():
    conf_file = open(os.environ.get('CONFIG_FILE'), 'r')
    conf = json.load(conf_file)

    failure_rate = conf['failure_rate']
    patterns = conf['patterns']
    users = conf['concurrentUsers']
    rounds = conf['rounds'] + 1
    envoy_host = conf['envoy_host']
    scenarios = []

    for failure in failure_rate:
        for pattern_template in patterns:
            config_templates = expand_config_template(pattern_template['config_template'])
            for config_template in config_templates:
                for user in users:
                    for idx_round in range(1, rounds):
                        scenarios.append({
                            'config_template': config_template,
                            'pattern_template': pattern_template,
                            'user': user,
                            'round': idx_round,
                            'failure': failure,
                            'envoy_host': envoy_host
                        })
    return scenarios


def main():
    scenarios = build_scenarios()
    results = []
    total_scenarios = len(scenarios)
    for idx, scenario in enumerate(scenarios):
        user = scenario['user']
        pattern_template = scenario['pattern_template']
        failure = scenario['failure']
        config_template = scenario['config_template']
        round = scenario['round']
        
        print(f'Round [{idx}/{total_scenarios}] Users {user} Pattern {pattern_template["name"]}')

        status_code, result = do_test(config_template, pattern_template, user)
        if status_code != 200:
            result = [{
                'error': True,
                'error_message': result
            }]
        
        for item_result in result:
            item_result['users'] = user
            item_result['round'] = round
            item_result['lib'] = pattern_template['lib']
            item_result['name'] = pattern_template['name']
            item_result['failure_rate'] = failure
            for config_key in config_template.keys():
                item_result[config_key] = config_template[config_key]
        
        results += result

        if idx % 100 == 0:
            export(f'{idx}.csv', results)
    export(f'total-{idx}.csv', results)

def export(filename, data):
    df = pd.DataFrame(data)
    df.to_csv(f'{os.environ.get("OUTPUT_PATH")}/{filename}', index=False)

def update_env(server_host, failure):
    pass

def do_test(config_template, pattern, users):
    payload = {
            'concurrentUsers': users,
            'maxRequestsAllowed': 1000,
            'targetSuccessfulRequests': 25,
            'params': config_template
        }
    response = requests.post(pattern['url'], data=json.dumps(payload), headers={'Content-Type': 'application/json'})
    result = response.text
    if response.status_code == 200:
        result = response.json()

    return response.status_code, result

main()
# s = build_scenarios()
# j = json.dumps(s, indent=4)
# f = open('./scenarios-1.json', 'w')
# f.write(j)
