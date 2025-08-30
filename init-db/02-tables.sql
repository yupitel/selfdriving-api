-- =====================================================
-- Table Creation Script for Self-Driving Data Collection
-- =====================================================
-- This script creates all necessary tables in the selfdriving schema
-- Based on SQLModel definitions from the application

-- Use the selfdriving schema
SET search_path TO selfdriving;

-- =====================================================
-- 1. VEHICLE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS vehicle (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    country TEXT,
    name TEXT NOT NULL,
    data_path TEXT,
    type SMALLINT NOT NULL,
    status SMALLINT NOT NULL
);

-- Create indexes for vehicle table
CREATE INDEX IF NOT EXISTS idx_vehicle_country ON vehicle(country);
CREATE INDEX IF NOT EXISTS idx_vehicle_name ON vehicle(name);
CREATE INDEX IF NOT EXISTS idx_vehicle_type ON vehicle(type);
CREATE INDEX IF NOT EXISTS idx_vehicle_status ON vehicle(status);
CREATE INDEX IF NOT EXISTS idx_vehicle_created_at ON vehicle(created_at DESC);

-- Add comments
COMMENT ON TABLE vehicle IS 'Vehicle information for self-driving data collection';
COMMENT ON COLUMN vehicle.id IS 'Unique identifier for the vehicle';
COMMENT ON COLUMN vehicle.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN vehicle.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN vehicle.country IS 'Country where the vehicle operates';
COMMENT ON COLUMN vehicle.name IS 'Name of the vehicle';
COMMENT ON COLUMN vehicle.data_path IS 'Path to vehicle-related data';
COMMENT ON COLUMN vehicle.type IS 'Vehicle type (0=SEDAN, 1=SUV, 2=TRUCK, 3=VAN, 4=BUS, 5=COMPACT, 6=MINIVAN, 99=EXPERIMENTAL)';
COMMENT ON COLUMN vehicle.status IS 'Vehicle status (0=INACTIVE, 1=ACTIVE, 2=MAINTENANCE, 3=TESTING, 4=OFFLINE)';

-- =====================================================
-- 2. MEASUREMENT TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS measurement (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    vehicle_id UUID NOT NULL,
    area_id UUID NOT NULL,
    local_time TIMESTAMP NOT NULL,
    measured_at BIGINT NOT NULL,
    name TEXT,
    data_path TEXT
);

-- Create indexes for measurement table
CREATE INDEX IF NOT EXISTS idx_measurement_vehicle_id ON measurement(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_measurement_area_id ON measurement(area_id);
CREATE INDEX IF NOT EXISTS idx_measurement_local_time ON measurement(local_time);
CREATE INDEX IF NOT EXISTS idx_measurement_measured_at ON measurement(measured_at);
CREATE INDEX IF NOT EXISTS idx_measurement_created_at ON measurement(created_at DESC);

-- Add comments
COMMENT ON TABLE measurement IS 'Measurement data from vehicles';
COMMENT ON COLUMN measurement.id IS 'Unique identifier for the measurement';
COMMENT ON COLUMN measurement.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN measurement.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN measurement.vehicle_id IS 'Reference to the vehicle that made the measurement';
COMMENT ON COLUMN measurement.area_id IS 'Reference to the area where measurement was taken';
COMMENT ON COLUMN measurement.local_time IS 'Local time when the measurement was taken';
COMMENT ON COLUMN measurement.measured_at IS 'Unix timestamp of the measurement';
COMMENT ON COLUMN measurement.name IS 'Name or description of the measurement';
COMMENT ON COLUMN measurement.data_path IS 'Path to measurement data files';

-- =====================================================
-- 3. DATASTREAM TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS datastream (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    type SMALLINT NOT NULL,
    measurement_id UUID NOT NULL,
    name TEXT,
    data_path TEXT,
    src_path TEXT,
    CONSTRAINT fk_datastream_measurement 
        FOREIGN KEY (measurement_id) 
        REFERENCES measurement(id) 
        ON DELETE CASCADE
);

-- Create indexes for datastream table
CREATE INDEX IF NOT EXISTS idx_datastream_type ON datastream(type);
CREATE INDEX IF NOT EXISTS idx_datastream_measurement_id ON datastream(measurement_id);
CREATE INDEX IF NOT EXISTS idx_datastream_name ON datastream(name);
CREATE INDEX IF NOT EXISTS idx_datastream_created_at ON datastream(created_at DESC);

-- Add comments
COMMENT ON TABLE datastream IS 'Data streams associated with measurements';
COMMENT ON COLUMN datastream.id IS 'Unique identifier for the datastream';
COMMENT ON COLUMN datastream.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN datastream.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN datastream.type IS 'Type of datastream (0=CAMERA, 1=LIDAR, 2=RADAR, 3=IMU, 4=GPS, 5=CAN, 6=ULTRASONIC, 7=THERMAL, 8=MICROPHONE, 99=OTHER)';
COMMENT ON COLUMN datastream.measurement_id IS 'Reference to the associated measurement';
COMMENT ON COLUMN datastream.name IS 'Name or description of the datastream';
COMMENT ON COLUMN datastream.data_path IS 'Path to the processed data file';
COMMENT ON COLUMN datastream.src_path IS 'Path to the source/raw data file';

-- =====================================================
-- 4. PIPELINE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS pipeline (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    name TEXT NOT NULL,
    type SMALLINT NOT NULL,
    "group" SMALLINT NOT NULL,  -- group is a reserved word, so we quote it
    is_available SMALLINT NOT NULL CHECK (is_available IN (0, 1)),
    version SMALLINT NOT NULL,
    options TEXT,  -- JSON string
    params TEXT NOT NULL  -- JSON string
);

-- Create indexes for pipeline table
CREATE INDEX IF NOT EXISTS idx_pipeline_name ON pipeline(name);
CREATE INDEX IF NOT EXISTS idx_pipeline_type ON pipeline(type);
CREATE INDEX IF NOT EXISTS idx_pipeline_group ON pipeline("group");
CREATE INDEX IF NOT EXISTS idx_pipeline_is_available ON pipeline(is_available);
CREATE INDEX IF NOT EXISTS idx_pipeline_version ON pipeline(version);
CREATE INDEX IF NOT EXISTS idx_pipeline_created_at ON pipeline(created_at DESC);

-- Add comments
COMMENT ON TABLE pipeline IS 'Pipeline configurations for data processing';
COMMENT ON COLUMN pipeline.id IS 'Unique identifier for the pipeline';
COMMENT ON COLUMN pipeline.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN pipeline.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN pipeline.name IS 'Name of the pipeline';
COMMENT ON COLUMN pipeline.type IS 'Type of pipeline (0=DATA_COLLECTION, 1=DATA_PROCESSING, 2=DATA_VALIDATION, 3=ML_TRAINING, 4=ML_INFERENCE, 5=DATA_EXPORT, 6=DATA_IMPORT, 7=QUALITY_CHECK, 8=ANNOTATION, 99=OTHER)';
COMMENT ON COLUMN pipeline."group" IS 'Pipeline group for categorization';
COMMENT ON COLUMN pipeline.is_available IS 'Availability status (0=unavailable, 1=available)';
COMMENT ON COLUMN pipeline.version IS 'Version of the pipeline';
COMMENT ON COLUMN pipeline.options IS 'Optional pipeline configuration as JSON string';
COMMENT ON COLUMN pipeline.params IS 'Required pipeline parameters as JSON string';


-- =====================================================
-- End of Table Creation Script
-- =====================================================