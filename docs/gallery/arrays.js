"use strict";
document.querySelectorAll('.array-card details').forEach(detail=>detail.addEventListener('toggle',()=>{if(!detail.open)return;const viewer=detail.querySelector('model-viewer');if(viewer&&!viewer.src)viewer.src=viewer.dataset.src;}));
