'use strict';
const el=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let catalog=[],side='front';
function cards(){const selected=catalog.filter(s=>!el('remix-filter').value||s.category===el('remix-filter').value);el('remix-count').textContent=`${selected.length} of 11 remixes`;el('remix-cards').innerHTML=selected.map(s=>`<article class="remix-card"><a href="?part=${s.id}" data-id="${s.id}" aria-label="Inspect ${esc(s.name)}"><img src="pegstr/${s.id}/${side}.png" alt="${esc(s.name)} — ${side==='front'?'front view':'flush back and replacement pegs'}" loading="lazy"></a><div class="copy"><span class="id">${s.id} / ${esc(s.category)}</span><h2>${esc(s.name)}</h2><p>${esc(s.description)}</p>${["P01","P09"].includes(s.id)?`<p><a href="arrays.html#${s.id}">Four more array sizes + generator ↗</a></p>`:""}<p>${s.bounds_mm.map(n=>Math.round(n)).join(' × ')} mm overall · ${s.mount_columns_x_mm.length*2} pegs</p></div><button data-id="${s.id}">Inspect model & mounts ↗</button></article>`).join('');}
function show(id){const s=catalog.find(x=>x.id===id);if(!s)return;const root=`pegstr/${id}/`;el('remix-detail-content').innerHTML=`<p class="eyebrow">${id} / PEGSTR REMIX</p><h2>${esc(s.name)}</h2><p>${esc(s.description)}</p>${["P01","P09"].includes(s.id)?`<p><a href="arrays.html#${s.id}">Four more array sizes + generator ↗</a></p>`:""}<div class="view-controls"><button data-mode="images">Front & rear renders</button><button data-mode="orbit">Rotate in 3D</button></div><div id="remix-pictures" class="remix-pictures"><figure><img src="${root}front.png" alt="Front of ${esc(s.name)}"><figcaption>Original pocket profile, custom peg mounting.</figcaption></figure><figure><img src="${root}rear.png" alt="Rear contact face and pegs"><figcaption>Broad flush rear contact. Shafts buried in the receiver.</figcaption></figure></div><model-viewer id="remix-viewer" hidden camera-controls camera-orbit="150deg 65deg auto" touch-action="pan-y" interaction-prompt="none" environment-image="neutral" shadow-intensity="0.4" alt="Orbitable ${esc(s.name)}"></model-viewer><p>${esc(s.changes)}</p>${s.back_extension_mm>1?`<p>The rear apron extends ${s.back_extension_mm.toFixed(1)} mm below the original back to accommodate the lower locator.</p>`:''}<dl><dt>Overall size</dt><dd>${s.bounds_mm.map(n=>n.toFixed(1)).join(' × ')} mm (width × depth × height)</dd><dt>Mounting</dt><dd>${s.mount_columns_x_mm.length} column${s.mount_columns_x_mm.length>1?'s':''}, upper retention + lower locator, 25.4 mm vertical pitch</dd><dt>Rear wall</dt><dd>5.4 mm, flush against the board</dd><dt>Model checks</dt><dd>One closed mesh component; one valid solid after STEP round trip</dd><dt>STEP type</dt><dd>Mesh-derived faceted solid; receiver STEP retains analytic peg geometry</dd></dl><div class="downloads"><a href="${root}model.stl" download>Remix STL</a><a href="${root}model.step" download>Remix STEP</a><a href="${root}receiver.step" download>Analytic receiver STEP</a><a href="${root}model.scad" download>Remix recipe</a><a href="${root}receiver.stl" download>Receiver STL</a><a href="${root}original.stl" download>Original STL</a><a href="${root}spec.json">Model record</a></div><p class="note">${esc(s.qualification)} Recipe dependencies: save model.scad, receiver.stl and original.stl in the same folder.</p><p><a href="${s.source_url}">Original Pegstr by mgx</a> · <a href="pegstr/LICENSE.txt">CC Attribution Non-Commercial</a></p>`;
 el('remix-detail-content').querySelector('.view-controls').onclick=e=>{const mode=e.target.dataset.mode;if(!mode)return;el('remix-pictures').hidden=mode==='orbit';const mv=el('remix-viewer');mv.hidden=mode!=='orbit';if(mode==='orbit')mv.src=`${root}model.glb`;};
 if(!el('remix-detail').open)el('remix-detail').showModal();history.replaceState(null,'',`?part=${id}`);}
el('remix-cards').onclick=e=>{const b=e.target.closest('[data-id]');if(b){e.preventDefault();show(b.dataset.id);}};el('fronts').onclick=()=>{side='front';el('fronts').setAttribute('aria-pressed','true');el('backs').setAttribute('aria-pressed','false');cards();};el('backs').onclick=()=>{side='rear';el('fronts').setAttribute('aria-pressed','false');el('backs').setAttribute('aria-pressed','true');cards();};el('remix-filter').onchange=cards;
el('remix-detail').addEventListener('close',()=>history.replaceState(null,'','pegstr.html'));
catalog=[
  {
    "id": "P01",
    "name": "16 small square seats",
    "description": "Sixteen 6.5 \u00d7 6.5 mm nominal openings.",
    "category": "Small tools",
    "source_file": "PegBoard_4by4_6.5x6.5.stl",
    "source_sha256": "8aa2ba2fe3eef83af3ab757dc03ba66c44a38f1da019a0e8deb58578bea0ff93",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 34.981201171875,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      49.657999992370605,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 15.9816025390625,
    "mesh_sha256": "50e4287d7bfa8d1f6b6c2c07bcdcad57145360ec25858adf0494f1b9852ced76",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 10730
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 10834,
      "welded_facets": 10730,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 3.666311849153265e-06
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P02",
    "name": "Four square seats",
    "description": "Four 10 \u00d7 10 mm nominal openings.",
    "category": "Small tools",
    "source_file": "PegBoard_2by2_10x10.stl",
    "source_sha256": "1fae186022975fad0e0156291f742b50bfe6bbde905a8b507b89aa9a2da42c7f",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 31.403600692749023,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      40.55799961090088,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 11.8995654296875,
    "mesh_sha256": "9c1900ff411a451155bd08927ae3db69a0101fc4021eaf87da43871018ba8260",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 8846
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 8884,
      "welded_facets": 8846,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 2.5440723606398195e-06
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P03",
    "name": "Twin rectangular seats",
    "description": "Two 10 \u00d7 20 mm nominal openings.",
    "category": "Small tools",
    "source_file": "PegBoard_2by1_10x20.stl",
    "source_sha256": "4f9c883771d2d2062de9a344be345587cf93e07c5e3a95d39da6a0c21df95345",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": false,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 31.403600692749023,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      40.50800037384033,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 13.8578935546875,
    "mesh_sha256": "e897cbf7779a4111fe47e2cda1d22718397068137e835178f1358d5535545555",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 8836
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 8856,
      "welded_facets": 8836,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 1.9026804327710066e-06
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P04",
    "name": "Windscreen tool cradle",
    "description": "Original curved open-sided tool seat.",
    "category": "Medium tools",
    "source_file": "PegBoard_windscreen_tool.stl",
    "source_sha256": "ddd16b84275290fca36a642d13b1e02c0eb750c1959c1e6023c7962d3060ed5a",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 32.46879959106445,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      49.31099987030029,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 14.3682587890625,
    "mesh_sha256": "7e5de5894bb4a807448cc1d8a5bc0d39e07cde3ada9a45b0b714b8d326b4b753",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 8748
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 8752,
      "welded_facets": 8748,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 4.757666231498795e-07
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P05",
    "name": "MT2 holder",
    "description": "Original named MT2 profile; verify your tool against the model.",
    "category": "Medium tools",
    "source_file": "PegBoard_MT2.stl",
    "source_sha256": "272eb70c86bc994cdd65a745cbab449a62048d8688202cb2f60b18cdbc85cf52",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": false,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 31.403600692749023,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      59.169100761413574,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 21.780345703125,
    "mesh_sha256": "7f67b4da56606e029c16bcf8842c441dcd1fe1884cbac1bbbd50c5afd8b57d0f",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 9072
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 9076,
      "welded_facets": 9072,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 1.6141246669186494e-06
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P06",
    "name": "100 \u00d7 60 bin",
    "description": "Original wide open bin.",
    "category": "Medium parts",
    "source_file": "PegBoard_box_100x60.stl",
    "source_sha256": "cec2e042629261589c6b47924fba332545f9b5dabc438bc28aefa7b8f524ffe3",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": false,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -38.099999999999994,
      38.099999999999994
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 107.60350036621094,
    "receiver_width_mm": 107.60350036621094,
    "back_extension_mm": 0,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      107.60359954833984,
      80.1579999923706,
      38.12499952316284
    ],
    "w": 107.60359954833984,
    "volume_cm3": 69.0481484375,
    "mesh_sha256": "0de1cb769ab1573315e1c512d2a627d3ca4e61221a59bb26da026588b80cfb4c",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 10114
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.09380083190764e-05,
      "raw_facets": 10448,
      "welded_facets": 10118,
      "redundant_facets_removed": 4,
      "volume_change_fraction": 1.8103278752702197e-06
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P07",
    "name": "60 \u00d7 40 bin",
    "description": "Original compact open bin.",
    "category": "Small parts",
    "source_file": "PegBoard_box_60x40.stl",
    "source_sha256": "ff62eb28ff4b6769fdf839a4bd24adbb10a50541e86a12a2f8628d8fffe08afa",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -25.4,
      25.4
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 63.20000076293945,
    "receiver_width_mm": 63.20000076293945,
    "back_extension_mm": 0,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      63.20000076293945,
      57.85800075531006,
      38.12499952316284
    ],
    "w": 63.20000076293945,
    "volume_cm3": 26.73709375,
    "mesh_sha256": "a27a6a3e3bfd408cd0d90c2562b2edfaf8ddfb397ba72966053e4d39d25600a9",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 9302
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.197259582145863e-05,
      "raw_facets": 9640,
      "welded_facets": 9302,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 3.5063771869840647e-06
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P08",
    "name": "Flashlight ring",
    "description": "Original round through-seat.",
    "category": "Medium tools",
    "source_file": "PegBoard_flashlight.stl",
    "source_sha256": "85768f687724c1df6777540ae8bb8b00a540df60a4ec910e616e312dec4cbd09",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 33.978599548339844,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      53.39729976654053,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 20.888837890625,
    "mesh_sha256": "a46b7ee2aef0cec96f4cbadf9e3c5245d6f86f735983d58b96e4517e1ffbc451",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 8608
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 8616,
      "welded_facets": 8608,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 0.0
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P09",
    "name": "24 round seats",
    "description": "Six by four bank of nominal 10 mm openings.",
    "category": "Small tools",
    "source_file": "PegBoard_6by4_10mm.stl",
    "source_sha256": "2224dd8d5163f4ac8e85e77f753d99cbc849eb649d42fbdacd8ebc5bd18d695f",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -25.4,
      25.4
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 83.41000366210938,
    "receiver_width_mm": 83.41000366210938,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      83.41000366210938,
      71.2380018234253,
      37.144999980926514
    ],
    "w": 83.41000366210938,
    "volume_cm3": 76.286890625,
    "mesh_sha256": "9dcac75381062780bea6a5da3a65a749dc45f36d689b9300470607b864a94137",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 11148
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.197259582145863e-05,
      "raw_facets": 11160,
      "welded_facets": 11148,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 1.0240939610305622e-07
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P10",
    "name": "Low rectangular slot",
    "description": "Original 40 \u00d7 10 mm nominal opening; deeper rear wall for the lower peg.",
    "category": "Small tools",
    "source_file": "PegBoard_40x10_small.stl",
    "source_sha256": "5bb0b152c419958d276d7bf449850514390ee10b5bbf969735b8acae9772ccdc",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 56.80339813232422,
    "receiver_width_mm": 56.80339813232422,
    "back_extension_mm": 18.224700565338136,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      56.80339813232422,
      30.157999992370605,
      37.144999980926514
    ],
    "w": 56.80339813232422,
    "volume_cm3": 16.10782421875,
    "mesh_sha256": "a7e52f2c46117ddc740cddbc9312074360ce26966c9860ac4a79975763f150f5",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 8672
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 8692,
      "welded_facets": 8672,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 1.2125322238016802e-07
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  },
  {
    "id": "P11",
    "name": "Caliper slot",
    "description": "Original caliper-shaped through-seat.",
    "category": "Medium tools",
    "source_file": "PegBoard_caliper.stl",
    "source_sha256": "0638219805a99bea0a593852633957e0ded4e893c7f504810b7a11637e583a10",
    "original_author": "Marius Gheorghescu / mgx",
    "original_mesh_closed": true,
    "source_url": "https://www.thingiverse.com/thing:537516",
    "license": "Creative Commons Attribution Non-Commercial (supplied notice; version unspecified)",
    "source_cut_plane_x_mm": -2.4,
    "body_transform": [
      [
        0,
        -1,
        0,
        0
      ],
      [
        -1,
        0,
        0,
        1.75
      ],
      [
        0,
        0,
        -1,
        -1.9834998893737792
      ],
      [
        0,
        0,
        0,
        1
      ]
    ],
    "rear_contact_y_mm": 0.15,
    "receiver_thickness_mm": 5.4,
    "mount_columns_x_mm": [
      -12.7,
      12.7
    ],
    "peg_checks": [
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      },
      {
        "board_side_difference_mm3": 0.0,
        "buried_overlap_mm": 1.25,
        "single_valid_solid": true
      }
    ],
    "model_revision": "r2",
    "source_body_width_mm": 31.403600692749023,
    "receiver_width_mm": 35.56,
    "back_extension_mm": 1.6146999549865733,
    "original_openings_rescaled": false,
    "changes": "Original pins removed; original openings preserved. Two mounting columns in a broad 5.4 mm flush receiving wall. Narrow receiving walls widened to 35.56 mm to leave material around the exact 5.6 mm shaft roots at 25.4 mm spacing.",
    "phase": "Form and function review",
    "status": "Awaiting user review",
    "qualification": "Geometry checks only; tool fit, strength and printing remain unqualified.",
    "bounds_mm": [
      35.560001373291016,
      38.407999992370605,
      37.144999980926514
    ],
    "w": 35.560001373291016,
    "volume_cm3": 15.3073818359375,
    "mesh_sha256": "a2228d563fbf7f792113be6164c2b03ab9916186e439f66793ff2bfcf06108b0",
    "mesh": {
      "closed": true,
      "components": 1,
      "nonmanifold": false,
      "facets": 8600
    },
    "export_cleanup": {
      "grid_mm": 0.0001,
      "max_vertex_displacement_mm": 8.163482347325639e-05,
      "raw_facets": 8604,
      "welded_facets": 8600,
      "redundant_facets_removed": 0,
      "volume_change_fraction": 0.0
    },
    "step_kind": "Faceted solid derived from the supplied STL; receiver.step retains analytic peg geometry.",
    "step_roundtrip_valid": true
  }
]
;cards();show(new URLSearchParams(location.search).get('part'));
