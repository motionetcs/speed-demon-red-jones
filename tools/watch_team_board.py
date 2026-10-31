#!/usr/bin/env python3
"""Read complete public team objects using ordinary current-object HTTP ranges."""
import argparse,datetime,hashlib,json,re,subprocess,time,urllib.error,urllib.request
from pathlib import Path
URL='https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json'
def main():
 p=argparse.ArgumentParser();p.add_argument('--commit',default='HEAD');p.add_argument('--baseline',type=Path,default=Path('docs/round73-start-board.json'));p.add_argument('--report',type=Path,required=True);p.add_argument('--timeout',type=int,default=900);a=p.parse_args();sha=subprocess.check_output(['git','rev-parse',a.commit],text=True).strip();old=json.loads(a.baseline.read_text());encoded=json.dumps(old,indent=1);key=encoded.index('"team": "Red Jones"');position=len(encoded[:key].encode());deadline=time.monotonic()+a.timeout;previous=None
 while time.monotonic()<deadline:
  try:
   start=max(0,position-24576);end=position+49151
   request=urllib.request.Request(URL,headers={'User-Agent':'speed-demon-team-watch/1.0','Cache-Control':'no-cache','Range':f'bytes={start}-{end}'})
   with urllib.request.urlopen(request,timeout=25) as response:
    assert response.status==206;headers=dict(response.headers);data=response.read()
   content_range=headers.get('Content-Range','');m=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',content_range);assert m and int(m[1])==start and len(data)==int(m[2])-start+1
   s=data.decode('utf-8',errors='replace');at=s.index('"team": "Red Jones"');begin=s.rfind('{',0,at);team,used=json.JSONDecoder().raw_decode(s[begin:]);assert team['slug']=='red-jones-00c4a7'
   records={t:team['tracks'][t].get('latest',{}) for t in 'acd' if team['tracks'][t].get('latest',{}).get('commit')==sha};state=json.dumps({'head':team.get('watch',{}).get('head'),'queue':team.get('queue'),'results':{t:(x.get('stage'),x.get('points')) for t,x in records.items()}},sort_keys=True)
   if state!=previous:print(headers.get('Last-Modified'),state,flush=True);previous=state
   terminal=len(records)==3 and all(x.get('stage')=='scored' or x.get('ok') is False for x in records.values())
   if terminal:
    passed=all(x.get('ok') and x.get('stage')=='scored' and all(x['gates'].values()) for x in records.values());report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'feed_generated_at':None,'source':URL,'commit':sha,'team':team['team'],'slug':team['slug'],'tracks':records,'passed':passed,'scope':'Official public-seed board; complete exact team object from one normal public current-object byte-range response. Final holdout/judging separate. Rankings use a separately complete feed.','download':{'etag':headers.get('ETag'),'last_modified':headers.get('Last-Modified'),'content_range':content_range,'sha256':hashlib.sha256(data).hexdigest()}}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print('SCORED' if passed else 'FAILED',json.dumps({t:{k:x.get(k) for k in ['run_id','T_s','M_bytes','S','K','points','failure']} for t,x in records.items()}),flush=True);return 0 if passed else 2
  except urllib.error.HTTPError as error:
   if error.code in (403,429):
    print('Public feed denied or rate-limited; stopping:',error.code,flush=True);return 4
   print('Public feed HTTP error:',error.code,flush=True)
  except (OSError,ValueError,AssertionError,KeyError) as error:
   # No historical-version access, alternate identity or response reconstruction.
   print('Public feed read unavailable:',str(error)[:160],flush=True)
  time.sleep(15)
 print('Timeout waiting for exact all-track result',sha,flush=True);return 3
if __name__=='__main__':raise SystemExit(main())
