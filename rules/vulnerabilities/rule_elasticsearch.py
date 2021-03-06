from core.redis   import rds
from core.triage  import Triage
from core.parser  import ScanParser, ConfParser

class Rule:
  def __init__(self):
    self.rule = 'VLN_77D7'
    self.rule_severity = 2
    self.rule_description = 'Checks for Open Elasticsearch instances'
    self.rule_confirm = 'Identified an open Elasticsearch'
    self.rule_details = ''
    self.rule_mitigation = '''Identify whether ElasticSearch should allow access to any local network host.'''
    self.rule_match_string = {
                              '/_cat/indices?v':{
                                'app':'ELASTICSEARCH1',
                                'match':['"took":'],
                                'title':'Elastic Search'
                                },
                               '/_all/_search':{
                                'app':'ELASTICSEARCH2',
                                'match':['"took":'],
                                'title':'Elastic Search'
                                },
                           }
    
    self.intensity = 3
    
  def check_rule(self, ip, port, values, conf):
    c = ConfParser(conf)
    t = Triage()
    p = ScanParser(port, values)
    
    domain = p.get_domain()
    module = p.get_module()
    
    if port != 9200:
      return
    
    if 'http' in module:
      for uri, values in self.rule_match_string.items():
        app_name = values['app']
        app_title = values['title']
  
        resp = t.http_request(ip, port, uri=uri)

        if resp is not None:
          for match in values['match']:
            if match in resp.text:
              self.rule_details = 'Exposed {} at {}'.format(app_title, uri)
              js_data = {
                  'ip':ip,
                  'port':port,
                  'domain':domain,
                  'rule_id':self.rule,
                  'rule_sev':self.rule_severity,
                  'rule_desc':self.rule_description,
                  'rule_confirm':self.rule_confirm,
                  'rule_details':self.rule_details,
                  'rule_mitigation':self.rule_mitigation
                }
              rds.store_vuln(js_data)
              return
    return
