/* Shared display treatment for the pinned model-viewer build.
 * Only preview shaders change; source geometry and download materials stay intact.
 */
(() => {
  const style = document.createElement('style');
  style.textContent = `model-viewer { background: radial-gradient(ellipse at 35% 18%, #fffef8 0%, #f1eee3 60%, #dedbcf 100%) !important; }`;
  document.head.append(style);
  const symbol = (object, name) => Object.getOwnPropertySymbols(object).find(key => key.description === name);
  const shader = `
    // Camera-space workbench lamps: large upper-left key and right-hand fill.
    vec3 benchNormal = normalize(normal);
    float benchKey = dot(benchNormal, normalize(vec3(-0.45, 0.8, 0.65)));
    float benchFill = max(dot(benchNormal, normalize(vec3(0.8, 0.2, 0.5))), 0.0);
    float benchLight = benchKey + 0.22 * benchFill;
    float benchBand = benchLight < -0.2 ? 0.48 : benchLight < 0.25 ? 0.72 : benchLight < 0.65 ? 1.02 : 1.30;
    // A restrained silhouette edge keeps small lips legible against the bench.
    float benchEdge = smoothstep(0.0, 0.18, abs(dot(benchNormal, normalize(vViewPosition))));
    outgoingLight = diffuseColor.rgb * benchBand * mix(0.78, 1.0, benchEdge);
    #include <opaque_fragment>
  `;
  function shade(viewer) {
    let count = 0;
    for (const material of viewer.model?.materials || []) {
      const objects = material[symbol(material, 'correlatedObjects')];
      for (const native of objects || []) {
        if (!native.isMeshStandardMaterial) continue;
        if (!native.userData.workbenchCel) {
          const previous = native.onBeforeCompile;
          native.onBeforeCompile = function(program, renderer) {
            previous.call(this, program, renderer);
            program.fragmentShader = program.fragmentShader.replace('#include <opaque_fragment>', shader);
          };
          native.customProgramCacheKey = () => 'peg-workbench-cel-v1';
          native.userData.workbenchCel = true;
          native.needsUpdate = true;
        }
        count++;
      }
    }
    viewer.dataset.workbenchMaterials = String(count);
    const scene = viewer[symbol(viewer, 'scene')];
    scene?.queueRender();
  }
  function setup(viewer) {
    if (viewer.dataset.workbench) return;
    viewer.dataset.workbench = 'cel';
    viewer.setAttribute('environment-image', 'neutral');
    viewer.setAttribute('tone-mapping', 'neutral');
    viewer.setAttribute('exposure', '1');
    viewer.setAttribute('shadow-intensity', '0.8');
    viewer.setAttribute('shadow-softness', '0.85');
    viewer.addEventListener('load', () => shade(viewer));
    if (viewer.loaded) shade(viewer);
  }
  customElements.whenDefined('model-viewer').then(() => {
    document.querySelectorAll('model-viewer').forEach(setup);
    new MutationObserver(() => document.querySelectorAll('model-viewer').forEach(setup))
      .observe(document.body, {childList: true, subtree: true});
  });
})();
