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
    driver_id UUID,
    local_time TIMESTAMP NOT NULL,
    measured_at BIGINT NOT NULL,
    name TEXT,
    data_path TEXT,
    distance DECIMAL(10,2),  -- Total distance in kilometers
    duration BIGINT,  -- Total duration in seconds
    start_location TEXT,  -- JSON format: {"lat": 35.6762, "lng": 139.6503}
    end_location TEXT,  -- JSON format: {"lat": 35.6762, "lng": 139.6503}
    weather_condition TEXT,
    road_condition TEXT
);

-- Create indexes for measurement table
CREATE INDEX IF NOT EXISTS idx_measurement_vehicle_id ON measurement(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_measurement_area_id ON measurement(area_id);
CREATE INDEX IF NOT EXISTS idx_measurement_driver_id ON measurement(driver_id);
CREATE INDEX IF NOT EXISTS idx_measurement_local_time ON measurement(local_time);
CREATE INDEX IF NOT EXISTS idx_measurement_measured_at ON measurement(measured_at);
CREATE INDEX IF NOT EXISTS idx_measurement_created_at ON measurement(created_at DESC);

-- Add comments
COMMENT ON TABLE measurement IS 'Measurement data from vehicles - represents a complete driving session';
COMMENT ON COLUMN measurement.id IS 'Unique identifier for the measurement';
COMMENT ON COLUMN measurement.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN measurement.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN measurement.vehicle_id IS 'Reference to the vehicle that made the measurement';
COMMENT ON COLUMN measurement.area_id IS 'Reference to the area where measurement was taken';
COMMENT ON COLUMN measurement.driver_id IS 'Reference to the driver who conducted the measurement';
COMMENT ON COLUMN measurement.local_time IS 'Local time when the measurement was taken';
COMMENT ON COLUMN measurement.measured_at IS 'Unix timestamp of the measurement';
COMMENT ON COLUMN measurement.name IS 'Name or description of the measurement';
COMMENT ON COLUMN measurement.data_path IS 'Path to measurement data files';
COMMENT ON COLUMN measurement.distance IS 'Total distance driven in kilometers';
COMMENT ON COLUMN measurement.duration IS 'Total duration of the drive in seconds';
COMMENT ON COLUMN measurement.start_location IS 'Starting location as JSON (lat/lng)';
COMMENT ON COLUMN measurement.end_location IS 'Ending location as JSON (lat/lng)';
COMMENT ON COLUMN measurement.weather_condition IS 'Weather conditions during the drive';
COMMENT ON COLUMN measurement.road_condition IS 'Road conditions during the drive';

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
    sequence_number INTEGER,  -- 1, 2, 3... for ordering within measurement
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration BIGINT,  -- Duration in milliseconds
    video_url TEXT,  -- URL to video file for this segment
    has_data_loss BOOLEAN DEFAULT FALSE,
    data_loss_duration BIGINT,  -- Data loss duration in milliseconds
    processing_status SMALLINT DEFAULT 0,  -- 0=PENDING, 1=PROCESSING, 2=COMPLETED, 3=FAILED
    CONSTRAINT fk_datastream_measurement 
        FOREIGN KEY (measurement_id) 
        REFERENCES measurement(id) 
        ON DELETE CASCADE
);

-- Create indexes for datastream table
CREATE INDEX IF NOT EXISTS idx_datastream_type ON datastream(type);
CREATE INDEX IF NOT EXISTS idx_datastream_measurement_id ON datastream(measurement_id);
CREATE INDEX IF NOT EXISTS idx_datastream_measurement_sequence ON datastream(measurement_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_datastream_name ON datastream(name);
CREATE INDEX IF NOT EXISTS idx_datastream_processing_status ON datastream(processing_status);
CREATE INDEX IF NOT EXISTS idx_datastream_created_at ON datastream(created_at DESC);

-- Add comments
COMMENT ON TABLE datastream IS 'Data streams representing 30-minute segments of driving data';
COMMENT ON COLUMN datastream.id IS 'Unique identifier for the datastream';
COMMENT ON COLUMN datastream.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN datastream.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN datastream.type IS 'Type of datastream (0=CAMERA, 1=LIDAR, 2=RADAR, 3=IMU, 4=GPS, 5=CAN, 6=ULTRASONIC, 7=THERMAL, 8=MICROPHONE, 99=OTHER)';
COMMENT ON COLUMN datastream.measurement_id IS 'Reference to the associated measurement';
COMMENT ON COLUMN datastream.name IS 'Name or description of the datastream';
COMMENT ON COLUMN datastream.data_path IS 'Path to the processed data file';
COMMENT ON COLUMN datastream.src_path IS 'Path to the source/raw data file';
COMMENT ON COLUMN datastream.sequence_number IS 'Sequence number within measurement (1, 2, 3...)';
COMMENT ON COLUMN datastream.start_time IS 'Start time of this data segment';
COMMENT ON COLUMN datastream.end_time IS 'End time of this data segment';
COMMENT ON COLUMN datastream.duration IS 'Duration of this segment in milliseconds';
COMMENT ON COLUMN datastream.video_url IS 'URL to the video file for this segment';
COMMENT ON COLUMN datastream.has_data_loss IS 'Whether data loss occurred in this segment';
COMMENT ON COLUMN datastream.data_loss_duration IS 'Duration of data loss in milliseconds';
COMMENT ON COLUMN datastream.processing_status IS 'Processing status (0=PENDING, 1=PROCESSING, 2=COMPLETED, 3=FAILED)';

-- =====================================================
-- 4. SCENE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS scene (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    name TEXT,
    type SMALLINT NOT NULL,
    state SMALLINT NOT NULL,
    datastream_id UUID,
    start_idx INTEGER NOT NULL,
    end_idx INTEGER NOT NULL,
    data_path TEXT,
    CONSTRAINT fk_scene_datastream
        FOREIGN KEY (datastream_id)
        REFERENCES datastream(id)
        ON DELETE SET NULL
);

-- Create indexes for scene table
CREATE INDEX IF NOT EXISTS idx_scene_type ON scene(type);
CREATE INDEX IF NOT EXISTS idx_scene_state ON scene(state);
CREATE INDEX IF NOT EXISTS idx_scene_datastream_id ON scene(datastream_id);
CREATE INDEX IF NOT EXISTS idx_scene_created_at ON scene(created_at DESC);

-- Add comments
COMMENT ON TABLE scene IS 'Scene segments or events detected within datastreams';
COMMENT ON COLUMN scene.id IS 'Unique identifier for the scene';
COMMENT ON COLUMN scene.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN scene.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN scene.name IS 'Name or description of the scene (e.g., crosswalk)';
COMMENT ON COLUMN scene.type IS 'Scene type (application-defined, 0-32767)';
COMMENT ON COLUMN scene.state IS 'Scene state (application-defined, 0-32767)';
COMMENT ON COLUMN scene.datastream_id IS 'Reference to the associated datastream';
COMMENT ON COLUMN scene.start_idx IS 'Inclusive start index within the datastream';
COMMENT ON COLUMN scene.end_idx IS 'Inclusive end index within the datastream';
COMMENT ON COLUMN scene.data_path IS 'Optional path to artifacts for this scene';

-- =====================================================
-- 4. DRIVER TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS driver (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    
    -- Driver identification
    driver_code TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    name TEXT NOT NULL,
    name_kana TEXT,
    
    -- License information
    license_number TEXT,
    license_type TEXT,
    license_expiry_date DATE,
    
    -- Certification information
    certification_level SMALLINT DEFAULT 0,  -- 0=TRAINEE, 1=BASIC, 2=ADVANCED, 3=EXPERT
    certification_date DATE,
    training_completed_date DATE,
    
    -- Status
    status SMALLINT NOT NULL DEFAULT 1,  -- 0=INACTIVE, 1=ACTIVE, 2=ON_LEAVE, 3=RETIRED
    employment_type SMALLINT DEFAULT 1,  -- 0=FULL_TIME, 1=CONTRACT, 2=PART_TIME, 3=EXTERNAL
    
    -- Organization
    department TEXT,
    team TEXT,
    supervisor_id UUID,
    
    -- Statistics
    total_drives INTEGER DEFAULT 0,
    total_distance DECIMAL(10,2) DEFAULT 0,
    total_duration BIGINT DEFAULT 0,
    last_drive_date DATE,
    
    -- Scores
    safety_score DECIMAL(3,2),
    efficiency_score DECIMAL(3,2),
    data_quality_score DECIMAL(3,2),
    
    -- Contact information
    phone_number TEXT,
    emergency_contact TEXT,
    
    -- Metadata
    notes TEXT,
    metadata TEXT,  -- JSON string
    
    CONSTRAINT fk_driver_supervisor 
        FOREIGN KEY (supervisor_id) 
        REFERENCES driver(id) 
        ON DELETE SET NULL
);

-- Create indexes for driver table
CREATE INDEX IF NOT EXISTS idx_driver_driver_code ON driver(driver_code);
CREATE INDEX IF NOT EXISTS idx_driver_email ON driver(email);
CREATE INDEX IF NOT EXISTS idx_driver_name ON driver(name);
CREATE INDEX IF NOT EXISTS idx_driver_status ON driver(status);
CREATE INDEX IF NOT EXISTS idx_driver_certification_level ON driver(certification_level);
CREATE INDEX IF NOT EXISTS idx_driver_department ON driver(department);
CREATE INDEX IF NOT EXISTS idx_driver_team ON driver(team);
CREATE INDEX IF NOT EXISTS idx_driver_supervisor_id ON driver(supervisor_id);
CREATE INDEX IF NOT EXISTS idx_driver_last_drive_date ON driver(last_drive_date DESC);
CREATE INDEX IF NOT EXISTS idx_driver_created_at ON driver(created_at DESC);

-- Add comments
COMMENT ON TABLE driver IS 'Driver information for self-driving vehicle operators';
COMMENT ON COLUMN driver.id IS 'Unique identifier for the driver';
COMMENT ON COLUMN driver.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN driver.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN driver.driver_code IS 'Unique driver code or employee number';
COMMENT ON COLUMN driver.email IS 'Driver email address';
COMMENT ON COLUMN driver.name IS 'Full name of the driver';
COMMENT ON COLUMN driver.name_kana IS 'Name in Katakana (for Japanese names)';
COMMENT ON COLUMN driver.license_number IS 'Driving license number';
COMMENT ON COLUMN driver.license_type IS 'Type of driving license';
COMMENT ON COLUMN driver.license_expiry_date IS 'License expiration date';
COMMENT ON COLUMN driver.certification_level IS 'Certification level (0=TRAINEE, 1=BASIC, 2=ADVANCED, 3=EXPERT)';
COMMENT ON COLUMN driver.certification_date IS 'Date when certification was obtained';
COMMENT ON COLUMN driver.training_completed_date IS 'Date when training was completed';
COMMENT ON COLUMN driver.status IS 'Driver status (0=INACTIVE, 1=ACTIVE, 2=ON_LEAVE, 3=RETIRED)';
COMMENT ON COLUMN driver.employment_type IS 'Employment type (0=FULL_TIME, 1=CONTRACT, 2=PART_TIME, 3=EXTERNAL)';
COMMENT ON COLUMN driver.department IS 'Department the driver belongs to';
COMMENT ON COLUMN driver.team IS 'Team the driver belongs to';
COMMENT ON COLUMN driver.supervisor_id IS 'Reference to supervisor (self-referencing)';
COMMENT ON COLUMN driver.total_drives IS 'Total number of driving sessions';
COMMENT ON COLUMN driver.total_distance IS 'Total distance driven in kilometers';
COMMENT ON COLUMN driver.total_duration IS 'Total driving time in seconds';
COMMENT ON COLUMN driver.last_drive_date IS 'Date of last driving session';
COMMENT ON COLUMN driver.safety_score IS 'Safety performance score (0.00-1.00)';
COMMENT ON COLUMN driver.efficiency_score IS 'Efficiency score (0.00-1.00)';
COMMENT ON COLUMN driver.data_quality_score IS 'Data collection quality score (0.00-1.00)';
COMMENT ON COLUMN driver.phone_number IS 'Contact phone number';
COMMENT ON COLUMN driver.emergency_contact IS 'Emergency contact information';
COMMENT ON COLUMN driver.notes IS 'Additional notes about the driver';
COMMENT ON COLUMN driver.metadata IS 'Additional metadata as JSON string';

-- Add foreign key constraint to measurement table
ALTER TABLE measurement 
ADD CONSTRAINT fk_measurement_driver 
    FOREIGN KEY (driver_id) 
    REFERENCES driver(id) 
    ON DELETE SET NULL;

-- =====================================================
-- 5. PIPELINE TABLE
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
-- 6. PIPELINEDATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS pipelinedata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    name TEXT,
    type SMALLINT NOT NULL,
    datastream_id UUID,
    scene_id UUID,
    source TEXT,
    data_path TEXT,
    params TEXT,  -- JSON string for parameters
    CONSTRAINT fk_pipelinedata_datastream 
        FOREIGN KEY (datastream_id) 
        REFERENCES datastream(id) 
        ON DELETE SET NULL
);

-- Create indexes for pipelinedata table
CREATE INDEX IF NOT EXISTS idx_pipelinedata_type ON pipelinedata(type);
CREATE INDEX IF NOT EXISTS idx_pipelinedata_datastream_id ON pipelinedata(datastream_id);
CREATE INDEX IF NOT EXISTS idx_pipelinedata_scene_id ON pipelinedata(scene_id);
CREATE INDEX IF NOT EXISTS idx_pipelinedata_source ON pipelinedata(source);
CREATE INDEX IF NOT EXISTS idx_pipelinedata_created_at ON pipelinedata(created_at DESC);

-- Add comments
COMMENT ON TABLE pipelinedata IS 'Pipeline data entries for processing jobs';
COMMENT ON COLUMN pipelinedata.id IS 'Unique identifier for the pipeline data';
COMMENT ON COLUMN pipelinedata.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN pipelinedata.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN pipelinedata.name IS 'Name or description of the pipeline data';
COMMENT ON COLUMN pipelinedata.type IS 'Type of pipeline data (0=RAW_DATA, 1=PROCESSED_DATA, 2=ANNOTATED_DATA, 3=VALIDATED_DATA, 4=TRAINING_DATA, 5=TEST_DATA, 99=OTHER)';
COMMENT ON COLUMN pipelinedata.datastream_id IS 'Reference to associated datastream';
COMMENT ON COLUMN pipelinedata.scene_id IS 'Reference to associated scene';
COMMENT ON COLUMN pipelinedata.source IS 'Source information for the data';
COMMENT ON COLUMN pipelinedata.data_path IS 'Path to the data file or directory';
COMMENT ON COLUMN pipelinedata.params IS 'Additional parameters as JSON string';

-- Add foreign key for scene reference (defined after scene table exists)
ALTER TABLE IF EXISTS pipelinedata
    ADD CONSTRAINT fk_pipelinedata_scene
    FOREIGN KEY (scene_id)
    REFERENCES scene(id)
    ON DELETE SET NULL;

-- =====================================================
-- 7. PIPELINESTATE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS pipelinestate (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    pipelinedata_id UUID NOT NULL,
    pipeline_id UUID NOT NULL,
    input TEXT NOT NULL,  -- JSON string for input configuration
    output TEXT NOT NULL,  -- JSON string for output results
    state SMALLINT NOT NULL,
    CONSTRAINT fk_pipelinestate_pipelinedata 
        FOREIGN KEY (pipelinedata_id) 
        REFERENCES pipelinedata(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_pipelinestate_pipeline 
        FOREIGN KEY (pipeline_id) 
        REFERENCES pipeline(id) 
        ON DELETE CASCADE
);

-- Create indexes for pipelinestate table
CREATE INDEX IF NOT EXISTS idx_pipelinestate_pipelinedata_id ON pipelinestate(pipelinedata_id);
CREATE INDEX IF NOT EXISTS idx_pipelinestate_pipeline_id ON pipelinestate(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_pipelinestate_state ON pipelinestate(state);
CREATE INDEX IF NOT EXISTS idx_pipelinestate_created_at ON pipelinestate(created_at DESC);

-- Add comments
COMMENT ON TABLE pipelinestate IS 'Pipeline execution states representing jobs';
COMMENT ON COLUMN pipelinestate.id IS 'Unique identifier for the pipeline state';
COMMENT ON COLUMN pipelinestate.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN pipelinestate.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN pipelinestate.pipelinedata_id IS 'Reference to the pipeline data being processed';
COMMENT ON COLUMN pipelinestate.pipeline_id IS 'Reference to the pipeline configuration';
COMMENT ON COLUMN pipelinestate.input IS 'Input configuration as JSON string';
COMMENT ON COLUMN pipelinestate.output IS 'Output results as JSON string';
COMMENT ON COLUMN pipelinestate.state IS 'Execution state (0=PENDING, 1=RUNNING, 2=COMPLETED, 3=FAILED, 4=CANCELLED, 5=PAUSED)';

-- =====================================================
-- 8. PIPELINEDEPENDENCY TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS pipelinedependency (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL,
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    CONSTRAINT fk_pipelinedependency_parent 
        FOREIGN KEY (parent_id) 
        REFERENCES pipelinestate(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_pipelinedependency_child 
        FOREIGN KEY (child_id) 
        REFERENCES pipelinestate(id) 
        ON DELETE CASCADE,
    CONSTRAINT uk_pipelinedependency_parent_child 
        UNIQUE (parent_id, child_id)
);

-- Create indexes for pipelinedependency table
CREATE INDEX IF NOT EXISTS idx_pipelinedependency_parent_id ON pipelinedependency(parent_id);
CREATE INDEX IF NOT EXISTS idx_pipelinedependency_child_id ON pipelinedependency(child_id);
CREATE INDEX IF NOT EXISTS idx_pipelinedependency_created_at ON pipelinedependency(created_at DESC);

-- Add comments
COMMENT ON TABLE pipelinedependency IS 'Dependencies between pipeline states (jobs)';
COMMENT ON COLUMN pipelinedependency.id IS 'Unique identifier for the dependency';
COMMENT ON COLUMN pipelinedependency.created_at IS 'Unix timestamp when the record was created';
COMMENT ON COLUMN pipelinedependency.updated_at IS 'Unix timestamp when the record was last updated';
COMMENT ON COLUMN pipelinedependency.parent_id IS 'Reference to the parent pipeline state (must complete before child)';
COMMENT ON COLUMN pipelinedependency.child_id IS 'Reference to the child pipeline state (depends on parent)';

-- =====================================================
-- End of Table Creation Script
-- =====================================================
