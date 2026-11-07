"""CineIA API: MVP seguro, sin secretos embebidos."""
from datetime import datetime, timedelta, timezone
from typing import Literal
import json, os, uuid
import httpx
from urllib.parse import quote_plus, quote
from xml.etree import ElementTree
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Header, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL','')
JWT_SECRET=os.getenv('JWT_SECRET_KEY','development-only-change-me')
BI_API_KEY=os.getenv('BI_API_KEY','development-bi-key')
GROQ_API_KEY=os.getenv('GROQ_API_KEY','')
GROQ_MODEL=os.getenv('GROQ_MODEL','openai/gpt-oss-20b')
engine=create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
pwd=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')
app=FastAPI(title='CineIA API', version='1.1.0', description='API autenticada para CineIA')
frontend_origins=sorted({'http://localhost:5173','http://127.0.0.1:5173',*[origin.strip() for origin in os.getenv('FRONTEND_ORIGIN','').split(',') if origin.strip()]})
app.add_middleware(CORSMiddleware, allow_origins=frontend_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

class Login(BaseModel): email:str; password:str
class UserCreate(BaseModel): email:str; full_name:str; password:str=Field(min_length=8); role:Literal['ADMIN','USER']='USER'; token_limit_monthly:int=20000
class UserUpdate(BaseModel):
 full_name:str
 role:Literal['ADMIN','USER']
 is_active:bool
 token_limit_monthly:int=Field(ge=0)
 password:str|None=Field(default=None,min_length=8)
class CatalogIn(BaseModel): title:str; category:Literal['MOVIE','GAME']; synopsis:str; genre:str|None=None; platform:str|None=None; release_year:int|None=None; rating:float|None=None
class CatalogUpdate(CatalogIn): is_active:bool=True
class ServiceUpdate(BaseModel): is_active:bool
class ChatIn(BaseModel): message:str=Field(min_length=2,max_length=2000); conversation_id:str|None=None

def db():
 if not engine: raise HTTPException(503,'DATABASE_URL no está configurada.')
 return engine.connect()
def token_for(user):
 return jwt.encode({'sub':str(user['id']),'role':user['role'],'exp':datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES','60')))},JWT_SECRET,algorithm='HS256')
def current(token:str=Depends(oauth2)):
 try: data=jwt.decode(token,JWT_SECRET,algorithms=['HS256'])
 except JWTError: raise HTTPException(status_code=401,detail='Token inválido o vencido')
 with db() as c: row=c.execute(text('SELECT id,email,full_name,role,is_active FROM app_users WHERE id=:id'),{'id':data['sub']}).mappings().first()
 if not row or not row['is_active']: raise HTTPException(status_code=401,detail='Usuario inexistente o inactivo')
 return {'id':str(row['id']),'email':row['email'],'name':row['full_name'],'role':row['role']}
def admin(user=Depends(current)):
 if user['role']!='ADMIN': raise HTTPException(403,'Se requiere rol Administrador')
 return user
def ensure_quota(user, estimated_tokens=1000):
 with db() as c:
  used=c.execute(text("SELECT coalesce(sum(total_tokens),0) FROM usage_logs WHERE user_id=:u AND date_trunc('month',created_at)=date_trunc('month',now())"),{'u':user['id']}).scalar()
  limit=c.execute(text('SELECT token_limit_monthly FROM app_users WHERE id=:u AND is_active=true'),{'u':user['id']}).scalar()
  if limit is None: raise HTTPException(403,'Usuario inactivo')
  if used+estimated_tokens>limit: raise HTTPException(429,'Cuota mensual de IA insuficiente; no se realizó la consulta.')
 return {'used':used,'limit':limit,'remaining':limit-used}
def record(user, service, incoming, outgoing):
 with db() as c:
  c.execute(text('INSERT INTO usage_logs(user_id,service_code,request_tokens,response_tokens,total_tokens) VALUES(:u,:s,:i,:o,:t)'),{'u':user['id'],'s':service,'i':incoming,'o':outgoing,'t':incoming+outgoing}); c.commit()
def enabled(code):
 with db() as c:
  if not c.execute(text('SELECT 1 FROM ai_services WHERE code=:x AND is_active=true'),{'x':code}).first(): raise HTTPException(503,'Este servicio está desactivado.')
def groq_chat(messages):
 if not GROQ_API_KEY: raise HTTPException(503,'GROQ_API_KEY no está configurada.')
 try:
  response=httpx.post('https://api.groq.com/openai/v1/chat/completions',headers={'Authorization':f'Bearer {GROQ_API_KEY}','Content-Type':'application/json'},json={'model':GROQ_MODEL,'messages':messages,'temperature':0.2,'max_tokens':700},timeout=35)
  response.raise_for_status(); data=response.json(); usage=data.get('usage',{})
  return data['choices'][0]['message']['content'],int(usage.get('prompt_tokens',0)),int(usage.get('completion_tokens',0))
 except httpx.HTTPStatusError as exc:
  detail='Groq rechazó la solicitud.' if exc.response.status_code in (401,403) else 'Groq no pudo procesar la solicitud.'
  raise HTTPException(502,detail)
 except (httpx.HTTPError,KeyError,IndexError,ValueError): raise HTTPException(502,'No fue posible comunicarse con Groq.')
def wikipedia_details(title):
 try:
  response=httpx.get('https://es.wikipedia.org/w/api.php',params={'action':'query','generator':'search','gsrsearch':title+' película videojuego','gsrlimit':1,'prop':'extracts|info','exintro':1,'explaintext':1,'inprop':'url','format':'json'},headers={'User-Agent':'CineIA-academic/1.0 (admin@cineia.local)'},timeout=12)
  if response.status_code!=200:return None
  pages=response.json().get('query',{}).get('pages',{});data=next(iter(pages.values()),None)
  if not data:return None
  return {'title':data.get('title',title),'extract':data.get('extract',''),'url':data.get('fullurl')}
 except httpx.HTTPError:return None
def google_news(query):
 try:
  url='https://news.google.com/rss/search?q='+quote_plus(query)+'&hl=es-419&gl=US&ceid=US:es-419'
  response=httpx.get(url,headers={'User-Agent':'CineIA-academic/1.0'},timeout=15);response.raise_for_status()
  root=ElementTree.fromstring(response.content);items=[]
  for node in root.findall('.//item')[:5]: items.append({'title':node.findtext('title',''),'url':node.findtext('link',''),'date':node.findtext('pubDate','')})
  return items
 except (httpx.HTTPError,ElementTree.ParseError):return []
def save_exchange(user,service,question,answer,sources):
 with db() as c:
  cid=str(c.execute(text('INSERT INTO conversations(user_id,service_code) VALUES(:u,:s) RETURNING id'),{'u':user['id'],'s':service}).scalar())
  c.execute(text("INSERT INTO chat_messages(conversation_id,role,content,sources) VALUES(:c,'user',:q,'[]'),(:c,'assistant',:a,CAST(:sources AS jsonb))"),{'c':cid,'q':question,'a':answer,'sources':json.dumps(sources)});c.commit()
 return cid

@app.get('/health')
def health(): return {'status':'ok','database_configured':bool(engine),'groq_configured':bool(GROQ_API_KEY),'version':app.version}
@app.post('/api/v1/auth/login')
def login(body:Login):
 with db() as c:
  row=c.execute(text('SELECT id,email,full_name,password_hash,role,is_active FROM app_users WHERE email=:e'),{'e':body.email.lower()}).mappings().first()
 if not row or not row['is_active'] or not pwd.verify(body.password,row['password_hash']): raise HTTPException(401,'Credenciales inválidas')
 return {'access_token':token_for(row),'token_type':'bearer','user':{'id':str(row['id']),'email':row['email'],'name':row['full_name'],'role':row['role']}}
@app.post('/api/v1/auth/logout',status_code=204)
def logout(): return None
@app.get('/api/v1/auth/me')
def me(user=Depends(current)): return user
@app.get('/api/v1/services')
def available_services(user=Depends(current)):
 with db() as c:return [dict(x) for x in c.execute(text('SELECT code,name,description,is_active FROM ai_services ORDER BY code')).mappings()]
@app.get('/api/v1/catalog/items')
def catalog(q:str|None=None, user=Depends(current)):
 with db() as c:
  return [dict(x) for x in c.execute(text("SELECT id,title,category,synopsis,genre,platform,release_year,rating FROM catalog_items WHERE is_active AND (CAST(:q AS text) IS NULL OR title ILIKE '%'||CAST(:q AS text)||'%' OR synopsis ILIKE '%'||CAST(:q AS text)||'%') ORDER BY title"),{'q':q}).mappings()]
@app.get('/api/v1/admin/catalog/items')
def admin_catalog(q:str|None=None,user=Depends(admin)):
 with db() as c:
  return [dict(x) for x in c.execute(text("SELECT id,title,category,synopsis,genre,platform,release_year,rating,is_active FROM catalog_items WHERE (CAST(:q AS text) IS NULL OR title ILIKE '%'||CAST(:q AS text)||'%' OR synopsis ILIKE '%'||CAST(:q AS text)||'%') ORDER BY is_active DESC,title"),{'q':q}).mappings()]
@app.post('/api/v1/catalog/items',status_code=201)
def create_catalog(body:CatalogIn, user=Depends(admin)):
 with db() as c:
  row=c.execute(text('INSERT INTO catalog_items(title,category,synopsis,genre,platform,release_year,rating) VALUES(:title,:category,:synopsis,:genre,:platform,:release_year,:rating) RETURNING id'),body.model_dump()).first(); c.commit(); return {'id':str(row[0])}
@app.put('/api/v1/catalog/items/{item_id}')
def update_catalog(item_id:str,body:CatalogUpdate,user=Depends(admin)):
 with db() as c:
  values={**body.model_dump(),'id':item_id}
  changed=c.execute(text('UPDATE catalog_items SET title=:title,category=:category,synopsis=:synopsis,genre=:genre,platform=:platform,release_year=:release_year,rating=:rating,is_active=:is_active,updated_at=now() WHERE id=:id'),values).rowcount
  if not changed: raise HTTPException(404,'Elemento no encontrado')
  c.commit();return {'id':item_id,'updated':True}
@app.delete('/api/v1/catalog/items/{item_id}')
def delete_catalog(item_id:str,user=Depends(admin)):
 with db() as c:
  changed=c.execute(text('UPDATE catalog_items SET is_active=false,updated_at=now() WHERE id=:id'),{'id':item_id}).rowcount
  if not changed: raise HTTPException(404,'Elemento no encontrado')
  c.commit();return {'id':item_id,'is_active':False}
@app.get('/api/v1/admin/users')
def users(user=Depends(admin)):
 with db() as c:return [dict(x) for x in c.execute(text('SELECT id,email,full_name,role,is_active,token_limit_monthly,created_at FROM app_users ORDER BY created_at DESC')).mappings()]
@app.post('/api/v1/admin/users',status_code=201)
def create_user(body:UserCreate,user=Depends(admin)):
 with db() as c:
  try: row=c.execute(text('INSERT INTO app_users(email,full_name,password_hash,role,token_limit_monthly) VALUES(:email,:full_name,:password_hash,:role,:token_limit_monthly) RETURNING id'),{**body.model_dump(exclude={'password'}),'email':body.email.lower(),'password_hash':pwd.hash(body.password)}).first();c.commit();return {'id':str(row[0])}
  except Exception: raise HTTPException(409,'El correo ya existe o los datos son inválidos')
@app.put('/api/v1/admin/users/{user_id}')
def update_user(user_id:str,body:UserUpdate,user=Depends(admin)):
 if user_id==user['id'] and (not body.is_active or body.role!='ADMIN'): raise HTTPException(400,'No puedes desactivar ni quitar tu propio rol de administrador.')
 with db() as c:
  values={**body.model_dump(exclude={'password'}),'password_hash':pwd.hash(body.password) if body.password else None,'id':user_id}
  changed=c.execute(text('UPDATE app_users SET full_name=:full_name,role=:role,is_active=:is_active,token_limit_monthly=:token_limit_monthly,password_hash=coalesce(:password_hash,password_hash) WHERE id=:id'),values).rowcount
  if not changed: raise HTTPException(404,'Usuario no encontrado')
  c.commit();return {'id':user_id,'updated':True}
@app.get('/api/v1/admin/services')
def services(user=Depends(admin)):
 with db() as c:return [dict(x) for x in c.execute(text('SELECT code,name,description,is_active FROM ai_services ORDER BY code')).mappings()]
@app.put('/api/v1/admin/services/{code}')
def update_service(code:str,body:ServiceUpdate,user=Depends(admin)):
 with db() as c:
  if c.execute(text('UPDATE ai_services SET is_active=:a WHERE code=:c'),{'a':body.is_active,'c':code}).rowcount==0: raise HTTPException(404,'Servicio no encontrado')
  c.commit();return {'code':code,'is_active':body.is_active}
def rag_reply(message):
 with db() as c:
  rows=c.execute(text("""SELECT id,title,category,synopsis,genre,platform,release_year,rating,
   greatest(similarity(title,:q),word_similarity(title,:q)) score
   FROM catalog_items WHERE is_active AND (
    to_tsvector('spanish',title||' '||synopsis||' '||coalesce(genre,'')) @@ websearch_to_tsquery('spanish',:q)
    OR word_similarity(title,:q) > 0.35 OR similarity(title,:q) > 0.2)
   ORDER BY score DESC,rating DESC NULLS LAST LIMIT 5"""),{'q':message}).mappings().all()
 sources=[{'id':str(r['id']),'title':r['title'],'type':'catalog'} for r in rows]
 context='\n'.join(f"- {r['title']} ({r['category']}, {r['release_year'] or 'año desconocido'}). Género: {r['genre'] or 'N/D'}. Plataforma: {r['platform'] or 'N/D'}. Calificación: {r['rating'] or 'N/D'}. Sinopsis: {r['synopsis']}" for r in rows)
 return context,sources
def preference_candidates(message):
 stop={'para','como','quiero','buena','buenas','recomienda','recomiendame','recomiéndame','pelicula','película','juego','videojuego','con','que','una','uno','los','las','del','por'}
 words={w.strip('¿?¡!.,:;').lower() for w in message.split() if len(w.strip('¿?¡!.,:;'))>3}-stop
 with db() as c: rows=c.execute(text('SELECT id,title,category,synopsis,genre,platform,release_year,rating FROM catalog_items WHERE is_active ORDER BY rating DESC NULLS LAST')).mappings().all()
 ranked=[]
 for row in rows:
  haystack=' '.join(str(row.get(k) or '') for k in ('title','category','synopsis','genre','platform')).lower();score=sum(1 for w in words if w in haystack)
  if score: ranked.append((score,row))
 selected=[r for _,r in sorted(ranked,key=lambda x:(x[0],float(x[1]['rating'] or 0)),reverse=True)[:5]]
 context='\n'.join(f"- {r['title']} ({r['category']}, {r['release_year'] or 'año desconocido'}). Género: {r['genre'] or 'N/D'}. Plataforma: {r['platform'] or 'N/D'}. Calificación: {r['rating'] or 'N/D'}. Sinopsis: {r['synopsis']}" for r in selected)
 sources=[{'id':str(r['id']),'title':r['title'],'type':'catalog'} for r in selected]
 return context,sources
@app.post('/api/v1/ai/rag/chat')
def rag(body:ChatIn,user=Depends(current)):
 enabled('rag');ensure_quota(user);context,sources=rag_reply(body.message)
 if not sources: answer='No encontré información suficiente en el catálogo para responder con fiabilidad.';incoming=len(body.message.split());outgoing=len(answer.split())
 else:
  memory=[]
  if body.conversation_id:
   with db() as c: memory=[{'role':r['role'],'content':r['content']} for r in c.execute(text('SELECT role,content FROM chat_messages WHERE conversation_id=:c ORDER BY created_at DESC LIMIT 6'),{'c':body.conversation_id}).mappings()][::-1]
  system='Eres CineIA. Responde en español únicamente con el contexto del catálogo. Cita los títulos usados. Si el contexto no basta, indícalo claramente. No inventes datos.\nCONTEXTO:\n'+context
  answer,incoming,outgoing=groq_chat([{'role':'system','content':system},*memory,{'role':'user','content':body.message}])
 record(user,'rag',incoming,outgoing)
 with db() as c:
  cid=body.conversation_id or str(c.execute(text("INSERT INTO conversations(user_id,service_code) VALUES(:u,'rag') RETURNING id"),{'u':user['id']}).scalar())
  c.execute(text("INSERT INTO chat_messages(conversation_id,role,content,sources) VALUES(:c,'user',:m,'[]'),(:c,'assistant',:a,CAST(:s AS jsonb))"),{'c':cid,'m':body.message,'a':answer,'s':json.dumps(sources)});c.commit()
 return {'conversation_id':cid,'answer':answer,'sources':sources,'usage':{'input_tokens':incoming,'output_tokens':outgoing,'total_tokens':incoming+outgoing}}
@app.post('/api/v1/ai/recommend')
def recommend(body:ChatIn,user=Depends(current)):
 enabled('recommend');ensure_quota(user);context,sources=rag_reply(body.message)
 if not sources: context,sources=preference_candidates(body.message)
 if not sources:return {'answer':'No encontré candidatos suficientes en el catálogo para recomendar. Prueba con un título o género disponible.','sources':[],'usage':{'total_tokens':0}}
 external=[]
 for source in sources[:3]:
  detail=wikipedia_details(source['title'])
  if detail and detail['extract']:
   context+=f"\n- Fuente externa Wikipedia para {detail['title']}: {detail['extract']}"
   external.append({'title':detail['title'],'type':'wikipedia','url':detail['url']})
 answer,incoming,outgoing=groq_chat([{'role':'system','content':'Eres un agente recomendador de CineIA. Compara los candidatos en varios pasos, explica por qué encajan con la preferencia y menciona limitaciones. Usa solo estos datos y diferencia catálogo de fuente externa:\n'+context},{'role':'user','content':body.message}]);all_sources=sources+external;record(user,'recommend',incoming,outgoing);cid=save_exchange(user,'recommend',body.message,answer,all_sources);return {'conversation_id':cid,'answer':answer,'sources':all_sources,'usage':{'input_tokens':incoming,'output_tokens':outgoing,'total_tokens':incoming+outgoing}}
@app.post('/api/v1/ai/news')
def news(body:ChatIn,user=Depends(current)):
 enabled('news');ensure_quota(user);articles=google_news(body.message)
 if not articles:return {'answer':'No encontré novedades verificables en la fuente externa para esa consulta.','sources':[],'usage':{'total_tokens':0}}
 context='\n'.join(f"- {a['title']} | {a['date']} | {a['url']}" for a in articles)
 answer,incoming,outgoing=groq_chat([{'role':'system','content':'Eres el agente de novedades de CineIA. Resume en español únicamente estas noticias RSS. Incluye fechas cuando existan, separa hechos de incertidumbre y no inventes información.\nFUENTES:\n'+context},{'role':'user','content':body.message}]);sources=[{'title':a['title'],'type':'google_news_rss','url':a['url'],'date':a['date']} for a in articles];record(user,'news',incoming,outgoing);cid=save_exchange(user,'news',body.message,answer,sources);return {'conversation_id':cid,'answer':answer,'sources':sources,'usage':{'input_tokens':incoming,'output_tokens':outgoing,'total_tokens':incoming+outgoing}}
@app.get('/api/v1/history/me')
def history(user=Depends(current)):
 with db() as c:return [dict(x) for x in c.execute(text("SELECT cm.role,cm.content,cm.sources,cm.created_at,c.service_code FROM chat_messages cm JOIN conversations c ON c.id=cm.conversation_id WHERE c.user_id=:u ORDER BY cm.created_at DESC LIMIT 100"),{'u':user['id']}).mappings()]
@app.get('/api/v1/usage/me')
def my_usage(user=Depends(current)):
 with db() as c:return [dict(x) for x in c.execute(text('SELECT service_code,coalesce(sum(total_tokens),0) total_tokens,count(*) requests FROM usage_logs WHERE user_id=:u GROUP BY service_code'),{'u':user['id']}).mappings()]
@app.get('/api/v1/usage/me/summary')
def my_usage_summary(user=Depends(current)):
 with db() as c:
  row=c.execute(text("""SELECT u.token_limit_monthly,
   coalesce(sum(l.request_tokens),0) input_tokens,coalesce(sum(l.response_tokens),0) output_tokens,
   coalesce(sum(l.total_tokens),0) total_tokens,count(l.id) requests
   FROM app_users u LEFT JOIN usage_logs l ON l.user_id=u.id
    AND date_trunc('month',l.created_at)=date_trunc('month',now())
   WHERE u.id=:u GROUP BY u.token_limit_monthly"""),{'u':user['id']}).mappings().one()
  result=dict(row);result['remaining_tokens']=max(0,result['token_limit_monthly']-result['total_tokens']);return result
@app.get('/api/v1/admin/usage')
def usage(date_from:str|None=None,date_to:str|None=None,service:str|None=None,user_id:str|None=None,user=Depends(admin)):
 with db() as c:return [dict(x) for x in c.execute(text("""SELECT date(l.created_at) date,l.service_code service,u.email user_email,count(*) requests,
  sum(l.request_tokens) input_tokens,sum(l.response_tokens) output_tokens,sum(l.total_tokens) total_tokens
  FROM usage_logs l JOIN app_users u ON u.id=l.user_id
  WHERE (CAST(:s AS text) IS NULL OR l.service_code=CAST(:s AS text))
   AND (CAST(:f AS date) IS NULL OR date(l.created_at)>=CAST(:f AS date))
   AND (CAST(:t AS date) IS NULL OR date(l.created_at)<=CAST(:t AS date))
   AND (CAST(:uid AS uuid) IS NULL OR l.user_id=CAST(:uid AS uuid))
  GROUP BY date(l.created_at),l.service_code,u.email ORDER BY date,service,user_email"""),{'s':service,'f':date_from,'t':date_to,'uid':user_id}).mappings()]
@app.get('/api/v1/bi/consumption')
def bi(api_key:str=Query(...),date_from:str|None=None,date_to:str|None=None,service:str|None=None):
 if api_key!=BI_API_KEY: raise HTTPException(401,'Clave BI inválida')
 return usage(date_from,date_to,service,None,{'role':'ADMIN'})
