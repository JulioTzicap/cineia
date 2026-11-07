export type Role='ADMIN'|'USER';
export type Session={access_token:string;user:{id:string;name:string;role:Role;email:string}};
export type CatalogItem={id:string;title:string;category:'MOVIE'|'GAME';synopsis:string;genre?:string;platform?:string;release_year?:number;rating?:number;is_active?:boolean};
export type AppUser={id:string;email:string;full_name:string;role:Role;is_active:boolean;token_limit_monthly:number;created_at?:string};
export type AIService={code:string;name:string;description:string;is_active:boolean};
export type Source={title:string;type:string;url?:string;date?:string};
export type Tab='ia'|'catalog'|'users'|'services'|'usage'|'history';
