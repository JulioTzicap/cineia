import type {Session} from '../types';
export const API_URL=import.meta.env.VITE_API_URL||'http://localhost:8000';
export class ApiError extends Error{status:number;constructor(message:string,status=0){super(message);this.status=status}}
export async function api<T>(session:Session|null,path:string,options:RequestInit={}):Promise<T>{
 try{
  const response=await fetch(API_URL+path,{...options,headers:{'Content-Type':'application/json',...(session?{Authorization:'Bearer '+session.access_token}:{}),...options.headers}});
  const data=response.status===204?null:await response.json().catch(()=>null);
  if(!response.ok){if(response.status===401)window.dispatchEvent(new Event('cineia:unauthorized'));throw new ApiError(data?.detail||`Error HTTP ${response.status}`,response.status)}
  return data as T;
 }catch(error){
  if(error instanceof ApiError)throw error;
  throw new ApiError('No se pudo conectar con la API. Comprueba que FastAPI esté encendido.',0);
 }
}
