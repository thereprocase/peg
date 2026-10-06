'use strict';
(async()=>{
  const $=id=>document.getElementById(id);
  const families={pegstr:'Pegstr remixes',arrays:'Seat arrays','bin-expansion':'Flat-bottom bins','solder-modules':'Solder station','shaft-holders':'Shaft holders','shaft-sampler':'Shaft sampler',workshop:'Screw dish',accessories:'Removable accessories'};
  const pegstrFamilies=['pegstr','arrays','bin-expansion'];
  const reproFamilies=['solder-modules','shaft-holders','shaft-sampler','workshop','accessories'];
  const belongs=(row,family)=>family==='all'||(family==='repro'&&reproFamilies.includes(row.family))||(family==='pegstr-all'&&pegstrFamilies.includes(row.family))||(family==='new'&&row.new_design)||(family==='solder-modules'&&row.family==='accessories')||(family==='expansion'?['arrays','bin-expansion'].includes(row.family):family==='screwdriver'?['shaft-holders','shaft-sampler'].includes(row.family):row.family===family);
  let catalog,selected,view='installed';
  function modelView(next){
    view=next;const asset=selected.assets[next+'_glb'];const model=$('model');
    $('model-status').textContent='Loading '+(next==='print'?'print orientation':'installed view')+'…';
    model.src=asset;model.poster=selected.assets[next+'_png']||selected.assets.preview_png;
    model.alt=selected.name+' · '+(next==='print'?selected.pose+' print orientation':'installed mounting orientation');
    model.cameraOrbit=next==='print'?'35deg 60deg auto':'145deg 70deg auto';
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===next)));
  }
  function select(record,scroll=false){
    selected=record;$('detail').hidden=false;$('part-id').textContent=record.id+' · '+families[record.family];$('part-name').textContent=record.name;
    $('part-version').textContent=record.version+' · '+record.fit_label;
    $('orientation').textContent=record.notes.orientation;$('upper').textContent=record.notes.upper_pegs;
    $('bounds').textContent='Print bounds: '+record.print_bounds_mm.map(n=>Number(n).toFixed(1)).join(' × ')+' mm.';
    $('supports').textContent=record.notes.supports;$('mount').textContent=record.notes.mount;
    $('qualification').textContent=record.notes.qualification;$('credit').textContent=record.credit||'';
    const links=[['print_stl',record.kind==='accessory'?'Vase-mode filled STL':'Print STL'],['installed_stl','Installed STL'],['installed_step','Installed STEP'],['print_step','Print STEP'],['cad_bundle','CAD + source'],['checks','Mounting checks']];
    $('downloads').replaceChildren(...links.filter(([k])=>record.assets[k]).map(([k,label])=>{const a=document.createElement('a');a.href=record.assets[k];a.textContent=label;if(k.endsWith('stl'))a.setAttribute('download','');return a;}),...(record.extra_downloads||[]).map(item=>{const a=document.createElement('a');a.href=item.url;a.textContent=item.label;return a;}));
    document.querySelectorAll('.part').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.id===record.id)));
    modelView(view);if(scroll)$('detail').scrollIntoView({block:'start'});
  }
  function render(){
    const query=$('search').value.trim().toLowerCase(),family=$('family').value;
    const rows=catalog.parts.filter(r=>belongs(r,family)&&(!query||(r.id+' '+r.name).toLowerCase().includes(query)));
    const headings={repro:['Repro bespoke models','21 holders and accessories for soldering tools, spools, tweezers, screwdrivers and workshop storage. Select a model for its CAD, print orientation and physical test status.'],'pegstr-all':['Pegstr remix / expansion','11 remounted Pegstr designs, 8 seat arrays and 4 flat-bottom bins, based on Marius Gheorghescu’s Pegstr. Each model retains attribution and source recipes.']};
    const heading=headings[family]||['Repro and Pegstr models','44 holders and accessories across Repro’s bespoke designs and the Pegstr remix and expansion collection. Each entry includes CAD downloads, print orientation and model-specific checks.'];
    $('bespoke-review-link').hidden=pegstrFamilies.includes(family)||family==='pegstr-all'||family==='expansion';
    $('collection-title').textContent=heading[0];$('collection-description').textContent=heading[1];document.title=heading[0]+' · thereprocase';
    $('count').textContent=rows.length+' of '+catalog.parts.length+' designs';$('empty').hidden=rows.length>0;
    $('parts').replaceChildren(...rows.map(r=>{const b=document.createElement('button');b.className='part';b.dataset.id=r.id;b.setAttribute('aria-pressed',String(selected?.id===r.id));
      const img=document.createElement('img');img.src=r.assets.preview_png;img.alt='';img.loading='lazy';
      const title=document.createElement('span');title.append(document.createTextNode(r.id+' · '+r.name));const small=document.createElement('small');small.textContent=(r.notes.status?r.notes.status+' · ':'')+r.pose+' · '+families[r.family];title.append(small);b.append(img,title);
      b.addEventListener('click',()=>{history.replaceState(null,'','#'+encodeURIComponent(r.id));select(r,true);});return b;}));
  }
  try{
    const response=await fetch('catalog.json');if(!response.ok)throw Error('Catalog HTTP '+response.status);catalog=await response.json();
    const family=new URLSearchParams(location.search).get('family');if(families[family]||['expansion','screwdriver','new','repro','pegstr-all'].includes(family))$('family').value=family;
    const id=decodeURIComponent(location.hash.slice(1));const initial=catalog.parts.find(r=>r.id===id)||catalog.parts.find(r=>belongs(r,$('family').value));
    render();await customElements.whenDefined('model-viewer');if(initial)select(initial,Boolean(id));$('build').textContent=catalog.build_note;
    $('search').addEventListener('input',render);$('family').addEventListener('change',()=>{
      const url=new URL(location.href);url.searchParams.set('family',$('family').value);url.hash='';history.replaceState(null,'',url);
      const first=catalog.parts.find(r=>belongs(r,$('family').value));if(first)select(first);render();
    });
    document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>modelView(b.dataset.view)));
    $('model').addEventListener('load',()=>{$('model-status').textContent=view==='print'?'Print STL uses this orientation.':'Rotate to inspect the integral mounts.';});
    $('model').addEventListener('error',()=>{$('model-status').textContent='The 3D preview could not load. STL and CAD downloads remain available.';});
    window.addEventListener('hashchange',()=>{const r=catalog.parts.find(r=>r.id===decodeURIComponent(location.hash.slice(1)));if(r)select(r,true);});
    window.currentPegs={catalog,get selected(){return selected},get view(){return view},select,modelView};
  }catch(error){$('count').textContent='The collection could not load. Refresh to try again.';console.error(error);}
})();
