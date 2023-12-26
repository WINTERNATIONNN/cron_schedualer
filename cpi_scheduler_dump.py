
from ensurepip import version
import uuid,re,time,pprint
from requests import head # type: ignore
from webservice import WebService
import json,os,sys,zipfile,xmltodict # type: ignore
from requests.auth import HTTPBasicAuth  # type: ignore
from base64 import b64encode, b64decode # type: ignore
import yaml # type: ignore
import difflib # type: ignore
from lxml import etree # type: ignore
from cron_descriptor import get_description, ExpressionDescriptor # type: ignore

def handleAuth(config, preToken=None, expectedTimeInSecondsToProcess=600):
    obj = config
    if obj["auth_type"] == 'Basic':
        return {"Authorization": "Basic %s" % (str(b64encode(bytes("%s:%s" % (obj["basic_username"], obj["basic_password"]), "UTF-8" ) ),'UTF-8'))}
    if obj["auth_type"] == 'oAuth2.0':
        
        if preToken != None:
            issue_time = preToken["issue_time"]
            life_time_in_sec = preToken["life_time_in_sec"]
            now = time.time()
            if (life_time_in_sec - (now-issue_time) ) > expectedTimeInSecondsToProcess:
                return preToken

        oAuthTokenUrl = "%s?grant_type=%s" % (obj["oauth_token_url"], obj["oauth_grant_type"])
        client_id = obj["oauth_client_id"]
        client_secret = obj["oauth_client_secret"]
        basicAuth = HTTPBasicAuth(username=client_id, password=client_secret)
        ws = WebService(oAuthTokenUrl, None, auth1=basicAuth)
        oresp = ws.post(headers=None, payload=None)
        resp = json.loads(str(oresp.content, 'utf-8'))
        atoken = resp['access_token']

        return {"Authorization":'%s %s' % (obj["oauth_header_prefix"], atoken),
                "life_time_in_sec": resp["expires_in"], "issue_time": time.time()}


def listRuntimeArtifacts(base_url, configurations, token):
    url = "%s/api/v1/IntegrationRuntimeArtifacts?$format=json" % (base_url)

    ws = WebService(url, None, auth1=None)
    token = handleAuth(configurations, preToken=token)
    resp = ws.get(token)
    if resp.status_code != 200:
        return {"status_code":resp.status_code}
    else:
        return {"status_code":resp.status_code, "content": str(resp.content,'utf-8')}

def readContent(contents, workfolder):
    randomCode = str.upper(uuid.uuid4().hex)
    srcPath = os.path.join(workfolder, 'S1O2U3R4C5E6____%s.zip' % (randomCode))
    targetPath = os.path.join(workfolder, 'T1A2R3G4E5T6____%s.zip' % (randomCode))
    result = None
    with open( srcPath, 'w+b') as f:
        f.write(contents['content'])
        f.close()
    with zipfile.ZipFile(srcPath, 'r') as inzip, zipfile.ZipFile(targetPath, 'w') as outzip:
        for inzipinfo in inzip.infolist():
        # Read input file
            with inzip.open(inzipinfo) as infile:
                content = infile.read()
                if inzipinfo.filename.endswith(".iflw"):                   
                    result =  content
                    break
                else: # Other file, dont want to modify => just copy it
                    pass
                outzip.writestr(inzipinfo.filename, content)

    
    
    ###clean temp file####
    os.system('rm %s' % (srcPath))
    os.system('rm %s' % (targetPath))

    return result

def dumpPkgContent(contents, workfolder, ids):
    randomCode = str.upper(uuid.uuid4().hex)
    srcPath = os.path.join(workfolder, 'S1O2U3R4C5E6____%s.zip' % (randomCode))
    targetPath = os.path.join(workfolder, 'T1A2R3G4E5T6____%s.zip' % (randomCode))
    result = {}
    resources = None
    with open( srcPath, 'w+b') as f:
        f.write(contents['content'])
        f.close()
    with zipfile.ZipFile(srcPath, 'r') as inzip, zipfile.ZipFile(targetPath, 'w') as outzip:
        for inzipinfo in inzip.infolist():
        # Read input file
            with inzip.open(inzipinfo) as infile:
                content = infile.read()
                if inzipinfo.filename.endswith("resources.cnt"): 
                    cont = b64decode(content)                
                    #result =  content
                    resources = json.loads(str(cont, "UTF-8"))
                    break
                else: # Other file, dont want to modify => just copy it
                    pass
                outzip.writestr(inzipinfo.filename, content)

                

        for id in ids:
            iflw_id = { id: x["id"]  for x in resources["resources"] if x["uniqueId"] == id }
            with inzip.open("%s_content" % (iflw_id[id])) as inf:
                c = inf.read()
                result[id] = {'status_code':200, 'content':c}
    
    
    ###clean temp file####
    os.system('rm %s' % (srcPath))
    os.system('rm %s' % (targetPath))

    return result

def downloadDesigntimeArtifact(base_url, id, configurations, token):
    url = "%s/api/v1/IntegrationDesigntimeArtifacts(Id='%s',Version='Active')/$value" % (base_url, id)

    ws = WebService(url, None, auth1=None)
    token = handleAuth(configurations, preToken=token)
    resp = ws.get(token)
    if resp.status_code != 200:
        return {"status_code":resp.status_code, "content": str(resp.content, 'utf-8')}
    else:
        return {"status_code":resp.status_code, "content": resp.content}
    

def getConfig(base_url, id, key,configurations, token=None):
    url = "%s/api/v1/IntegrationDesigntimeArtifacts(Id='%s',Version='active')/Configurations?$filter=ParameterKey eq '%s'&$format=json" % (base_url, id, key )
    ws = WebService(url, None, None)
    token = handleAuth(config=configurations, preToken=token)
    resp = ws.get(token, None)

    return str(resp.content, 'utf-8')

def dumpTimer(base_url, workfolder, configurations,read_only_artifacts_ids,id, content,token):
    read_only_keys = read_only_artifacts_ids.keys()
    
    results = {}
    
    iflw = readContent(content,workfolder)
    html = etree.HTML(iflw)
    values = html.xpath('//*[local-name()=("property")]/key[text()="scheduleKey"]/following-sibling::value/text()')
    if len(values) > 0 and id not in results.keys():
        results[id]=[]
    for value in values:
        cfg = re.match('{{.*}}', value)
        if cfg != None:
            cfg_v = getConfig(base_url, id, cfg.string[2:-2],configurations=configurations, token=token)
            cfg_v_json = json.loads(cfg_v)
            value = cfg_v_json["d"]["results"][0]["ParameterValue"]
            if value == 'fireNow=true':
                results[id].append({"value":"fireNow=true", "description":"one time execution during deployment"})
            else:
                vs = value.split(' --tz=')
                results[id].append({"value":vs[0], "description":get_description(vs[0]), "timezone": vs[1]})
            pass
        else:
            if value == 'fireNow=true':
                #print('one time execution during deployment')
                results[id].append({"value":"fireNow=true", "description":"one time execution during deployment"})
            else:
                ht = etree.HTML(value)
                v = ht.xpath('//cell[text()="schedule1"]/following-sibling::cell/text()')
                if len(v) > 0:
                    for i in v:
                        if i == 'fireNow=true':
                            results[id].append({"value":"fireNow=true", "description":"one time execution during deployment"})
                        else:
                            ii = i.split('&trigger.timeZone=');
                            results[id].append({"value":ii[0].replace('+',' '), "description":get_description(ii[0].replace('+',' ')), "timezone": ii[1]})
                else:
                    results[id].append({"value": value, "description": "unknown for now."})
    
    return results

def dumpTimers(base_url,workfolder,configurations,read_only_artifacts_ids):
    token = None
    token = handleAuth(configurations, preToken=token)

    read_only_keys = read_only_artifacts_ids.keys()

    artifacts = listRuntimeArtifacts(base_url, configurations, token)
    jbody = json.loads(artifacts["content"]);
    results = {}
    for result in jbody["d"]['results']:
        if result["Id"] in read_only_keys:
            read_only_artifacts_ids[result["Id"]]["required"] = True
            continue
        content = downloadDesigntimeArtifact(base_url, result["Id"], configurations=configurations, token=token)
        if content['status_code'] == 200:
            iflw = readContent(content,workfolder)
            html = etree.HTML(iflw)
            values = html.xpath('//*[local-name()=("property")]/key[text()="scheduleKey"]/following-sibling::value/text()')
            if len(values) > 0 and result["Id"] not in results.keys():
                results[result["Id"]]=[]
            for value in values:
                cfg = re.match('{{.*}}', value)
                if cfg != None:
                    cfg_v = getConfig(base_url, result["Id"], cfg.string[2:-2],configurations=configurations, token=token)
                    cfg_v_json = json.loads(cfg_v)
                    value = cfg_v_json["d"]["results"][0]["ParameterValue"]
                    if value == 'fireNow=true':
                        results[result["Id"]].append({"value":"fireNow=true", "description":"one time execution during deployment"})
                    else:
                        vs = value.split(' --tz=')
                        results[result["Id"]].append({"value":vs[0], "description":get_description(vs[0]), "timezone": vs[1]})
                    pass
                else:
                    if value == 'fireNow=true':
                        #print('one time execution during deployment')
                        results[result["Id"]].append({"value":"fireNow=true", "description":"one time execution during deployment"})
                    else:
                        ht = etree.HTML(value)
                        v = ht.xpath('//cell[text()="schedule1"]/following-sibling::cell/text()')
                        if len(v) > 0:
                            for i in v:
                                if i == 'fireNow=true':
                                    results[result["Id"]].append({"value":"fireNow=true", "description":"one time execution during deployment"})
                                else:
                                    ii = i.split('&trigger.timeZone=');
                                    results[result["Id"]].append({"value":ii[0].replace('+',' '), "description":get_description(ii[0].replace('+',' ')), "timezone": ii[1]})
                        else:
                            results[id].append({"value": value, "description": "unknown for now."})

    read_only_packages = { read_only_artifacts_ids[key]["pkg_id"]:[k for k in read_only_artifacts_ids.keys() if read_only_artifacts_ids[key]["pkg_id"] == read_only_artifacts_ids[k]["pkg_id"] and read_only_artifacts_ids[k]["required"]] for key in read_only_artifacts_ids.keys() }

    #print(read_only_packages)
    for key in read_only_packages:
        pkg_content = downloadPkg(base_url,workfolder,configurations,key, token)

        artifacts_contents = dumpPkgContent(pkg_content, workfolder, read_only_packages[key])

        #print(artifacts_contents)
        for id in read_only_packages[key]:
            r = dumpTimer(base_url, workfolder, configurations, read_only_artifacts_ids, id, artifacts_contents[id], token)

            results.update(r)

    return results

def readAritifactsFromDownloadedCopy(pkg_content, ids):
    pass

def downloadPkg(base_url,workfolder,configurations, id, token):
    
    url = "%s/api/v1/IntegrationPackages('%s')/$value" % (base_url, id )
    ws = WebService(url, None, None)
    token = handleAuth(config=configurations, preToken=token)

    resp = ws.get(token, None)

    if resp.status_code == 200:
        return {'status_code': resp.status_code, 'content': resp.content}
    else:
        return {'status_code': resp.status_code}

def getReadonlyPkgs(base_url,workfolder,configurations):
    token = None
    token = handleAuth(config=configurations, preToken=token)
    
    url = "https://integration-suite-x6woleh8.it-cpitrial03.cfapps.ap21.hana.ondemand.com/api/v1/IntegrationPackages?$format=json"
    #IntegrationRuntimeArtifacts
    ws = WebService(url, None, None)
    resp = ws.get(token, None)
    print(resp)
    results = json.loads(resp.content)

    pkgs = {}
    pkgs = {result["Id"]:result["Id"] for result in results["d"]["results"] if result["Mode"] == "READ_ONLY"}

    #pkgs = {result["Id"]:result["Id"] for result in results["d"]["results"] }

    #print(pkgs)
    return pkgs


def getReadonlyArtifacts(base_url, workfolder, configurations, pkgs):
    token = None
    artifacts = {}
    for key in pkgs.keys():
        url = "%s/api/v1/IntegrationPackages('%s')/IntegrationDesigntimeArtifacts?$format=json" % (base_url, key)

        ws = WebService(url, None, None)
        token = handleAuth(config=configurations, preToken=token)
        resp = ws.get(token, None)
        results = json.loads(resp.content)

        artifacts.update({result["Id"]:{ "required": False, "pkg_id": key }for result in results["d"]["results"] })
    
    return artifacts

def main():
    config_path = '/Users/I741185/Documents/scheduler dumps/config.json' #fIXME
    #input('Please specify the configuration file full path: ') 
    #'/Users/i318048/Documents/hierarchy/Projects/BTP/CommonUtils/utils_py/cpi/config.json' 
    configurations = None

    with open(config_path) as f:
        config = f.read()
        configurations = json.loads(config)
    read_only_artifacts_ids = {}

    print("Analyzing in process, please wait...")
    read_only_pkgs = getReadonlyPkgs(configurations["cpi_tenant_url"],configurations["temp_working_folder_with_write_access"], configurations)
    
    read_only_artifacts_ids = getReadonlyArtifacts(configurations["cpi_tenant_url"],configurations["temp_working_folder_with_write_access"], configurations, read_only_pkgs)
    result  = json.dumps(dumpTimers(configurations["cpi_tenant_url"],configurations["temp_working_folder_with_write_access"], configurations, read_only_artifacts_ids))

    if os.path.exists(configurations['result_output_path']):
        os.remove(configurations['result_output_path'])
    with open(configurations['result_output_path'], 'a') as f:
        f.writelines(result)
        #json.dump(result, f)

    print("Analzing done, result canbe found at %s same with below:" % (configurations['result_output_path']))
    print(result)
    
    

    