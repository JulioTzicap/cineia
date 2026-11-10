import {useEffect,useState} from 'react';
import {api} from '../api/client';
import type {AIService,Session,Source} from '../types';

type ServiceCode='rag'|'recommend'|'news';
type AIResponse={conversation_id?:string;answer:string;sources:Source[];usage?:{total_tokens:number}};

const serviceGuide:Record<ServiceCode,{title:string;subtitle:string;description:string;examples:string[];button:string;working:string}>={
 rag:{title:'Chat con el catálogo',subtitle:'Consulta películas y videojuegos disponibles',description:'Pregunta por títulos, géneros, plataformas o detalles del catálogo de CineIA. El asistente responde usando solamente la información registrada.',examples:['¿De qué trata Interestelar?','¿Qué películas de ciencia ficción hay disponibles?','Muéstrame videojuegos de aventura con buena calificación.'],button:'Consultar catálogo',working:'Consultando catálogo…'},
 recommend:{title:'Recomendador inteligente',subtitle:'Encuentra opciones según tus gustos',description:'Describe lo que te gustaría ver o jugar. El recomendador compara títulos del catálogo y puede complementar la respuesta con fuentes externas.',examples:['Recomiéndame ciencia ficción con buena calificación.','Quiero una película de aventura para ver este fin de semana.','Busco un videojuego de acción con historia interesante.'],button:'Buscar recomendaciones',working:'Buscando recomendaciones…'},
 news:{title:'Novedades de cine y videojuegos',subtitle:'Busca noticias con fuentes verificables',description:'Escribe una película, videojuego, actor, estudio o tema. El servicio consulta noticias recientes y muestra sus fuentes.',examples:['Dune película','Novedades de videojuegos de Nintendo','Noticias recientes de Marvel Studios'],button:'Buscar novedades',working:'Consultando noticias…'}
};

export function AIPage({session}:{session:Session}){
 const [selected,setSelected]=useState<ServiceCode>('rag');
 const [message,setMessage]=useState('');
 const [answer,setAnswer]=useState('');
 const [sources,setSources]=useState<Source[]>([]);
 const [services,setServices]=useState<AIService[]>([]);
 const [conversation,setConversation]=useState<string>();
 const [busy,setBusy]=useState('');
 const [error,setError]=useState('');
 const [tokens,setTokens]=useState(0);
 useEffect(()=>{api<AIService[]>(session,'/api/v1/services').then(setServices).catch(e=>setError(e.message))},[session]);
 const active=(code:ServiceCode)=>services.find(s=>s.code===code)?.is_active??false;
 const guide=serviceGuide[selected];
 const selectService=(code:ServiceCode)=>{setSelected(code);setMessage('');setAnswer('');setSources([]);setTokens(0);setError('')};
 const ask=async()=>{
  if(!active(selected)){setError('Este servicio está desactivado por un administrador.');return}
  if(message.trim().length<2){setError('Elige un ejemplo o escribe una consulta de al menos dos caracteres.');return}
  setBusy(selected);setError('');
  try{
   const path=selected==='rag'?'/api/v1/ai/rag/chat':'/api/v1/ai/'+selected;
   const data=await api<AIResponse>(session,path,{method:'POST',body:JSON.stringify({message,conversation_id:selected==='rag'?conversation:null})});
   setAnswer(data.answer);setSources(data.sources||[]);setTokens(data.usage?.total_tokens||0);
   if(selected==='rag'&&data.conversation_id)setConversation(data.conversation_id);
  }catch(e){setError((e as Error).message)}finally{setBusy('')}
 };
 return <section className="ai-workspace">
  <div className="section-head"><div><h2>Servicios IA</h2><p>Elige un servicio y realiza una consulta guiada.</p></div></div>
  <div className="ai-service-picker" role="tablist" aria-label="Servicios de inteligencia artificial">
   {(Object.keys(serviceGuide) as ServiceCode[]).map(code=>{
    const item=serviceGuide[code];
    return <button key={code} role="tab" aria-selected={selected===code} className={'ai-service-card '+(selected===code?'selected':'')} onClick={()=>selectService(code)}>
     <span className="ai-service-card-top"><strong>{item.title}</strong><span className={'pill '+(active(code)?'ok':'off')}>{active(code)?'Activo':'Inactivo'}</span></span>
     <small>{item.subtitle}</small>
    </button>
   })}
  </div>
  <article className="ai-chat-panel">
   <div className="ai-chat-heading"><div><span className="eyebrow">{guide.subtitle}</span><h3>{guide.title}</h3><p>{guide.description}</p></div><span className={'service-dot '+(active(selected)?'ready':'disabled')}>{active(selected)?'Listo para consultar':'Servicio desactivado'}</span></div>
   <div className="example-prompts"><strong>Prueba con uno de estos ejemplos:</strong><div>{guide.examples.map(example=><button type="button" key={example} className="prompt-chip" onClick={()=>{setMessage(example);setError('')}}>{example}</button>)}</div></div>
   <label className="ai-message-label">Tu consulta<textarea value={message} onChange={e=>setMessage(e.target.value)} placeholder={guide.examples[0]} aria-label="Consulta para el servicio de IA"/></label>
   <div className="ai-submit-row"><small>{selected==='rag'?'Puedes hacer una segunda pregunta para conservar el contexto de la conversación.':'Las respuestas mostrarán las fuentes utilizadas cuando estén disponibles.'}</small><button disabled={!!busy||!active(selected)} onClick={ask}>{busy===selected?guide.working:guide.button}</button></div>
   {error&&<p className="error">{error}</p>}
   {answer&&<article className="ai-result"><div className="result-head"><h3>Respuesta</h3><span className="pill">{tokens} tokens</span></div><p className="answer">{answer}</p>{sources.length>0&&<><strong>Fuentes</strong><ul>{sources.map((s,i)=><li key={`${s.title}-${i}`}>{s.url?<a href={s.url} target="_blank" rel="noreferrer">{s.title}</a>:s.title} <small>{s.type}{s.date?` · ${s.date}`:''}</small></li>)}</ul></>}</article>}
  </article>
 </section>
}
