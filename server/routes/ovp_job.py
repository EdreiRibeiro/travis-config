# -*- coding: utf-8 -*-
import os
import socket
import traceback
import time
import datetime
import sys
from collections import OrderedDict
from operator import itemgetter
from urlparse import urlparse, parse_qs
import xml.dom.minidom

# import xmltodict as xmltodict
import json

# from cloudant.client import Cloudant
# from cloudant.result import Result
from cloudant.design_document import DesignDocument
# from cloudant.database import CloudantDatabase

from concur import ConcurClient

####################
####ENV IMPORTS#####
####################
##--CLOUDANT--##
# from chaves_ibm_util.cloudant_bluemix_vars import CloudantDedicatedBleumix,handle_db,manageIndex,chunker ##DEPEND##

####PROD CONCUR#####
concur = ConcurClient(username='WebAdmin@us.ibm.com', password='Welcome1', consumerKey='NaCwFkAdAJLim8nSA4qX7t') #prod

##TEST CONCUR######
# concur = ConcurClient(username='WebAdmin@ibm.com', password='Welcome1?', consumerKey='FYB8YBa5ggY9HBEETbraKk', base_url='https://implementation.concursolutions.com')  # test


#=================================================================================
# def loadEnv(filename_path_str):
#     import re
#
#     envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
#     results = {}
#     with open(filename_path_str) as ins:
#         for line in ins:
#             match = envre.match(line)
#             if match is not None:
#                 results[match.group(1)] = match.group(2)
#
#     return results
#
# results = loadEnv('.local_python')  # PYTHON VARIABLES FILE




# client = CloudantDedicatedBleumix() #Cloudant

SOCKET_TIMEOUT = 60*10

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def manageIndex(db_name,document_id,index_name, search_func, analyzer="keyword"):
    try:
        if DesignDocument(db_name, document_id=document_id).exists():
            des_doc = db_name.get_design_document(document_id)
        else:
            des_doc = DesignDocument(db_name, document_id=document_id)

        if index_name in des_doc.list_indexes():
            idx_get = des_doc.get_index(index_name)
            if not (idx_get['index'] == search_func) or not (idx_get['analyzer'] == analyzer):  # index func changed
                des_doc.delete_index(index_name)
                print 'deleted'
                des_doc.add_search_index(index_name=index_name, search_func=search_func, analyzer=analyzer)
        else:
            des_doc.add_search_index(index_name=index_name, search_func=search_func, analyzer=analyzer)

        des_doc.save()
    except:
        print sys.exc_info()

def handle_db(client,db_name):
    # db_name = 'feedback-backup'
    client.connect()
    # print 'db_name:', db_name, '  - All dbs:', client.all_dbs()
    if db_name not in client.all_dbs():
        # print "Nova db criado:",db_name
        db_name = client.create_database(db_name)
    else:
        # print "Db jah existe:", db_name
        db_name = client[db_name]
    return db_name

def gen_dict_extract(key, var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result

def genericSearchResults(limit=100, nextPage=None, api_url=None, resp_key=None, params_ext=None, headers_ext=None):

    # url = 'v3.0/expense/reports/'
    # url = 'v3.0/expense/entries/'
    # url = 'v3.0/common/users/'
    # url = 'v3.0/expense/receiptimages/'
    # url = 'image/v1.0/expenseentry/gWonjE$prhaSd7DMzt3iGi1EcpjI3UNHOjwQ'
    # url = 'v3.0/expense/expensegroupconfigurations'
    # url = 'user/v1.0/user'
    # url = 'expense/expensereport/v2.0/report/BF93E2AB86D746F1B219' #TEST
    # url = 'expense/expensereport/v2.0/report/5B38C4A2F6EB4C8AB561'
    # url = 'expense/expensereport/v2.0/report/DFCC33713E5946DBA05A' #JP SECONDEE
    # url = 'expense/expensereport/v2.0/report/158CDE55632F47FC9B3E' #JP EXPENSE TEST
    # url = 'expense/expensereport/v2.0/report/08C34E0FBF7A475E8ACC'
    # url = 'expense/expensereport/v2.0/report/'
    # url = 'travel/trip/v1.1/gWupfRy3KgBloZVefUTW4S2L5VczzUK9R058'
    # url = 'travel/trip/v1.1/'
    # url = 'travelprofile/v2.0/profile'
    url = 'v3.0/common/lists'
    # url = 'v3.0/common/lists/gWnlUZfLdIepKxhEcbz2bY8DfpWS1al1GJA'
    # url = 'v3.0/common/listitems'

    ##PARAM EXTERNO##
    url = api_url if api_url is not None else url

    params = {

        # "ListID": 'gWnlUZfLdIepKxhEcbz2bY8DfpWS1al1GJA',

        # 'loginID':'2J3135897@IBM.COM',
        # userid_type = login & user_id = login_ID
        # 'userid_type':'login',
        # 'user_id':'ALL',
        # 'ReportKey':'63',
        # 'user_id':'2J3135897@IBM.COM',

        # 'userid_type': 'login',
        # 'userid_value': '2J3135897@IBM.COM',
        # 'userid_value': 'BB0TGS760@IBM.COM',
        # 'userid_value': '106471631@IBM.COM',

        'user': 'ALL',
        # 'user': 'pltr@ibmdemo.com',
        # 'user': '001247781@IBM.COM',
        # 'user': '-0500W631@IBM.COM',
        # 'reportID':  '6B56DE60BFC64043BA51',

        # 'id':'gWnlUZfLdIepKxhEcbz2bY8DfpWS1al1GJA',
        # 'approvalStatusCode': 'A_NOTF', #DRAFTS
        # 'paymentStatusCode': 'P_PAYC',
        # 'countryCode': 'JP',
        # 'isTestUser': 'false',
        # 'limit': limit,

        # 'userid_type': 'login',
        # 'userid_value': 'ALL',

        # 'includeCanceledTrips': 'false',
        # 'includeMetadata': 'true',
        # 'ItemsPerPage': '100',
        # 'Page': '1',
        # 'bookingType': 'Air',
        # 'createdAfterDate': '2018-08-25',
        # 'createdBeforeDate': '2018-03-15',
        # 'lastModifiedDate': '2018-08-15',
        # 'submitDateBefore': '2018-08-15',

        # 'paidDateAfter': '2018-12-17T20:59:59',
        # 'paidDateBefore': '2018-08-02T23:59:59',
        # 'isTestUser': 'false',
        # 'hasImages': 'true',
        # 'countryCode': 'IT',
        # 'paymentStatusCode': 'P_PAID,P_PAYC,P_PROC',
        # 'paymentStatusCode': 'P_HOLD',
        # 'paymentStatusCode': 'P_NOTP',

        # 'loginID':'000320JPM@IBM.COM',

        # 'reportID': '5B38C4A2F6EB4C8AB561',
        # 'ID': '5083E452AE314B36B545',
    }

    ##PARAM EXTERNO##
    params = params_ext if params_ext is not None else params

    headers = {
        'Accept': 'application/json',
        # 'Accept': 'application/xml',
    }

    ##PARAM EXTERNO##
    headers = headers_ext if headers_ext is not None else headers

    if nextPage is not None:
        params['offset'] = nextPage

    resp = concur.validate_response(concur.api(url, method='GET', headers=headers, params=params))


    expense_data_nextpage = list(gen_dict_extract('NextPage',resp[1]))
    print 'expense_data_nextpage:', expense_data_nextpage

    # print json.dumps(resp, indent=4)

    if expense_data_nextpage[0] is None:
        expense_data_nextpage = None
    else:
        expense_data_nextpage = expense_data_nextpage[0]
        expense_data_nextpage = parse_qs(urlparse(expense_data_nextpage).query)['offset'][0]


    if resp_key:
        expense_data = list(gen_dict_extract(resp_key,resp[1]))[0]
    else:
        expense_data = list(gen_dict_extract('Items',resp[1]))[0] #Items is most common

    expense_data = [expense_data] if isinstance(expense_data, dict) == 1 else expense_data

    # print json.dumps(expense_data, indent=4)

    ##LISTS VALUES##
    # for r in expense_data:
    #     for k, v in r.iteritems():
    #         if (k.startswith('OrgUnit') and v) or (k.startswith('Custom') and v):
    #             r.update({k: v['Value']})

    ##SORTING##
    # from operator import itemgetter
    # newlist = sorted(expense_data, key=itemgetter('CreateDate'), reverse=True) #order the list by CreateDate (sanity check)
    # print json.dumps(newlist, indent=4)

    return expense_data_nextpage, expense_data

def genericNextPageControl(limit=100, api_url='v3.0/common/lists', resp_key='List', params_ext={'user': 'ALL',},headers_ext={'Accept': 'application/json',}):

    result_arr = []

    nextPage, expense_data = genericSearchResults(limit=limit,nextPage=None,api_url=api_url,resp_key=resp_key,params_ext=params_ext,headers_ext=headers_ext)
    result_arr.extend(expense_data)

    while nextPage is not None:
        try:
            print 'trying to get '+nextPage
            print 'trying to get ' + api_url
            print 'trying to get ' + resp_key
            nextPage, expense_data = genericSearchResults(limit=limit,nextPage=nextPage,api_url=api_url,resp_key=resp_key,params_ext=params_ext,headers_ext=headers_ext)
            result_arr.extend(expense_data)
        except ValueError:
            print ValueError

    return result_arr

def getUserDetails(loginID=None):

    try:
        url = 'user/v1.0/user'
        params = {
            'loginID': loginID,
        }
        headers = {
            'Accept': 'application/json',
        }

        resp = concur.validate_response(concur.api(url, method='GET', headers=headers, params=params, verify=False))

        # print json.dumps(resp,indent=4)

        expense_data = resp[1]

        expense_data['_id'] = expense_data['EmpId']

        expense_data = [expense_data] if isinstance(expense_data, dict) == 1 else expense_data

        return expense_data
    except Exception as e:
        print "Erro message:", e.message
        expense_data = {}
        expense_data['_id'] = loginID.split('@')[0]
        expense_data['EmpId'] = loginID.split('@')[0]
        expense_data['Error'] = e.message
        expense_data['LoginId'] = loginID
        return [expense_data]



if __name__ == "__main__":

    # print 'local_path:',local_path
    # worker = cfworker.cfworker(int(os.getenv('PORT', 8080)))
    # worker.start()
    # while True:
    #     try:
    #         # sleep due concur winny! sleepy before exception, so if raise keep giving 1 minute time
    #         print 'Sleeping 60 seconds....'
    #         time.sleep(60)
    #
    #         # ip = urllib.urlopen('http://ip.jsontest.com').read()
    #         # print 'External IP:',ip
    #
    #         #flush to show ip
    #         sys.stdout.flush()
    #
    #
    #         ###CODE###
    #
    #         #flush
    #         sys.stdout.flush()
    #
    #     except KeyboardInterrupt:
    #         print('Interrompendo!!')
    #         sys.exit(0)
    #
    #     except Exception as e:
    #         print 'Got into Generic Exception'
    #         exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    #         traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback, limit=2, file=sys.stdout)
    #
    # worker.stop()

    loginID = '106471631@IBM.COM'
    # loginID = '054195631@IBM.COM' #OVP BR PROD USER
    # loginID = '158856724@IBM.COM'
    # loginID = '-0500W631@IBM.COM'
    # loginID = '-0500Y631@IBM.COM' #emp4

    user_details = getUserDetails(loginID=loginID)
    user_details = {k:(v.split(')')[0][1:] if v.startswith('(') else v) for k,v in user_details[0].iteritems()}
    # print 'user_details:', user_details
    print 'user_details:', json.dumps(user_details, indent=4)

    # url_policy = 'v3.0/expense/expensegroupconfigurations/{PolicyID}'.format(PolicyID=report_header['PolicyID'])
    url_policy = 'v3.0/expense/expensegroupconfigurations'
    params = {
        # 'user': 'ALL',
        'user': loginID,
        # 'user': 'pltr@ibmdemo.com',
        # 'limit': 10,
    }
    content_type, policy_details = concur.validate_response(concur.api(url_policy, method='GET', headers={'Accept': 'application/json'}, params=params))

    policy_details = {p['Name']:p['ID'] for p in policy_details['Items'][0]['Policies'] if p['Name'].find('Travel and Expense') > -1}
    # policy_details = policy_details['Items']
    print json.dumps(policy_details, indent=4)

    # sys.exit(0)

    url = 'v3.0/common/lists'
    headers = {'Accept': 'application/json',}
    params = {'user': 'ALL',}
    resp_key = 'Items'
    list_accounting = genericNextPageControl(limit=100, api_url=url, resp_key=resp_key, params_ext=params, headers_ext=headers)

    # print 'list_accounting:', json.dumps(list_accounting, indent=4)

    # print 'List Name:',[t['Name'] for t in list_accounting if t['ID'] == "gWnlUZfLdIeo4iAqBzImDn5XYK$ssbIuy83g"]

    # list_accounting = [t['ID'] for t in list_accounting if t['Name'] == "Accounting - ODMLE-Dept/CC/Int Ord-Div"]
    list_accounting = [t['ID'] for t in list_accounting if t['Name'] == "US TET Header"] #gWnlUZfLdIeo4iAqBzImDn5XYK$ssbIuy83g


    print 'list_accounting filtered:',list_accounting


    # list_accounting = ['gWnlUZfLdIeo4iAqBzImDn5XYK$ssbIuy83g']
    url = 'v3.0/common/listitems'
    headers = {'Accept': 'application/json',}
    params = {'user': 'ALL', "ListID": list_accounting[0],}
    resp_key = 'Items'
    list_accounting_item = genericNextPageControl(limit=100, api_url=url, resp_key=resp_key, params_ext=params, headers_ext=headers)

    print 'list_accounting_item:', json.dumps(list_accounting_item, indent=4)

    # ## "Other Travel"  --  gWjIbp$p$sN9EVlE8IBqnz$pli1fhMOMX0LOdw

    list_accounting_item = [t['ID'] for t in list_accounting_item if t['Level1Code'].find('Non-Travel Expenses') > -1]
    print 'list_accounting_item filtered:', list_accounting_item

    # # list_accounting_item = [t['ID'] for t in list_accounting_item if t['Level1Code'] == user_details['OrgUnit1'] and t['Level2Code'] == user_details['OrgUnit2'] and t['Level3Code'] == user_details['OrgUnit3']]
    # # print 'list_accounting_item filtered:', list_accounting_item
    # # sys.exit(0)

    url = 'v3.0/common/listitems/' + list_accounting_item[0]
    headers = {'Accept': 'application/json',}
    params = {'user': 'ALL',}
    resp = concur.validate_response(concur.api(url, method='GET', headers=headers, params=params))

    print 'listitem:',json.dumps(resp,indent=4)


    # # url = 'expense/expensereport/v2.0/report/158CDE55632F47FC9B3E' #JP EXPENSE TEST
    # # url = 'expense/expensereport/v2.0/report/A0ABA47245074CEE92E0' #BR EXPENSE PROD OVP
    # # url = 'expense/expensereport/v2.0/report/D202391C0AC649E9AE34' #BR EXPENSE TEST OVP
    # url = 'v3.0/expense/reports/FC067AFEE36E48F498A4'
    # # url = 'v3.0/expense/entries/'
    # # url = 'v3.0/common/lists'
    #
    # params = {
    #     # 'user': 'ALL',
    #     # 'user': 'pltr@ibmdemo.com',
    #     # 'user': '-0500W631@IBM.COM',
    #     'user': loginID, #FOR API V3
    #
    #     # 'reportID': 'A0ABA47245074CEE92E0',
    #     # 'ID': 'A0ABA47245074CEE92E0',
    # }
    # headers = {
    #     'Accept': 'application/json',
    #     # 'Accept': 'application/xml',
    # }
    #
    # resp = concur.validate_response(concur.api(url, method='GET', headers=headers, params=params))
    #
    # resp = resp[1]
    # # resp = resp[1]['Items'][0]
    #
    # # resp = {k:(v['Value'] if isinstance(v, dict) and 'Value' in v else v) for k,v in resp.iteritems() if v != None}
    #
    # # print json.dumps(OrderedDict(sorted(resp.items(), key=lambda t: t[0])),indent=4)
    # print 'Wade Report Checking:',json.dumps(resp,indent=4)

    ##XML##
    # dom = xml.dom.minidom.parseString(resp)
    # pretty_xml_as_string = dom.toprettyxml()
    # print dom.toprettyxml()

    # sys.exit(0)

    '''
##REPORT####    
{
  "Comment": "string",
  "Custom1": "string",
  "Custom10": "string",
  "Custom11": "string",
  "Custom12": "string",
  "Custom13": "string",
  "Custom14": "string",
  "Custom15": "string",
  "Custom16": "string",
  "Custom17": "string",
  "Custom18": "string",
  "Custom19": "string",
  "Custom2": "string",
  "Custom20": "string",
  "Custom3": "string",
  "Custom4": "string",
  "Custom5": "string",
  "Custom6": "string",
  "Custom7": "string",
  "Custom8": "string",
  "Custom9": "string",
  "Name": "string",
  "OrgUnit1": "string",
  "OrgUnit2": "string",
  "OrgUnit3": "string",
  "OrgUnit4": "string",
  "OrgUnit5": "string",
  "OrgUnit6": "string",
  "PolicyID": "string",
  "Purpose": "string",
  "UserDefinedDate": "2019-08-22T20:43:09.078Z"
}    

{
    "Comment": "string", 
    "Country": "BR", 
    "Custom1": "3", 
    "Custom13": "Non-Travel Expenses", 
    "Custom14": "Other - No Allowances", 
    "Custom2": "LA", 
    "Custom4": "GF", 
    "Custom5": "BusSuppOps", 
    "Custom6": "BusSuppOps", 
    "Custom7": "TR", 
    "Custom8": "Y", 
    "Custom9": "N", 
    "Name": "OVPFORM Setup Employee", 
    "OrgUnit1": "BR 1442", 
    "OrgUnit2": "RWTB11", 
    "OrgUnit3": "07-620", 
    "OrgUnit4": "Department/Cost Center/Int Order", 
    "PolicyID": "gWsIadVLnyvXwm0TYnUgarz2nvsCWsdv1YA",
    "Purpose": "string", 
    "UserDefinedDate": "2019-06-05T00:00:00", 
}    
    
    
##ENTRIE##
{
  "Comment": "string",
  "Custom1": "string",
  "Custom10": "string",
  "Custom11": "string",
  "Custom12": "string",
  "Custom13": "string",
  "Custom14": "string",
  "Custom15": "string",
  "Custom16": "string",
  "Custom17": "string",
  "Custom18": "string",
  "Custom19": "string",
  "Custom2": "string",
  "Custom20": "string",
  "Custom21": "string",
  "Custom22": "string",
  "Custom23": "string",
  "Custom24": "string",
  "Custom25": "string",
  "Custom26": "string",
  "Custom27": "string",
  "Custom28": "string",
  "Custom29": "string",
  "Custom3": "string",
  "Custom30": "string",
  "Custom31": "string",
  "Custom32": "string",
  "Custom33": "string",
  "Custom34": "string",
  "Custom35": "string",
  "Custom36": "string",
  "Custom37": "string",
  "Custom38": "string",
  "Custom39": "string",
  "Custom4": "string",
  "Custom40": "string",
  "Custom5": "string",
  "Custom6": "string",
  "Custom7": "string",
  "Custom8": "string",
  "Custom9": "string",
  "Description": "string",
  "ExchangeRate": 0,
  "ExpenseTypeCode": "string",
  "IsBillable": true,
  "IsPersonal": true,
  "LocationID": "string",
  "OrgUnit1": "string",
  "OrgUnit2": "string",
  "OrgUnit3": "string",
  "OrgUnit4": "string",
  "OrgUnit5": "string",
  "OrgUnit6": "string",
  "PaymentTypeID": "string",
  "ReportID": "string",
  "TaxReceiptType": "string",
  "TransactionAmount": 0,
  "TransactionCurrencyCode": "string",
  "TransactionDate": "2019-08-22T20:36:07.015Z",
  "VendorDescription": "string",
  "VendorListItemID": "string"
}



{
    "Comment": "string",
    "Custom1": "GR2", 
    "Custom18": "N", 
    "Custom20": "Brazil", 
    "Custom21": "Taxicab", 
    "Custom22": "Y", 
    "Custom26": "0", 
    "Custom29": "Brazil", 
    "Description": "Employee reimbursed expenses to which she was not eligible to an", 
    "ExchangeRate": 1.0, 
    "ExpenseTypeCode": "TAXIX", 
    "IsBillable": false, 
    "IsPersonal": false, 
    "LocationID": "gWufDYYdMgGDmBz7qwIc$sl1A0o5pv5JxdTw", 
    "PaymentTypeID": "gWkdvE4L2YnFDV9XTk3dhWIRTkzaX", 
    "PaymentTypeName": "Cash", 
    "ReportID": "A0ABA47245074CEE92E0", 
    "TaxReceiptType": "N", 
    "TransactionAmount": -1159.64, 
    "TransactionCurrencyCode": "BRL", 
    "TransactionDate": "2019-06-05T00:00:00", 
    "VendorDescription": "n/a"
    "VendorListItemID": "string"
}

    '''


    # dict_report = {}
    # dict_report['Report'] = {}
    # dict_report['Report'] = {
    # "Name": "TEST OVPFORM Setup Employee",
    # "Purpose": "Purpose of this one is to test custom13 that was a big problem",
    # "Policy": policy_details.keys()[0],
    # # "Country": "BR",
    # # "Custom1": "3",
    # "Custom13": {
    #     "ListItemID": list_accounting_item[0],
    #     # "ListItemID": "gWjIbpoqL$pDAbnOFNouUcQWXrPejv6p$polA",
    #     # "Code": "(BR)Non-Travel Expenses",
    # #     # "Type": "List",
    # #     # "Value": "Other Travel",
    # #     "Name": "Non-Travel Expenses",
    # },
    # "Comment": "this is just a comment after figuring custom13",
    # # "Custom13": "(BR)Non-Travel Expenses",
    # # "Custom14": "Other - No Allowances",
    # # "Custom2": "LA",
    # # "Custom4": "GF",
    # # "Custom5": "BusSuppOps",
    # # "Custom6": "BusSuppOps",
    # # "Custom7": "TR",
    # # "Custom8": "Y",
    # # "Custom9": "N",
    #
    # # "OrgUnit1": user_details['OrgUnit1'],
    # # "OrgUnit2": user_details['OrgUnit2'],
    # # "OrgUnit3": user_details['OrgUnit3'],
    #
    # # "OrgUnit4": None,
    # # "OrgUnit5": None,
    # # "OrgUnit6": None,
    # # "OrgUnit7": None,
    # # "OrgUnit8": None,
    # # "OrgUnit9": None,
    #
    # # "OrgUnit1": {
    # #     "ListItemID": "gWjIbpo6O$pEQUqYGhpJ07E$pn4Dxaa3qvJlA",
    # #     "Code": user_details['OrgUnit1'],
    # #     "Type": "ConnectedList",
    # #     "Value": user_details['OrgUnit1'],
    # # },
    # # "OrgUnit2": {
    # #     "ListItemID": "gWjIbpo6O$pEQUqYGhpJ07E$pn4Dxaa3qvJlA",
    # #     "Code": user_details['OrgUnit2'],
    # #     "Type": "ConnectedList",
    # #     "Value": user_details['OrgUnit2'],
    # # },
    # # "OrgUnit3": {
    # #     "ListItemID": "gWjIbpo6O$pEQUqYGhpJ07E$pn4Dxaa3qvJlA",
    # #     "Code": user_details['OrgUnit3'],
    # #     "Type": "ConnectedList",
    # #     "Value": user_details['OrgUnit3'],
    # # },
    # # "OrgUnit4": "Department/Cost Center/Int Order",
    # # "PolicyID": "gWsIadVLnyvXwm0TYnUgarz2nvsCWsdv1YA",
    # # "UserDefinedDate": "2019-06-05T00:00:00",
    # }
    # # dict_report['Report']['@xmlns'] = 'http://www.concursolutions.com/api/expense/expensereport/2011/03'
    #
    # # xml_post = xmltodict.unparse(dict_report)
    # xml_post = xmltodict.unparse(dict_report, pretty=True)
    # xml_post = xml_post.split("\n",1)[1];


    params = {
        # 'user': 'ALL',
        # 'user': 'pltr@ibmdemo.com',
        'user': loginID,

        # 'loginID': loginID,

        # 'reportID': 'A0ABA47245074CEE92E0',
        # 'ID': 'A0ABA47245074CEE92E0',
    }

    # ##XML##
    # dom = xml.dom.minidom.parseString(xml_post)
    # pretty_xml_as_string = dom.toprettyxml()
    # print dom.toprettyxml()

    # print 'xml_post:', xml_post

    # print 'json:',json.dumps(dict_report, indent=4)

    json_data = {
        "Name": "TEST #2 OVPFORM Setup Employee",
        "Purpose": "Purpose of this one is to test custom13 that was a big problem",
        "PolicyID": 'gWsIadVLnyvXwm0TYnUgarz2nvsCWsdv1YA',
        # "PolicyID": policy_details.values()[0],
        # "Country": "BR",
        # "Custom1": "3",
        # "Custom13": {
        #     "ListItemID": list_accounting_item[0],
        #     # "ListItemID": "gWjIbpoqL$pDAbnOFNouUcQWXrPejv6p$polA",
        # },
        "Comment": "this is just a comment after figuring custom13"
    }

    content_type, resp_post = concur.validate_response(concur.api('v3.0/expense/reports', method='POST', params=params,
                                                                  headers={'Content-type': 'application/json', 'accept': '*'}, data=json.dumps(json_data)))

    ##GET LATEST REPORT FOR A PERSON##
    # url = 'v3.0/expense/reports/'
    # params = {
    #     # 'user': '-0500W631@IBM.COM',
    #     'user': loginID, #FOR API V3
    #     'paymentStatusCode': 'P_NOTP',  ##TEST##
    #     'limit': 100,
    # }
    # headers = {
    #     'Accept': 'application/json',
    # }
    # resp = concur.validate_response(concur.api(url, method='GET', headers=headers, params=params))
    # expense_data = resp[1]['Items']
    # newlist = sorted(expense_data, key=itemgetter('CreateDate'), reverse=True)  # order the list by CreateDate (sanity check)
    # print json.dumps(newlist[0],indent=4)
    #
    # xml_post = '''<Report><PolicyID>''' + policy_details.values()[0] + '''</PolicyID></Report>'''
    # print 'xml_post (PolicyID):',xml_post
    # content_type, resp_post = concur.validate_response(concur.api('v3.0/expense/reports/'+newlist[0]['ID'], method='PUT', params=params,
    #                                                               headers={'content-type': 'application/xml', 'accept': '*'}, data=xml_post))

    # xml_post = '''<Report><Custom13><ListItemID>gWp$pCxj1LTXkAAwXYWR6DAFpZ7zogOKe86w</ListItemID></Custom13></Report>'''
    # content_type, resp_post = concur.validate_response(concur.api('v3.0/expense/reports/8CC8D782D620479084A3', method='PUT', params=params,
    #                                                               headers={'content-type': 'application/xml', 'accept': '*'}, data=xml_post))



#===========================================================
#===============SUBMIT THE REPORT AGAIN=====================
#===========================================================



# print 'xml_post:',xml_post
# url = 'expense/expensereport/v1.1/report/9DA11BA5482848848201'
# params = {
#             # 'user': 'ALL',
#             'user': loginID,
#         }
# headers = {
#             # 'Accept': 'application/json',
#             # 'Accept': 'application/xml',
#             'Accept': '*',
#             'Content-type': 'application/xml',
#             'X_UserID': loginID,
#             }
# resp = concur.validate_response(concur.api(url, method='POST', headers=headers, params=params, data=xml_post))
# print json.dumps(resp,indent=4)