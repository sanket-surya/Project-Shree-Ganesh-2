import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Layers, RotateCcw, Flame, Eye, Sparkles, Compass, ZoomIn } from 'lucide-react';

export default function ThreeEngineTwin({ telemetry, onSelectComponent }) {
  const mountRef = useRef(null);
  const [exploded, setExploded] = useState(false);
  const [xrayMode, setXrayMode] = useState(true);
  const [combustionEnabled, setCombustionEnabled] = useState(true);
  const [selectedPart, setSelectedPart] = useState(null);
  const [autoRotate, setAutoRotate] = useState(false);
  const [cameraPreset, setCameraPreset] = useState('ISO');

  const telemetryRef = useRef(telemetry);
  const explodedRef = useRef(exploded);
  const xrayModeRef = useRef(xrayMode);
  const onSelectComponentRef = useRef(onSelectComponent);
  const autoRotateRef = useRef(autoRotate);
  const combustionEnabledRef = useRef(combustionEnabled);

  useEffect(() => {
    telemetryRef.current = telemetry;
    explodedRef.current = exploded;
    xrayModeRef.current = xrayMode;
    onSelectComponentRef.current = onSelectComponent;
    autoRotateRef.current = autoRotate;
    combustionEnabledRef.current = combustionEnabled;
  }, [telemetry, exploded, xrayMode, onSelectComponent, autoRotate, combustionEnabled]);

  // Animation & Scene References
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const engineGroupRef = useRef(null);
  const crankshaftRef = useRef(null);
  const propHubRef = useRef(null);
  const turboSpoolRef = useRef(null);
  const cylindersRef = useRef([]);
  const pistonsRef = useRef([]);
  const connRodsRef = useRef([]);
  const sparkFlashesRef = useRef([]);
  const exhaustPipesRef = useRef([]);
  const radarRingRef = useRef(null);
  const explodedLerpRef = useRef(0);
  const xrayLerpRef = useRef(1);

  // Temperature to Color Helpers
  const getChtColor = (tempC) => {
    if (tempC < 100) return new THREE.Color(0x00f0ff);
    if (tempC < 120) return new THREE.Color(0x10b981);
    if (tempC < 135) return new THREE.Color(0xf59e0b);
    return new THREE.Color(0xef4444);
  };

  const getEgtGlow = (tempC) => {
    if (tempC < 800) return new THREE.Color(0xd97706);
    if (tempC < 890) return new THREE.Color(0xf97316);
    return new THREE.Color(0xff2200);
  };

  // Spherical camera state
  const sphericalRef = useRef({ radius: 38, theta: 0.75, phi: 1.15, targetRadius: 38, targetTheta: 0.75, targetPhi: 1.15 });

  const setViewPreset = (view) => {
    setCameraPreset(view);
    const s = sphericalRef.current;
    if (view === 'ISO') {
      s.targetRadius = 38; s.targetTheta = 0.75; s.targetPhi = 1.15;
    } else if (view === 'TURBO') {
      s.targetRadius = 24; s.targetTheta = Math.PI * 0.95; s.targetPhi = 0.85;
    } else if (view === 'PISTONS') {
      s.targetRadius = 26; s.targetTheta = 0.1; s.targetPhi = 1.45;
    } else if (view === 'FRONT') {
      s.targetRadius = 25; s.targetTheta = 0.0; s.targetPhi = 1.25;
    }
  };

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    // 1. Scene Setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0x050811);

    // 2. Camera Setup
    const width = currentMount.clientWidth;
    const height = currentMount.clientHeight;
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
    cameraRef.current = camera;

    // 3. WebGL Renderer with High-End PBR tone mapping
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.4;
    rendererRef.current = renderer;
    currentMount.appendChild(renderer.domElement);

    // 4. Studio & Military Tactical Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambientLight);

    // Top Key Light
    const topKey = new THREE.DirectionalLight(0xdff6ff, 2.0);
    topKey.position.set(30, 45, 30);
    topKey.castShadow = true;
    scene.add(topKey);

    // Rim Cyan Backlight (Tactical Military glow)
    const rimCyan = new THREE.DirectionalLight(0x00f0ff, 1.8);
    rimCyan.position.set(-30, 20, -35);
    scene.add(rimCyan);

    // Warm Orange Underlight (Combustion contrast)
    const underWarm = new THREE.PointLight(0xff6600, 1.6, 50);
    underWarm.position.set(0, -12, -8);
    scene.add(underWarm);

    // Central Core Glow
    const coreGlow = new THREE.PointLight(0x00f0ff, 1.8, 30);
    coreGlow.position.set(0, 4, 0);
    scene.add(coreGlow);

    // 5. Defense Engineering Tactical Floor
    const hudFloor = new THREE.Group();
    hudFloor.position.y = -9.5;

    // Primary calm grid
    const gridHelper = new THREE.GridHelper(48, 48, 0x242e42, 0x141a26);
    hudFloor.add(gridHelper);

    // Concentric Range Rings
    [10, 18, 26].forEach((radius) => {
      const ringGeo = new THREE.RingGeometry(radius - 0.08, radius + 0.08, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x242e42, transparent: true, opacity: 0.25, side: THREE.DoubleSide });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2;
      hudFloor.add(ringMesh);
    });

    // Rotating Radar Sweep Ring
    const radarGeo = new THREE.RingGeometry(5.0, 24.0, 48, 1, 0, Math.PI * 0.35);
    const radarMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.10,
      side: THREE.DoubleSide
    });
    const radarSweep = new THREE.Mesh(radarGeo, radarMat);
    radarSweep.rotation.x = Math.PI / 2;
    hudFloor.add(radarSweep);
    radarRingRef.current = radarSweep;

    scene.add(hudFloor);

    // 6. Build High-Fidelity Rotax 914F 3D Engine Assembly
    const engineGroup = new THREE.Group();
    engineGroupRef.current = engineGroup;
    scene.add(engineGroup);

    // --- A. Billet Aircraft Aluminum Crankcase (Split Horizontal Housing) ---
    const caseGroup = new THREE.Group();
    caseGroup.name = "Rotax 914F Crankcase Assembly";

    // Main central case body
    const mainCaseGeo = new THREE.BoxGeometry(7.6, 5.6, 9.8);
    const alumPbrMat = new THREE.MeshStandardMaterial({
      color: 0x243247,
      metalness: 0.92,
      roughness: 0.24,
      transparent: true,
      opacity: 0.88
    });
    const mainCase = new THREE.Mesh(mainCaseGeo, alumPbrMat);
    caseGroup.add(mainCase);

    // CNC Machined Split Flanges & Mounting Lugs
    for (let side of [-1, 1]) {
      const flangeGeo = new THREE.BoxGeometry(0.5, 5.2, 9.4);
      const flangeMat = new THREE.MeshStandardMaterial({ color: 0x3b4d66, metalness: 0.88, roughness: 0.3 });
      const flange = new THREE.Mesh(flangeGeo, flangeMat);
      flange.position.set(side * 3.85, 0, 0);
      caseGroup.add(flange);

      // 4 Heavy-duty Aircraft Mounting Lugs
      for (let zLug of [-3.2, 3.2]) {
        const lugGeo = new THREE.CylinderGeometry(0.7, 0.7, 1.2, 16);
        const lugMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.95 });
        const lug = new THREE.Mesh(lugGeo, lugMat);
        lug.rotation.z = Math.PI / 2;
        lug.position.set(side * 4.4, -1.8, zLug);
        caseGroup.add(lug);
      }
    }

    // Top Access Inspection Plate
    const topCoverGeo = new THREE.BoxGeometry(5.2, 0.4, 7.2);
    const topCoverMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.9, roughness: 0.2 });
    const topCover = new THREE.Mesh(topCoverGeo, topCoverMat);
    topCover.position.set(0, 2.9, 0);
    caseGroup.add(topCover);

    engineGroup.add(caseGroup);

    // --- B. Rotating Crankshaft with Balanced Counterweights ---
    const crankGroup = new THREE.Group();
    crankGroup.name = "Crankshaft & Counterweights";
    const mainShaftGeo = new THREE.CylinderGeometry(0.9, 0.9, 9.2, 24);
    const steelShaftMat = new THREE.MeshStandardMaterial({ color: 0xcfd8dc, metalness: 0.98, roughness: 0.12 });
    const shaftMesh = new THREE.Mesh(mainShaftGeo, steelShaftMat);
    shaftMesh.rotation.x = Math.PI / 2;
    crankGroup.add(shaftMesh);

    // 4 Precision Billet Counterweight Lobes
    for (let c = -3.2; c <= 3.2; c += 2.1) {
      const lobeGeo = new THREE.BoxGeometry(1.8, 2.8, 0.8);
      const lobeMat = new THREE.MeshStandardMaterial({ color: 0x78909c, metalness: 0.92 });
      const lobe = new THREE.Mesh(lobeGeo, lobeMat);
      lobe.position.set(0, 0.9, c);
      crankGroup.add(lobe);
    }
    engineGroup.add(crankGroup);
    crankshaftRef.current = crankGroup;

    // --- C. Lower Lubrication Oil Sump with Cooling Ribs ---
    const sumpGeo = new THREE.BoxGeometry(6.4, 2.4, 8.2);
    const sumpMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      metalness: 0.88,
      roughness: 0.35,
      transparent: true,
      opacity: 0.92
    });
    const sump = new THREE.Mesh(sumpGeo, sumpMat);
    sump.position.set(0, -3.9, 0);
    sump.name = "Rotax Dry-Sump Lubrication Tank";
    engineGroup.add(sump);

    // Sump cooling ribs
    for (let r = -3.0; r <= 3.0; r += 1.2) {
      const ribGeo = new THREE.BoxGeometry(6.6, 0.25, 0.4);
      const ribMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x002b3d, metalness: 0.9 });
      const rib = new THREE.Mesh(ribGeo, ribMat);
      rib.position.set(0, -5.1, r);
      engineGroup.add(rib);
    }

    // --- D. Rotax 914F 2.43:1 Propeller Reduction Gearbox (Front) ---
    const gbGroup = new THREE.Group();
    gbGroup.position.set(0, 0.4, 6.4);
    gbGroup.name = "Rotax 2.43:1 Propeller Reduction Gearbox";

    const gbHousingGeo = new THREE.CylinderGeometry(2.6, 3.1, 3.4, 24);
    const gbHousingMat = new THREE.MeshStandardMaterial({ color: 0x283548, metalness: 0.92, roughness: 0.25 });
    const gbHousing = new THREE.Mesh(gbHousingGeo, gbHousingMat);
    gbHousing.rotation.x = Math.PI / 2;
    gbGroup.add(gbHousing);

    // Front Prop Drive Flange with 6 Aircraft Bolts
    const flangeGeo = new THREE.CylinderGeometry(2.2, 2.2, 0.5, 24);
    const flangeMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x003344, metalness: 0.96 });
    const propFlange = new THREE.Mesh(flangeGeo, flangeMat);
    propFlange.rotation.x = Math.PI / 2;
    propFlange.position.z = 2.0;
    gbGroup.add(propFlange);

    // 6 Hex Bolts on Prop Flange
    for (let b = 0; b < 6; b++) {
      const angle = (b / 6) * Math.PI * 2;
      const boltGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.6, 8);
      const boltMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.98 });
      const bolt = new THREE.Mesh(boltGeo, boltMat);
      bolt.rotation.x = Math.PI / 2;
      bolt.position.set(Math.cos(angle) * 1.5, Math.sin(angle) * 1.5, 2.2);
      gbGroup.add(bolt);
    }

    // High-Torque Spinner Hub
    const propHubGeo = new THREE.ConeGeometry(1.2, 2.2, 20);
    const propHubMat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x004455,
      metalness: 0.95,
      roughness: 0.15
    });
    const propHub = new THREE.Mesh(propHubGeo, propHubMat);
    propHub.rotation.x = Math.PI / 2;
    propHub.position.set(0, 0, 3.1);
    propHubRef.current = propHub;
    gbGroup.add(propHub);

    engineGroup.add(gbGroup);

    // --- E. 4 Boxer Cylinders with Real Concentric Cooling Fins ---
    const cylinders = [];
    const pistons = [];
    const connRods = [];
    const sparkFlashes = [];

    // Realistic Boxer layout: Cyl 1 & 3 on Right, Cyl 2 & 4 on Left
    const cylPositions = [
      { id: 1, x: 5.6, y: 0.6, z: 2.3, dir: 1, phase: 0, name: "Cylinder 1 (Right Front)" },
      { id: 2, x: -5.6, y: 0.6, z: 2.3, dir: -1, phase: Math.PI * 0.5, name: "Cylinder 2 (Left Front)" },
      { id: 3, x: 5.6, y: 0.6, z: -2.3, dir: 1, phase: Math.PI, name: "Cylinder 3 (Right Rear - Critical)" },
      { id: 4, x: -5.6, y: 0.6, z: -2.3, dir: -1, phase: Math.PI * 1.5, name: "Cylinder 4 (Left Rear)" },
    ];

    cylPositions.forEach((pos) => {
      const cylAssembly = new THREE.Group();
      cylAssembly.position.set(pos.x, pos.y, pos.z);
      cylAssembly.userData = { id: pos.id, basePos: { x: pos.x, y: pos.y, z: pos.z }, dir: pos.dir, name: pos.name };

      // Main Cylinder Barrel Sleeve
      const barrelGeo = new THREE.CylinderGeometry(2.0, 2.0, 4.4, 28);
      const barrelMat = new THREE.MeshStandardMaterial({
        color: 0x10b981,
        metalness: 0.72,
        roughness: 0.32,
        emissive: 0x064e3b,
        emissiveIntensity: 0.35,
        transparent: true,
        opacity: 0.45
      });
      const barrel = new THREE.Mesh(barrelGeo, barrelMat);
      barrel.rotation.z = Math.PI / 2;
      barrel.name = `${pos.name} Barrel`;
      cylAssembly.add(barrel);

      // 6 Precision Air-Cooling Fins per Cylinder
      for (let f = -1.6; f <= 1.6; f += 0.6) {
        const finGeo = new THREE.CylinderGeometry(2.45, 2.45, 0.12, 28);
        const finMat = new THREE.MeshStandardMaterial({
          color: 0x38bdf8,
          metalness: 0.9,
          roughness: 0.25,
          transparent: true,
          opacity: 0.5
        });
        const finMesh = new THREE.Mesh(finGeo, finMat);
        finMesh.rotation.z = Math.PI / 2;
        finMesh.position.x = f;
        cylAssembly.add(finMesh);
      }

      // Titanium Cylinder Head Cap with Valve Covers
      const headGeo = new THREE.CylinderGeometry(2.2, 2.2, 1.2, 28);
      const headMat = new THREE.MeshStandardMaterial({
        color: 0x0284c7,
        metalness: 0.88,
        roughness: 0.18,
        transparent: true,
        opacity: 0.92
      });
      const head = new THREE.Mesh(headGeo, headMat);
      head.rotation.z = Math.PI / 2;
      head.position.x = pos.dir * 2.5;
      cylAssembly.add(head);

      // Blue Anodized Rocker Arm Box Cover
      const rockerGeo = new THREE.BoxGeometry(1.4, 2.8, 2.4);
      const rockerMat = new THREE.MeshStandardMaterial({
        color: 0x0077cc,
        metalness: 0.95,
        roughness: 0.15
      });
      const rockerCover = new THREE.Mesh(rockerGeo, rockerMat);
      rockerCover.position.set(pos.dir * 3.3, 0, 0);
      cylAssembly.add(rockerCover);

      // Spark Plug with High-Tension Boot
      const plugGeo = new THREE.CylinderGeometry(0.35, 0.35, 1.6, 12);
      const plugMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, metalness: 0.96 });
      const plug = new THREE.Mesh(plugGeo, plugMat);
      plug.position.set(pos.dir * 2.6, 1.6, 0);
      plug.rotation.z = -pos.dir * 0.45;
      cylAssembly.add(plug);

      // 4-Stroke Combustion Flash (Firing in combustion chamber)
      const fireGeo = new THREE.SphereGeometry(1.1, 16, 16);
      const fireMat = new THREE.MeshBasicMaterial({
        color: 0xffea00,
        transparent: true,
        opacity: 0.0
      });
      const fireMesh = new THREE.Mesh(fireGeo, fireMat);
      fireMesh.position.set(pos.dir * 2.0, 0, 0);
      cylAssembly.add(fireMesh);

      const fireLight = new THREE.PointLight(0xff7700, 0, 14);
      fireLight.position.set(pos.dir * 2.0, 0, 0);
      cylAssembly.add(fireLight);
      sparkFlashes.push({ mesh: fireMesh, light: fireLight, phase: pos.phase });

      // Internal Reciprocating Piston (Crown + Skirt)
      const pistonGeo = new THREE.CylinderGeometry(1.75, 1.75, 2.0, 24);
      const pistonMat = new THREE.MeshStandardMaterial({
        color: 0xf1f5f9,
        metalness: 0.96,
        roughness: 0.12
      });
      const piston = new THREE.Mesh(pistonGeo, pistonMat);
      piston.rotation.z = Math.PI / 2;
      cylAssembly.add(piston);

      // Connecting Rod
      const rodGeo = new THREE.BoxGeometry(2.6, 0.45, 0.35);
      const rodMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.92 });
      const rod = new THREE.Mesh(rodGeo, rodMat);
      rod.position.set(-pos.dir * 1.3, 0, 0);
      cylAssembly.add(rod);

      engineGroup.add(cylAssembly);
      cylinders.push({ group: cylAssembly, barrelMat, headMat, data: pos });
      pistons.push({ mesh: piston, dir: pos.dir, phase: pos.phase });
      connRods.push({ mesh: rod, dir: pos.dir, phase: pos.phase });
    });

    cylindersRef.current = cylinders;
    pistonsRef.current = pistons;
    connRodsRef.current = connRods;
    sparkFlashesRef.current = sparkFlashes;

    // --- F. Dual Electronic Fuel Injector Rails (Top Mounted) ---
    for (let railSide of [-1, 1]) {
      const railGeo = new THREE.CylinderGeometry(0.35, 0.35, 8.4, 16);
      const railMat = new THREE.MeshStandardMaterial({ color: 0xef4444, metalness: 0.95 }); // Anodized Red Fuel Rail
      const fuelRail = new THREE.Mesh(railGeo, railMat);
      fuelRail.rotation.x = Math.PI / 2;
      fuelRail.position.set(railSide * 3.6, 3.2, 0);
      engineGroup.add(fuelRail);

      // Electronic Injector Nozzles into each cylinder
      for (let zInj of [-2.3, 2.3]) {
        const injGeo = new THREE.CylinderGeometry(0.25, 0.25, 1.8, 12);
        const injMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, metalness: 0.95 });
        const injector = new THREE.Mesh(injGeo, injMat);
        injector.position.set(railSide * 4.4, 2.2, zInj);
        injector.rotation.z = -railSide * 0.4;
        engineGroup.add(injector);
      }
    }

    // --- G. Glowing Inconel Exhaust Headers (Dynamic EGT Heat Pipes) ---
    const exhaustPipes = [];
    cylPositions.forEach((pos) => {
      const curve = new THREE.CatmullRomCurve3([
        new THREE.Vector3(pos.x, pos.y - 1.2, pos.z),
        new THREE.Vector3(pos.x * 0.55, pos.y - 2.8, pos.z * 0.75),
        new THREE.Vector3(0, pos.y - 3.4, -4.9)
      ]);
      const pipeGeo = new THREE.TubeGeometry(curve, 28, 0.52, 14, false);
      const pipeMat = new THREE.MeshStandardMaterial({
        color: 0xf97316,
        emissive: 0xd97706,
        emissiveIntensity: 0.85,
        metalness: 0.7,
        roughness: 0.3
      });
      const pipeMesh = new THREE.Mesh(pipeGeo, pipeMat);
      pipeMesh.name = `Exhaust Header Cyl ${pos.id}`;
      engineGroup.add(pipeMesh);
      exhaustPipes.push({ mesh: pipeMesh, mat: pipeMat, id: pos.id });
    });
    exhaustPipesRef.current = exhaustPipes;

    // --- H. Rotax 914F High-Performance Turbocharger Assembly (Rear Top) ---
    const turboGroup = new THREE.Group();
    turboGroup.position.set(0, 3.6, -4.4);
    turboGroup.name = "Rotax 914F Turbocharger System";

    // 1. Hot Turbine Snail Housing (Glowing Ceramic / Cast Iron)
    const turbineGeo = new THREE.TorusGeometry(2.0, 0.85, 18, 28);
    const turbineMat = new THREE.MeshStandardMaterial({
      color: 0xe11d48,
      emissive: 0x9f1239,
      emissiveIntensity: 0.75,
      metalness: 0.85,
      roughness: 0.28
    });
    const turbine = new THREE.Mesh(turbineGeo, turbineMat);
    turbine.rotation.y = Math.PI / 2;
    turboGroup.add(turbine);

    // 2. Cold Compressor Scroll Housing (Polished Billet Aircraft Aluminum)
    const compGeo = new THREE.CylinderGeometry(1.6, 2.2, 2.4, 24);
    const compMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      metalness: 0.94,
      roughness: 0.16
    });
    const comp = new THREE.Mesh(compGeo, compMat);
    comp.position.set(0, 0, 2.2);
    turboGroup.add(comp);

    // 3. High-Speed Titanium Compressor Spool Wheel
    const spoolGeo = new THREE.CylinderGeometry(1.1, 1.1, 0.5, 16);
    const spoolMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, metalness: 0.98 });
    const turboSpool = new THREE.Mesh(spoolGeo, spoolMat);
    turboSpool.position.set(0, 0, 2.2);
    turboSpoolRef.current = turboSpool;
    turboGroup.add(turboSpool);

    // 4. Wastegate Actuator Canister & Linkage Arm
    const wastegateCanGeo = new THREE.CylinderGeometry(0.7, 0.7, 1.6, 16);
    const wastegateMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.9 }); // Brass actuator
    const wastegateCan = new THREE.Mesh(wastegateCanGeo, wastegateMat);
    wastegateCan.position.set(2.2, 1.4, 0.4);
    wastegateCan.rotation.z = Math.PI / 4;
    turboGroup.add(wastegateCan);

    const armGeo = new THREE.CylinderGeometry(0.12, 0.12, 2.8, 8);
    const armMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.98 });
    const arm = new THREE.Mesh(armGeo, armMat);
    arm.position.set(1.4, 0.6, -0.4);
    arm.rotation.z = Math.PI / 3;
    turboGroup.add(arm);

    engineGroup.add(turboGroup);

    // 7. Interactive Orbit Controls & Smooth Damping
    let isDragging = false;
    let prevMousePos = { x: 0, y: 0 };

    const updateCamera = () => {
      const s = sphericalRef.current;
      camera.position.x = s.radius * Math.sin(s.phi) * Math.sin(s.theta);
      camera.position.y = s.radius * Math.cos(s.phi);
      camera.position.z = s.radius * Math.sin(s.phi) * Math.cos(s.theta);
      camera.lookAt(0, 0, 0);
    };
    updateCamera();

    const onMouseDown = (e) => {
      isDragging = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMousePos.x;
      const deltaY = e.clientY - prevMousePos.y;
      prevMousePos = { x: e.clientX, y: e.clientY };

      const s = sphericalRef.current;
      s.targetTheta -= deltaX * 0.008;
      s.targetPhi = Math.max(0.25, Math.min(Math.PI - 0.25, s.targetPhi - deltaY * 0.008));
    };

    const onMouseUp = () => { isDragging = false; };
    const onWheel = (e) => {
      const s = sphericalRef.current;
      s.targetRadius = Math.max(14, Math.min(75, s.targetRadius + e.deltaY * 0.035));
    };

    currentMount.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    currentMount.addEventListener('wheel', onWheel);

    // 8. Raycaster for Interactive Component Inspection
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (e) => {
      const rect = currentMount.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(engineGroup.children, true);

      if (intersects.length > 0) {
        let hit = intersects[0].object;
        let partName = hit.name || hit.parent?.name || "Rotax 914F Core Subsystem";
        setSelectedPart(partName);
        if (onSelectComponentRef.current) onSelectComponentRef.current(partName);
      }
    };
    currentMount.addEventListener('click', onClick);

    // 9. Real-Time Working Animation Loop
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const dt = clock.getDelta();
      const elapsed = clock.getElapsedTime();

      // Smooth Camera Lerp to target preset/zoom
      const s = sphericalRef.current;
      s.radius += (s.targetRadius - s.radius) * dt * 5.0;
      s.theta += (s.targetTheta - s.theta) * dt * 5.0;
      s.phi += (s.targetPhi - s.phi) * dt * 5.0;

      if (autoRotateRef.current && !isDragging) {
        s.targetTheta += dt * 0.22;
      }
      updateCamera();

      // Rotate Tactical Radar Sweep Ring
      if (radarRingRef.current) {
        radarRingRef.current.rotation.z += dt * 1.2;
      }

      // Engine Speed Dynamics from Live Telemetry
      const currentTelem = telemetryRef.current;
      const cascade = currentTelem?.cascade;
      const rpm = currentTelem?.state?.rpm || 0;
      const isSeized = cascade?.engine_seized || (cascade?.stage === 4 && !cascade?.mitigated) || rpm <= 50;
      const omega = (rpm / 60.0) * Math.PI * 2 * 0.16;

      // 0. Dynamic Engine Vibration Trauma Shake
      if (engineGroupRef.current) {
        if (isSeized) {
          engineGroupRef.current.position.set(0, 0, 0);
        } else if (cascade?.active && cascade?.stage >= 2 && !cascade?.mitigated) {
          const shakeAmp = Math.min(0.25, (cascade.stage - 1) * 0.08);
          engineGroupRef.current.position.x = (Math.random() - 0.5) * shakeAmp;
          engineGroupRef.current.position.y = (Math.random() - 0.5) * shakeAmp;
          engineGroupRef.current.position.z = (Math.random() - 0.5) * shakeAmp;
        } else if ((currentTelem?.state?.overall_vibration_g || 1.2) > 2.0) {
          const shakeAmp = Math.min(0.18, ((currentTelem?.state?.overall_vibration_g || 1.2) - 1.8) * 0.06);
          engineGroupRef.current.position.x = (Math.random() - 0.5) * shakeAmp;
          engineGroupRef.current.position.y = (Math.random() - 0.5) * shakeAmp;
          engineGroupRef.current.position.z = (Math.random() - 0.5) * shakeAmp;
        } else {
          engineGroupRef.current.position.set(0, 0, 0);
        }
      }

      // 1. Crankshaft Rotation (Stops completely if seized)
      if (crankshaftRef.current && !isSeized) {
        crankshaftRef.current.rotation.z += (rpm / 60.0) * dt * 2.6;
      }

      // 2. Piston & Connecting Rod Reciprocation
      pistonsRef.current.forEach((p, idx) => {
        if (isSeized) {
          // Freeze pistons at seizure position
          return;
        }
        const strokePos = Math.sin(elapsed * omega + p.phase);
        p.mesh.position.x = p.dir * strokePos * 1.15;

        if (connRodsRef.current[idx]) {
          connRodsRef.current[idx].mesh.position.x = -p.dir * (1.3 - strokePos * 0.42);
          connRodsRef.current[idx].mesh.rotation.z = Math.cos(elapsed * omega + p.phase) * 0.28;
        }

        // 3. 4-Stroke Spark & Combustion Chamber Flash
        if (sparkFlashesRef.current[idx] && combustionEnabledRef.current && !isSeized) {
          const isTdcFiring = strokePos > 0.78;
          const flashIntensity = isTdcFiring ? Math.pow((strokePos - 0.78) / 0.22, 2) : 0;
          sparkFlashesRef.current[idx].mesh.material.opacity = flashIntensity * 0.95;
          sparkFlashesRef.current[idx].light.intensity = flashIntensity * 5.0;
        } else if (sparkFlashesRef.current[idx]) {
          sparkFlashesRef.current[idx].mesh.material.opacity = 0;
          sparkFlashesRef.current[idx].light.intensity = 0;
        }
      });

      // 4. Propeller Drive Hub Spinning
      if (propHubRef.current && !isSeized) {
        propHubRef.current.rotation.z += (rpm / 60.0) * dt * 3.8;
      }

      // 5. High-Speed Turbocharger Spool Spinning
      if (turboSpoolRef.current && !isSeized) {
        const turboRpm = currentTelem?.state?.turbo_rpm || 110000;
        turboSpoolRef.current.rotation.z += (turboRpm / 60.0) * dt * 0.09;
      }

      // 6. Smooth Exploded View Animation
      const targetExploded = explodedRef.current ? 1.0 : 0.0;
      explodedLerpRef.current += (targetExploded - explodedLerpRef.current) * dt * 4.5;
      const el = explodedLerpRef.current;

      cylindersRef.current.forEach((cyl) => {
        const b = cyl.data;
        cyl.group.position.x = b.x + (b.dir * el * 4.8);
        cyl.group.position.z = b.z + (b.z > 0 ? el * 2.2 : -el * 2.2);
      });

      // 7. Smooth X-Ray Transparency Animation
      const targetXray = xrayModeRef.current ? 0.38 : 0.95;
      xrayLerpRef.current += (targetXray - xrayLerpRef.current) * dt * 4.5;
      cylindersRef.current.forEach((cyl) => {
        cyl.barrelMat.opacity = xrayLerpRef.current;
      });

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!currentMount) return;
      const w = currentMount.clientWidth;
      const h = currentMount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      currentMount.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      currentMount.removeEventListener('wheel', onWheel);
      currentMount.removeEventListener('click', onClick);
      if (renderer.domElement && currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Synchronize Live Thermal Telemetry into Three.js Materials
  useEffect(() => {
    if (!telemetry?.state) return;
    const { cht_c, egt_c } = telemetry.state;

    // Update Cylinder Head & Fin Colors
    cylindersRef.current.forEach((cyl, idx) => {
      if (cht_c && cht_c[idx] !== undefined) {
        const temp = cht_c[idx];
        const color = getChtColor(temp);
        cyl.barrelMat.color.copy(color);
        cyl.barrelMat.emissive.copy(color);
        cyl.barrelMat.emissiveIntensity = temp > 125 ? 0.8 : 0.32;
      }
    });

    // Update Exhaust Manifold Glowing Inconel Header Tubes
    exhaustPipesRef.current.forEach((pipe, idx) => {
      if (egt_c && egt_c[idx] !== undefined) {
        const temp = egt_c[idx];
        const glow = getEgtGlow(temp);
        pipe.mat.color.copy(glow);
        pipe.mat.emissive.copy(glow);
        pipe.mat.emissiveIntensity = temp > 850 ? 1.1 : 0.65;
      }
    });
  }, [telemetry]);

  return (
    <div className="relative w-full h-full min-h-[480px] rounded-lg overflow-hidden border border-cyan-500/25 bg-slate-950/90 shadow-2xl">
      {/* 3D WebGL Canvas Mount */}
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Cascade Failure Tactical Warning / Mitigation HUD Strip */}
      {telemetry?.cascade?.active && (
        <div className={`absolute top-14 left-3 right-3 mx-auto max-w-xl z-20 px-3 py-1.5 rounded border backdrop-blur-md text-xs font-mono flex items-center justify-between shadow-xl transition-all ${
          telemetry.cascade.mitigated
            ? 'bg-emerald-950/90 border-emerald-500/80 text-emerald-300 ring-1 ring-emerald-400/50 shadow-[0_0_15px_rgba(16,185,129,0.4)]'
            : telemetry.cascade.engine_seized || telemetry.cascade.stage === 4
            ? 'bg-red-950/95 border-red-600 text-red-200 animate-pulse ring-2 ring-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]'
            : telemetry.cascade.stage >= 2
            ? 'bg-orange-950/90 border-orange-500/70 text-orange-200'
            : 'bg-yellow-950/90 border-yellow-500/70 text-yellow-200'
        }`}>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              telemetry.cascade.mitigated ? 'bg-emerald-400' : 'bg-red-500 animate-ping'
            }`} />
            <span className="font-bold tracking-wider">
              {telemetry.cascade.mitigated
                ? '🛡️ AI AUTONOMOUS MITIGATION ENGAGED: SAFE AT 3,300 RPM'
                : telemetry.cascade.engine_seized || telemetry.cascade.stage === 4
                ? '💀 ENGINE SEIZURE CATASTROPHIC FAILURE (0 RPM) — ASSET LOST'
                : `⚠️ CASCADE THERMAL TRAUMA: STAGE ${telemetry.cascade.stage}/4`}
            </span>
          </div>
          <span className="text-[10px] text-slate-300 hidden sm:inline">
            {telemetry.cascade.mitigated
              ? 'Throttle 50% | AFR Enriched | RTB Loiter'
              : telemetry.cascade.current_stage_info?.severity_level || 'Active'}
          </span>
        </div>
      )}

      {/* Floating Tactical HUD Controls (Top Left) */}
      <div className="absolute top-3 left-3 flex flex-wrap gap-2 z-10">
        <button
          onClick={() => setXrayMode(!xrayMode)}
          className={`tactical-btn ${xrayMode ? 'active' : ''}`}
          title="Toggle X-Ray Cutaway to see Internal Reciprocating Pistons & Crankshaft"
        >
          <Eye size={15} />
          {xrayMode ? 'X-RAY CUTAWAY: ON' : 'SOLID VIEW'}
        </button>

        <button
          onClick={() => setCombustionEnabled(!combustionEnabled)}
          className={`tactical-btn ${combustionEnabled ? 'active' : ''}`}
          title="Toggle 4-Stroke Spark & Combustion Flashes"
        >
          <Flame size={15} className={combustionEnabled ? 'text-amber-300' : ''} />
          {combustionEnabled ? 'COMBUSTION FLAME: ON' : 'COMBUSTION: OFF'}
        </button>

        <button
          onClick={() => setExploded(!exploded)}
          className={`tactical-btn ${exploded ? 'active' : ''}`}
          title="Toggle Exploded Assembly View"
        >
          <Layers size={15} />
          {exploded ? 'ASSEMBLED' : 'EXPLODED VIEW'}
        </button>

        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className={`tactical-btn ${autoRotate ? 'active' : ''}`}
          title="Toggle Orbit Auto-Rotation"
        >
          <RotateCcw size={15} />
          {autoRotate ? 'ORBIT: AUTO' : 'ORBIT: MANUAL'}
        </button>
      </div>

      {/* Camera Inspection Presets (Top Right) */}
      <div className="absolute top-3 right-3 flex items-center gap-1 bg-[#0f131d]/90 border border-[#1e2536] p-1 rounded z-10 font-mono text-[11px]">
        <span className="text-slate-400 font-medium px-1 flex items-center gap-1">
          <Compass size={12} className="text-sky-400" /> VIEW:
        </span>
        {['ISO', 'TURBO', 'PISTONS', 'FRONT'].map((v) => (
          <button
            key={v}
            onClick={() => setViewPreset(v)}
            className={`px-2 py-0.5 rounded transition-all text-[10px] ${
              cameraPreset === v
                ? 'bg-blue-600 text-white font-bold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#182030]'
            }`}
          >
            {v}
          </button>
        ))}
      </div>

      {/* Live Working Dynamics Badge (Bottom Left) */}
      <div className="absolute bottom-3 left-3 bg-[#0f131d]/95 border border-[#1e2536] p-2.5 rounded text-xs font-mono max-w-xs z-10">
        <div className="text-slate-200 font-bold tracking-wider mb-1 flex items-center gap-1.5 text-xs font-['Inter',sans-serif]">
          <span className="truncate">{telemetry?.state?.engine_name?.toUpperCase() || 'ROTAX 914F PROPULSION TWIN'}</span>
        </div>
        <div className="text-[9.5px] font-mono text-emerald-400/90 mb-1 border-b border-[#1a2234] pb-0.5">
          {telemetry?.state?.engine_type || '4-Cylinder Horizontally Opposed Turbo'}
        </div>
        <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[11px] text-slate-300">
          <div>Speed: <span className="text-white font-bold">{telemetry?.state?.rpm?.toFixed(0) || 5000} RPM</span></div>
          <div>Turbo: <span className="text-white font-bold">{telemetry?.state?.engine_profile_id === 'LYCOMING_IO360' ? 'N/A (Nat. Asp.)' : `${((telemetry?.state?.turbo_rpm || 110000)/1000).toFixed(0)}k`}</span></div>
          <div>Avg CHT: <span className="text-emerald-400 font-bold">{telemetry?.state?.cht_c ? (telemetry.state.cht_c.reduce((a,b)=>a+b,0)/4).toFixed(1) : 110}°C</span></div>
          <div>Max EGT: <span className="text-amber-400 font-bold">{telemetry?.state?.egt_c ? Math.max(...telemetry.state.egt_c).toFixed(1) : 815}°C</span></div>
        </div>
        {/* Component PHM Quick Health Pill */}
        {telemetry?.state?.components_health && (
          <div className="mt-2 pt-1.5 border-t border-[#1e2536] flex items-center justify-between text-[10px]">
            <span className="text-slate-400">PARTS HEALTH:</span>
            <span className={`font-bold ${
              telemetry.state.components_health.counts?.critical > 0 ? 'text-red-400 animate-pulse' :
              telemetry.state.components_health.counts?.due_soon > 0 ? 'text-amber-400' :
              'text-emerald-400'
            }`}>
              {telemetry.state.components_health.counts?.critical > 0
                ? `🚨 ${telemetry.state.components_health.counts.critical} PART AOG CRITICAL`
                : `${telemetry.state.components_health.average_component_health}% NOMINAL (${telemetry.state.components_health.counts?.optimal || 7} OK)`}
            </span>
          </div>
        )}
        {selectedPart && (
          <div className="mt-1.5 pt-1 border-t border-[#1e2536] text-sky-300 text-[10px]">
            Inspecting: <span className="text-white font-semibold">{selectedPart}</span>
          </div>
        )}
      </div>

      {/* Temperature Gradient Legend (Bottom Right) */}
      <div className="absolute bottom-3 right-3 bg-[#0f131d]/90 border border-[#1e2536] p-2 rounded text-[10px] font-mono z-10 text-slate-300">
        <div className="text-slate-400 font-semibold mb-1">THERMAL RANGES</div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded bg-sky-400 inline-block"></span>
          <span>&lt;100°C (Cold)</span>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="w-2 h-2 rounded bg-emerald-500 inline-block"></span>
          <span>100-120°C (Nominal)</span>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="w-2 h-2 rounded bg-amber-500 inline-block"></span>
          <span>120-135°C (Warm)</span>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="w-2 h-2 rounded bg-red-500 inline-block"></span>
          <span>&gt;135°C (Critical)</span>
        </div>
      </div>
    </div>
  );
}
