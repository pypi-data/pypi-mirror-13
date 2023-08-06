# dictionary for ELB presentation meta data
elbPres_meta = dict()
elbPres_meta['num'] = {'len': '%-5s', 'tit': '#', 'ul': '-'}
elbPres_meta['date'] = {'len': '%-22s', 'tit': 'Creation Time', 'ul': '-------------'}
elbPres_meta['name'] = {'len': '%-19s', 'tit': 'Name', 'ul': '----'}
elbPres_meta['vpcid'] = {'len': '%-15s', 'tit': 'VPC ID', 'ul': '------'}
elbPres_meta['zone'] = {'len': '%-25s', 'tit': 'Zones', 'ul': '-----'}
elbPres_meta['scheme'] = {'len': '%-18s', 'tit': 'Scheme', 'ul': '------'}
elbPres_meta['inst'] = {'len': '%-49s', 'tit': 'Instances', 'ul': '---------'}
elbPres_meta['sgname'] = {'len': '%-25s', 'tit': 'Security Groups', 'ul': '---------------'}

# dictionary for ELB node fields
elb_flds = ['num', 'date', 'name', 'vpcid', 'zone', 'scheme', 'inst', 'sgname']

# jinja2 template to print ELB nodes
elb_template = \
"""
{% for v in flds -%}
{{ "%s" % (pres[v]['len']) % (pres[v]['tit']) }}
{%- endfor %}
{% for v in flds -%}
{{ "%s" % (pres[v]['len']) % (pres[v]['ul']) }}
{%- endfor %}

{% for n in nodes -%}
{%- for v in flds -%}
{%- if v in ['zone', 'inst', 'sgname'] -%}
{{ "%s" % (pres[v]['len']) % (n[v]|join(', ')) }}
{%- else -%}
{{ "%s" % (pres[v]['len']) % (n[v]) }}
{%- endif -%}
{%- endfor %}

{% endfor %}
"""

########################################################################################################################

# dictionary for EC2 presentation meta data
ec2Pres_meta = dict()
ec2Pres_meta['ltime'] = {'len': '%-22s', 'tit': 'Launch Time', 'ul': '-----------'}
ec2Pres_meta['env'] = {'len': '%-12s', 'tit': 'Env (tag)', 'ul': '---------'}
ec2Pres_meta['id'] = {'len': '%-13s', 'tit': 'AWS-ID', 'ul': '------'}
ec2Pres_meta['state'] = {'len': '%-13s', 'tit': 'State', 'ul': '-----'}
ec2Pres_meta['name'] = {'len': '%-34s', 'tit': 'Name (tag)', 'ul': '----------'}
ec2Pres_meta['sgname'] = {'len': '%-40s', 'tit': 'Security Groups', 'ul': '---------------'}
ec2Pres_meta['kpname'] = {'len': '%-14s', 'tit': 'KP Name', 'ul': '-------'}
ec2Pres_meta['spacer'] = {'len': '%-6s', 'tit': '==>', 'ul': '---'}
ec2Pres_meta['cmd'] = {'len': '%-12s', 'tit': 'Command', 'ul': '-------'}

# dictionary for EC2 node fields
ec2_flds = ['ltime', 'env', 'id', 'state', 'name', 'sgname', 'kpname', 'spacer', 'cmd']

# jinja2 template to print EC2 instances
ec2_template = \
"""
{% for v in flds -%}
{{ "%s" % (pres[v]['len']) % (pres[v]['tit']) }}
{%- endfor %}
{% for v in flds -%}
{{ "%s" % (pres[v]['len']) % (pres[v]['ul']) }}
{%- endfor %}

{% for i in insts -%}
{%- set outerloop = loop -%}
{%- for v in flds -%}
{%- if v == 'sgname' -%}
{{ "%s" % (pres[v]['len']) % (i[v]|join(', ')) }}
{%- elif v == 'spacer' -%}
{{ "%s" % (pres[v]['len']) % (pres[v]['tit']) }}
{%- else -%}
{{ "%s" % (pres[v]['len']) % (i[v]) }}
{%- endif -%}
{%- endfor %}

{% endfor %}
"""
