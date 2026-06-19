// Gacha Zoo — API familiar (Pages _worker.js)
function json(d,s=200){ return new Response(JSON.stringify(d),{status:s,headers:{'content-type':'application/json'}}); }
function uid(){ return crypto.randomUUID(); }
function week(){ const d=new Date(); const o=new Date(d.getFullYear(),0,1);
  return d.getFullYear()+'-'+Math.ceil(((d-o)/864e5+o.getDay()+1)/7); }

async function auth(env,body){
  if(!body || !body.id || !body.pin) return null;
  const p=await env.DB.prepare('SELECT * FROM players WHERE id=?').bind(body.id).first();
  return (p && p.pin===String(body.pin)) ? p : null;
}

async function api(req,env,url){
  if(req.method!=='POST') return json({err:'POST only'},405);
  let b; try{ b=await req.json(); }catch(e){ return json({err:'bad json'},400); }
  const route=url.pathname.slice(5); // tras /api/

  if(route==='signup'){
    const name=String(b.name||'').trim().slice(0,14);
    const pin=String(b.pin||'').trim();
    if(name.length<2 || !/^\d{4}$/.test(pin)) return json({err:'nombre (mín. 2) y PIN de 4 dígitos'},400);
    const ex=await env.DB.prepare('SELECT id FROM players WHERE name=? COLLATE BINARY').bind(name).first();
    if(ex) return json({err:'ese nombre ya está cogido — si es tuyo, usa «Entrar»'},409);
    const id=uid();
    await env.DB.prepare('INSERT INTO players(id,name,pin,avatar,created,family) VALUES(?,?,?,?,?,NULL)')
      .bind(id,name,pin,String(b.avatar||'gato'),Date.now()).run();
    return json({ok:1,id,name,family:null});
  }

  if(route==='login'){
    const name=String(b.name||'').trim();
    const p=await env.DB.prepare('SELECT * FROM players WHERE name=? COLLATE BINARY').bind(name).first();
    if(!p) return json({err:'no existe ese usuario (ojo: las mayúsculas cuentan)'},404);
    if(p.pin!==String(b.pin||'').trim()) return json({err:'PIN incorrecto'},403);
    return json({ok:1,id:p.id,name:p.name,family:p.family||null});
  }

  if(route==='register'){
    if(String(b.family||'').toLowerCase()!==String(env.FAMILY_CODE).toLowerCase())
      return json({err:'código de familia incorrecto'},403);
    const name=String(b.name||'').trim().slice(0,14);
    const pin=String(b.pin||'').trim();
    if(!name || !/^\d{4}$/.test(pin)) return json({err:'nombre y PIN de 4 dígitos'},400);
    const ex=await env.DB.prepare('SELECT * FROM players WHERE name=?').bind(name).first();
    if(ex){
      if(ex.pin===pin) return json({ok:1,id:ex.id,name:ex.name}); // login
      return json({err:'ese nombre ya existe (PIN incorrecto)'},403);
    }
    const id=uid();
    await env.DB.prepare('INSERT INTO players(id,name,pin,avatar,created,family) VALUES(?,?,?,?,?,?)')
      .bind(id,name,pin,String(b.avatar||'gato'),Date.now(),String(env.FAMILY_CODE).toLowerCase()).run();
    return json({ok:1,id,name});
  }

  const me=await auth(env,b);
  if(!me) return json({err:'auth'},401);

  if(route==='famNew'){
    const raw=String(b.fname||'').trim().toLowerCase().replace(/[^a-z0-9ñ-]/g,'-').replace(/-+/g,'-').replace(/^-|-$/g,'').slice(0,16);
    const code= raw.length>=3 ? 'zoo-'+raw : 'zoo-'+Math.random().toString(36).slice(2,7);
    const ex=await env.DB.prepare('SELECT id FROM players WHERE family=? AND id<>?').bind(code,me.id).first();
    if(ex) return json({err:'ese código ya lo usa otra familia, elige otro nombre'},409);
    await env.DB.prepare('UPDATE players SET family=? WHERE id=?').bind(code,me.id).run();
    return json({ok:1,family:code});
  }

  if(route==='famJoin'){
    const code=String(b.code||'').trim().toLowerCase();
    if(!code) return json({err:'falta el código'},400);
    const ex=await env.DB.prepare('SELECT id FROM players WHERE family=?').bind(code).first();
    if(!ex) return json({err:'no existe ninguna familia con ese código'},404);
    await env.DB.prepare('UPDATE players SET family=? WHERE id=?').bind(code,me.id).run();
    return json({ok:1,family:code});
  }

  if(route==='famLeave'){
    const open=await env.DB.prepare("SELECT id FROM offers WHERE seller=? AND status='open'").bind(me.id).first();
    if(open) return json({err:'retira antes tus ofertas del tablón'},409);
    await env.DB.prepare('UPDATE players SET family=NULL WHERE id=?').bind(me.id).run();
    return json({ok:1});
  }

  if(route==='sync'){
    if(b.save){
      await env.DB.prepare(
        'INSERT INTO saves_prev(player,payload,updated) SELECT player,payload,updated FROM saves WHERE player=? ON CONFLICT(player) DO UPDATE SET payload=excluded.payload,updated=excluded.updated')
        .bind(me.id).run();
      await env.DB.prepare(
        'INSERT INTO saves(player,payload,updated) VALUES(?,?,?) ON CONFLICT(player) DO UPDATE SET payload=?,updated=?')
        .bind(me.id,JSON.stringify(b.save),Date.now(),JSON.stringify(b.save),Date.now()).run();
    }
    if(b.zoo) await env.DB.prepare(
      'INSERT INTO zoos(player,payload,updated) VALUES(?,?,?) ON CONFLICT(player) DO UPDATE SET payload=?,updated=?')
      .bind(me.id,JSON.stringify(b.zoo),Date.now(),JSON.stringify(b.zoo),Date.now()).run();
    if(b.scores){
      const w=week();
      for(const [g,sc] of Object.entries(b.scores)){
        const v=Math.max(0,parseInt(sc,10)||0);
        if(v>0) await env.DB.prepare(
          'INSERT INTO scores(player,game,score,week) VALUES(?,?,?,?) ON CONFLICT(player,game,week) DO UPDATE SET score=MAX(score,?)')
          .bind(me.id,g,v,w,v).run();
      }
    }
    const deltas=(await env.DB.prepare('SELECT id,payload FROM deltas WHERE player=? AND applied=0 ORDER BY id').bind(me.id).all()).results||[];
    if(deltas.length) await env.DB.prepare('UPDATE deltas SET applied=1 WHERE player=? AND applied=0').bind(me.id).run();
    let offers=[], players=[], ranking={};
    if(me.family){
      offers=(await env.DB.prepare(
        `SELECT o.id,o.seller,p.name sellerName,o.kind,o.animal,o.shiny,o.price,o.want
         FROM offers o JOIN players p ON p.id=o.seller WHERE o.status='open' AND p.family=? ORDER BY o.created DESC LIMIT 30`)
        .bind(me.family).all()).results||[];
      players=(await env.DB.prepare('SELECT id,name,avatar FROM players WHERE family=? ORDER BY created').bind(me.family).all()).results||[];
      const rk=(await env.DB.prepare(
        `SELECT s.game,p.name,s.score FROM scores s JOIN players p ON p.id=s.player
         WHERE s.week=? AND p.family=? ORDER BY s.game,s.score DESC`).bind(week(),me.family).all()).results||[];
      for(const r of rk){ (ranking[r.game]=ranking[r.game]||[]); if(ranking[r.game].length<3) ranking[r.game].push({name:r.name,score:r.score}); }
    }
    return json({ok:1, me:{name:me.name,family:me.family||null},
      deltas:deltas.map(d=>({id:d.id,...JSON.parse(d.payload)})), offers, players, ranking, week:week()});
  }

  if(route==='offer'){
    const kind=b.kind==='venta'?'venta':'trueque';
    const price=Math.max(1,Math.min(99,parseInt(b.price,10)||1));
    const id=uid();
    await env.DB.prepare(
      'INSERT INTO offers(id,seller,kind,animal,shiny,price,want,status,created) VALUES(?,?,?,?,?,?,?,?,?)')
      .bind(id,me.id,kind,String(b.animal),b.shiny?1:0,kind==='venta'?price:null,
        kind==='trueque'?String(b.want||'r:comun'):null,'open',Date.now()).run();
    return json({ok:1,id});
  }

  if(route==='cancel'){
    const r=await env.DB.prepare("UPDATE offers SET status='cancel',closed=? WHERE id=? AND seller=? AND status='open'")
      .bind(Date.now(),String(b.offerId),me.id).run();
    return json({ok:r.meta.changes>0});
  }

  if(route==='take'){
    const o=await env.DB.prepare(
      "SELECT o.* FROM offers o JOIN players p ON p.id=o.seller WHERE o.id=? AND o.status='open' AND p.family=?")
      .bind(String(b.offerId), me.family||'').first();
    if(!o) return json({err:'oferta ya no disponible'},409);
    if(o.seller===me.id) return json({err:'es tu propia oferta'},400);
    const r=await env.DB.prepare("UPDATE offers SET status='done',buyer=?,closed=? WHERE id=? AND status='open'")
      .bind(me.id,Date.now(),o.id).run();
    if(!r.meta.changes) return json({err:'alguien se adelantó'},409);
    let sellerDelta;
    if(o.kind==='venta'){
      sellerDelta={coins:o.price, msg:'💰 '+me.name+' te compró a tu '+o.animal+(o.shiny?' ✨':'')+' por '+o.price+' 🪙'};
    } else {
      const pay=String(b.payAnimal||'');
      if(!pay) return json({err:'falta tu animal de cambio'},400);
      sellerDelta={add:{a:pay,sh:b.payShiny?1:0}, msg:'🔄 '+me.name+' aceptó tu trueque: te llega '+pay};
    }
    await env.DB.prepare('INSERT INTO deltas(player,payload,created) VALUES(?,?,?)')
      .bind(o.seller,JSON.stringify(sellerDelta),Date.now()).run();
    return json({ok:1, animal:o.animal, shiny:o.shiny, price:o.price, kind:o.kind});
  }

  if(route==='load'){
    const tbl=b.prev?'saves_prev':'saves';
    const sv=await env.DB.prepare('SELECT payload,updated FROM '+tbl+' WHERE player=?').bind(me.id).first();
    if(!sv) return json({ok:1,save:null});
    return json({ok:1,save:JSON.parse(sv.payload),updated:sv.updated});
  }

  if(route==='zoo'){
    const z=await env.DB.prepare('SELECT z.payload,p.name FROM zoos z JOIN players p ON p.id=z.player WHERE z.player=? AND p.family=?')
      .bind(String(b.target), me.family||'').first();
    if(!z) return json({err:'sin datos'},404);
    return json({ok:1,name:z.name,zoo:JSON.parse(z.payload)});
  }

  return json({err:'ruta desconocida'},404);
}

export default {
  async fetch(req,env){
    const url=new URL(req.url);
    if(url.pathname.startsWith('/api/')){
      try{ return await api(req,env,url); }
      catch(e){ return json({err:'server: '+e.message},500); }
    }
    return env.ASSETS.fetch(req);
  }
};
