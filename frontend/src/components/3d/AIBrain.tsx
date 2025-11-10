'use client';

import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere } from '@react-three/drei';
import * as THREE from 'three';

function BrainMesh() {
  const meshRef = useRef<THREE.Mesh>(null);
  const wireframeRef = useRef<THREE.LineSegments>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
    }
    if (wireframeRef.current) {
      wireframeRef.current.rotation.y += 0.002;
    }
  });

  return (
    <group>
      {/* Main Brain Sphere */}
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2, 4]} />
        <meshStandardMaterial
          color="#8B5CF6"
          emissive="#8B5CF6"
          emissiveIntensity={0.2}
          wireframe={false}
          transparent
          opacity={0.3}
        />
      </mesh>

      {/* Wireframe Overlay */}
      <lineSegments ref={wireframeRef}>
        <icosahedronGeometry args={[2.1, 2]} />
        <lineBasicMaterial color="#8B5CF6" transparent opacity={0.6} />
      </lineSegments>

      {/* Inner Glow */}
      <Sphere args={[1.8, 32, 32]}>
        <meshBasicMaterial
          color="#2E9BFF"
          transparent
          opacity={0.1}
        />
      </Sphere>

      {/* Particles */}
      {[...Array(50)].map((_, i) => {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(Math.random() * 2 - 1);
        const x = 3 * Math.sin(phi) * Math.cos(theta);
        const y = 3 * Math.sin(phi) * Math.sin(theta);
        const z = 3 * Math.cos(phi);

        return (
          <mesh key={i} position={[x, y, z]}>
            <sphereGeometry args={[0.02, 8, 8]} />
            <meshBasicMaterial color="#8B5CF6" />
          </mesh>
        );
      })}
    </group>
  );
}

export function AIBrain() {
  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [0, 0, 6], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#2E9BFF" />
        <BrainMesh />
        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
      </Canvas>
    </div>
  );
}

