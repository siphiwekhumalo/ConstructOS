import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";
import { useTheme } from "next-themes";

function ParticleField() {
  const ref = useRef<THREE.Points>(null);
  const { resolvedTheme } = useTheme();
  
  const particleCount = 3000;
  
  const positions = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return positions;
  }, []);

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta * 0.02;
      ref.current.rotation.y -= delta * 0.03;
    }
  });

  const particleColor = resolvedTheme === "light" ? "#1e293b" : "#f97316";

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color={particleColor}
        size={0.02}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.6}
      />
    </Points>
  );
}

function GridPlane() {
  const { resolvedTheme } = useTheme();
  const gridColor = resolvedTheme === "light" ? "#cbd5e1" : "#334155";
  
  return (
    <gridHelper 
      args={[30, 30, gridColor, gridColor]} 
      position={[0, -3, 0]}
      rotation={[0, 0, 0]}
    />
  );
}

function FloatingCubes() {
  const cubesRef = useRef<THREE.Group>(null);
  const { resolvedTheme } = useTheme();
  
  const cubeColor = resolvedTheme === "light" ? "#f97316" : "#f97316";
  
  useFrame((state) => {
    if (cubesRef.current) {
      cubesRef.current.children.forEach((cube, i) => {
        cube.position.y = Math.sin(state.clock.elapsedTime * 0.5 + i) * 0.3 + cube.userData.baseY;
        cube.rotation.x = state.clock.elapsedTime * 0.2 + i;
        cube.rotation.y = state.clock.elapsedTime * 0.3 + i;
      });
    }
  });

  const cubePositions = useMemo(() => [
    { x: -4, y: 1, z: -3 },
    { x: 3, y: 2, z: -4 },
    { x: -2, y: -1, z: -2 },
    { x: 4, y: 0, z: -5 },
    { x: 0, y: 2.5, z: -6 },
  ], []);

  return (
    <group ref={cubesRef}>
      {cubePositions.map((pos, i) => (
        <mesh 
          key={i} 
          position={[pos.x, pos.y, pos.z]}
          userData={{ baseY: pos.y }}
        >
          <boxGeometry args={[0.4, 0.4, 0.4]} />
          <meshStandardMaterial 
            color={cubeColor} 
            transparent 
            opacity={0.3}
            wireframe
          />
        </mesh>
      ))}
    </group>
  );
}

export function ThreeBackground() {
  const { resolvedTheme } = useTheme();
  
  return (
    <div className="fixed inset-0 -z-10 pointer-events-none">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        style={{ background: "transparent" }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={0.8} />
        <ParticleField />
        <GridPlane />
        <FloatingCubes />
      </Canvas>
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: resolvedTheme === "light" 
            ? "radial-gradient(ellipse at center, transparent 0%, rgba(248, 250, 252, 0.9) 70%)"
            : "radial-gradient(ellipse at center, transparent 0%, rgba(15, 23, 42, 0.9) 70%)"
        }}
      />
    </div>
  );
}

export function ThreeHeroBackground() {
  return (
    <div className="absolute inset-0 -z-10">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 75 }}
        style={{ background: "transparent" }}
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#f97316" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#3b82f6" />
        <ParticleField />
      </Canvas>
    </div>
  );
}
