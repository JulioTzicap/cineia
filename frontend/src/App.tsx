import {useEffect,useState} from 'react';
import type {Session,Tab} from './types';
import {LoginPage} from './pages/LoginPage';
import {AIPage} from './pages/AIPage';
import {CatalogPage} from './pages/CatalogPage';
import {UsersPage} from './pages/UsersPage';
import {ServicesPage} from './pages/ServicesPage';
import {UsagePage} from './pages/UsagePage';
import {HistoryPage} from './pages/HistoryPage';
import {api} from './api/client';
const storageKey='cineia.session';
const readSession=():Session|null=>{try{return JSON.parse(sessionStorage.getItem(storageKey)||'null')}catch{return null}};
export default function App(){const [session,setSession]=useState<Session|null>(readSession),[tab,setTab]=useState<Tab>('ia'),[expired,setExpired]=useState(false);const login=(value:Session)=>{sessionStorage.setItem(storageKey,JSON.stringify(value));setSession(value);setExpired(false)};const clearSession=()=>{sessionStorage.removeItem(storageKey);setSession(null);setTab('ia')};const logout=()=>{if(session)void api(session,'/api/v1/auth/logout',{method:'POST'}).catch(()=>undefined);clearSession()};useEffect(()=>{const handler=()=>{setExpired(true);clearSession()};window.addEventListener('cineia:unauthorized',handler);const stored=readSession();if(stored)void api<Session['user']>(stored,'/api/v1/auth/me').then(user=>login({...stored,user})).catch(()=>clearSession());return()=>window.removeEventListener('cineia:unauthorized',handler)},[]);if(!session)return <><LoginPage onLogin={login}/>{expired&&<div className="toast">La sesión venció o el usuario está inactivo. Inicia sesión nuevamente.</div>}</>;const admin=session.user.role==='ADMIN';return <main><header><div><h1>CineIA</h1><span>{session.user.name} · {session.user.role}</span></div><button className="secondary" onClick={logout}>Cerrar sesión</button></header><nav>{([['ia','Servicios IA'],['catalog','Catálogo'],['history','Historial'],['usage','Consumo']] as [Tab,string][]).map(([id,label])=><button className={tab===id?'active':''} key={id} onClick={()=>setTab(id)}>{label}</button>)}{admin&&<><button className={tab==='users'?'active':''} onClick={()=>setTab('users')}>Usuarios</button><button className={tab==='services'?'active':''} onClick={()=>setTab('services')}>Configuración IA</button></>}</nav>{tab==='ia'&&<AIPage session={session}/>} {tab==='catalog'&&<CatalogPage session={session}/>} {tab==='history'&&<HistoryPage session={session}/>} {tab==='usage'&&<UsagePage session={session}/>} {tab==='users'&&admin&&<UsersPage session={session}/>} {tab==='services'&&admin&&<ServicesPage session={session}/>}</main>}
