const viewer=document.querySelector('model-viewer');
document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
  viewer.src=button.dataset.mode+'.glb';
  viewer.cameraOrbit=button.dataset.mode==='print'?'30deg 65deg auto':'0deg 75deg auto';
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
viewer.addEventListener('load',async()=>{
  await viewer.updateFraming();
  viewer.cameraTarget='auto auto auto';
  viewer.cameraOrbit=viewer.getAttribute('src')==='print.glb'?'30deg 65deg 115%':'0deg 75deg 115%';
  viewer.jumpCameraToGoal();
});
