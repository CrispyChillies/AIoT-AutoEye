import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { RefreshCw, Camera, AlertCircle } from "lucide-react";
import { TrafficData } from "@/lib/api/types";

interface CameraComponentProps {
  latestTraffic?: TrafficData | null;
  onRefresh?: () => void;
}

const CameraComponent: React.FC<CameraComponentProps> = ({ latestTraffic, onRefresh }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  console.log(latestTraffic)

  // Reset error when new traffic data comes in
  useEffect(() => {
    if (latestTraffic?.image) {
      setImageError(false);
    }
  }, [latestTraffic?.image]);

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  const handleImageLoad = () => {
    setImageLoading(false);
    setImageError(false);
  };

  const handleRefresh = () => {
    setImageLoading(true);
    setImageError(false);
    if (onRefresh) {
      onRefresh();
    }
  };

  // No traffic data available
  if (!latestTraffic) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-800 text-white">
        <div className="text-center">
          <Camera className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-lg mb-2">No Camera Data</p>
          <p className="text-sm text-gray-400">No traffic records available</p>
          <Button onClick={handleRefresh} variant="outline" size="sm" className="mt-4">
            <RefreshCw className="w-4 h-4 mr-2" />
            Load Data
          </Button>
        </div>
      </div>
    );
  }

  // Traffic data exists but no image
  if (!latestTraffic.image) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-800 text-white">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-yellow-400" />
          <p className="text-lg mb-2">No Image Available</p>
          <p className="text-sm text-gray-400">Latest record from {latestTraffic.location}</p>
          <p className="text-xs text-gray-500 mb-4">
            {new Date(latestTraffic.timestamp).toLocaleString()}
          </p>
          <Button onClick={handleRefresh} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
    );
  }

  // Display the image
  return (
    <div className="relative w-full h-full">
      {imageLoading && (
        <div className="absolute inset-0 bg-gray-800 flex items-center justify-center z-10">
          <RefreshCw className="w-8 h-8 animate-spin text-white" />
        </div>
      )}
      
      {imageError ? (
        <div className="w-full h-full flex items-center justify-center bg-gray-800 text-white">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
            <p className="text-lg mb-2">Image Load Error</p>
            <p className="text-sm text-gray-400 mb-4">Failed to load image from database</p>
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </div>
      ) : (
        <img
          src={`data:image/jpeg;base64,${latestTraffic.image}`}
          alt={`Traffic view from ${latestTraffic.location}`}
          className="w-full h-full object-cover"
          onError={handleImageError}
          onLoad={handleImageLoad}
          onLoadStart={() => setImageLoading(true)}
        />
      )}
      
      {/* Refresh button overlay */}
      <div className="absolute bottom-4 right-4">
        <Button 
          onClick={handleRefresh} 
          size="sm" 
          variant="secondary"
          className="bg-black/70 hover:bg-black/90 text-white border-0"
        >
          <RefreshCw className="w-4 h-4 mr-1" />
          Refresh
        </Button>
      </div>
    </div>
  );
};

export default CameraComponent; 