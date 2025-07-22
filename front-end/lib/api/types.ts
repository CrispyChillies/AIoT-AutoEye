// What a user looks like
export type User = {
  _id: string;
  personal: {
    name: string;
    email: string;
  };
}

// What traffic data looks like
export type TrafficData = {
  _id: string;
  location: string;
  vehicle_count: number;
  status: string;
  timestamp: string;
  // Add the missing fields from your JSON response
  car_count?: number;
  motorbike_count?: number;
  lane1_in?: number;
  lane1_out?: number;
  lane2_in?: number;
  lane2_out?: number;
  image?: string | null;
};

// What the health check returns
export type HealthResponse = {
  status: string;
  database: string;
};