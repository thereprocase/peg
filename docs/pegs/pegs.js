(async()=>{
 const status=document.getElementById('peg-status'),model=document.getElementById('peg-model'),choice=document.getElementById('peg-choice');
 try{
  const response=await fetch('pegs/catalog.json');if(!response.ok)throw new Error('Catalog unavailable');
  const data=await response.json();window.pegDownloads=data;
  for(const a of document.querySelectorAll('[data-pack]'))a.href=a.dataset.pack==='all'?data.all_formats:data.formats[a.dataset.pack];
  const rows=document.getElementById('peg-downloads');rows.replaceChildren();
  for(const part of data.parts){const row=document.createElement('tr');const name=document.createElement('td');name.textContent=part.name;row.append(name);for(const formats of [['step','freecad'],['iges','brep','stl','obj','3mf']]){const cell=document.createElement('td');if(formats.length>2)cell.className='peg-extra';for(const fmt of formats){if(cell.childNodes.length)cell.append(' · ');const link=document.createElement('a');link.href=part.links[fmt];link.textContent=fmt==='freecad'?'FCStd':fmt.toUpperCase();cell.append(link);}row.append(cell);}rows.append(row);}
  await customElements.whenDefined('model-viewer');
  model.addEventListener('load',()=>status.textContent='Drag to rotate · pinch or scroll to zoom');
  model.addEventListener('error',()=>status.textContent='Preview unavailable. CAD downloads are above.');
  choice.addEventListener('change',()=>{const part=data.parts.find(p=>p.id===choice.value);status.textContent='Loading '+part.name+'…';model.src='pegs/'+part.preview;model.alt=part.name+' with orange joining nub';});
  if(model.loaded)status.textContent='Drag to rotate · pinch or scroll to zoom';
 }catch(error){status.textContent='Preview unavailable. Use the format packs or release links above.';console.error(error);}
})();
