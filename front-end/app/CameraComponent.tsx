// Example: CameraComponent.tsx
import React, { useRef, useEffect } from 'react';

const CameraComponent = () => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    async function enableCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        alert('Camera access denied or not available.');
      }
    }
    enableCamera();
  }, []);

  return (
    <div>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          display: "block",
        }}
      />
    </div>
  );
};

export default CameraComponent;