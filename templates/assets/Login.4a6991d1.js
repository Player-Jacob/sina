import{q as e,M as s,w as t,a,z as r,E as i,b as l,r as c,o as n,g as o,f as u,e as d,m,t as g,u as p,i as h,p as f,l as v,B as y,j as x}from"./vendor.3e1d1ca5.js";import{_ as b,c as _,s as j,a as k}from"./index.4bf88f5f.js";const q={class:"login-container columnCC"},C={class:"title-container"},I={class:"title text-center"},L=(e=>(f("data-v-2529d779"),e=e(),v(),e))((()=>m("div",{class:"image-slot",style:{height:"inherit","background-color":"#f7f5fa"}},[m("i",{class:"el-icon-picture-outline",style:{"vertical-align":"middle"}}),m("p",null,"扫码登录")],-1))),Q={class:"tip-message"},w=y(" Login "),z={name:"Login"};var M=b(Object.assign(z,{setup:function(f){let{proxy:v}=x(),y=e({otherQuery:{},redirect:void 0});const b=s();t(b,(e=>{const s=e.query;s&&(y.redirect=s.redirect,y.otherQuery=(e=>Object.keys(e).reduce(((s,t)=>("redirect"!==t&&(s[t]=e[t]),s)),{}))(s))}),{immediate:!0});let z=a(!1),M=a(""),O=a("");const $=r();let B=setInterval((()=>{_().then((e=>{const{isLogin:s}=e.data;s&&(clearInterval(B),j(s),v.$router.push({path:y.redirect||"/",query:y.otherQuery}),i({message:"登录成功",type:"success"}))})).catch((e=>{}))}),5e3),E=()=>{z.value=!0,$.dispatch("user/login").then((e=>{const{isLogin:s}=e;s?(clearInterval(B),j(s),v.$router.push({path:y.redirect||"/",query:y.otherQuery}),i({message:"登录成功",type:"success"})):(O.value=e.image,z.value=!1)})).catch((e=>{M.value=e.msg,v.sleepMixin(30).then((()=>{z.value=!1}))}))};return l((()=>{E()})),(e,s)=>{const t=c("el-image"),a=c("el-button"),r=c("el-form");return n(),o("div",q,[u(r,{ref:(e,s)=>{s.refloginForm=e},size:"medium",class:"login-form text-center",rules:e.formRulesMixin},{default:d((()=>[m("div",C,[m("h3",I,g(p(k).title),1)]),u(t,{style:{width:"180px",height:"180px"},src:p(O),fit:"scale-down"},{error:d((()=>[L])),_:1},8,["src"]),m("div",Q,g(p(M)),1),u(a,{loading:p(z),type:"primary",class:"login-btn",size:"medium",onClick:h(p(E),["prevent"])},{default:d((()=>[w])),_:1},8,["loading","onClick"])])),_:1},8,["rules"])])}}}),[["__scopeId","data-v-2529d779"]]);export{M as default};
