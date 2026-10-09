const viewer=document.querySelector('#rack-viewer');
document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
  viewer.src=button.dataset.mode+'.glb?v=2';
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
viewer.addEventListener('load',async()=>{
  await viewer.updateFraming();
  viewer.cameraTarget='auto auto auto';
  viewer.cameraOrbit=viewer.getAttribute('src').startsWith('print.glb')?'35deg 60deg 115%':'30deg 70deg 115%';
  viewer.jumpCameraToGoal();
});
