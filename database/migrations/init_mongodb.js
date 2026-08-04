// database/migrations/init_mongodb.js
// This script runs when the MongoDB container initializes.
// It creates the database and collections, and sets up indexes.

db = db.getSiblingDB('twinflow');

// Create collections (optional, they will be created on first insert anyway)
db.createCollection('users');
db.createCollection('vehicles');
db.createCollection('signals');
db.createCollection('roads');
db.createCollection('predictions');
db.createCollection('negotiation_messages');
db.createCollection('recommendations');
db.createCollection('incidents');
db.createCollection('simulation_results');
db.createCollection('carbon_reports');

// Indexes for users
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });

// Indexes for vehicles
db.vehicles.createIndex({ "timestamp": -1 });
db.vehicles.createIndex({ "junction_id": 1 });
db.vehicles.createIndex({ "type": 1 });

// Indexes for signals
db.signals.createIndex({ "junction_id": 1 }, { unique: true });

// Indexes for roads
db.roads.createIndex({ "start_junction_id": 1, "end_junction_id": 1 });

// Indexes for predictions
db.predictions.createIndex({ "junction_id": 1, "timestamp": -1 });
db.predictions.createIndex({ "horizon_minutes": 1 });

// Indexes for negotiation messages
db.negotiation_messages.createIndex({ "junction_id": 1, "timestamp": -1 });

// Indexes for recommendations (master)
db.recommendations.createIndex({ "junction_id": 1, "timestamp": -1 });

// Indexes for incidents
db.incidents.createIndex({ "resolved": 1 });
db.incidents.createIndex({ "severity": 1 });
db.incidents.createIndex({ "start_time": -1 });

// Indexes for simulation results
db.simulation_results.createIndex({ "junction_id": 1, "time_horizon": 1 });
db.simulation_results.createIndex({ "simulation_id": 1 });

// Indexes for carbon reports
db.carbon_reports.createIndex({ "junction_id": 1, "date": -1 });