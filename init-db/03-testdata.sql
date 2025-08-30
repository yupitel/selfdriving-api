-- =====================================================
-- Test Data Script for Self-Driving Data Collection
-- =====================================================
-- This script inserts test data for development and testing
-- Tables: vehicle, measurement, datastream, pipeline

-- Use the selfdriving schema
SET search_path TO selfdriving;

-- =====================================================
-- 1. VEHICLE TEST DATA
-- =====================================================
-- Clear existing test data (optional - comment out in production)
-- DELETE FROM vehicle WHERE name LIKE 'TEST-%';

-- Insert test vehicles from different countries
INSERT INTO vehicle (id, created_at, updated_at, country, name, data_path, type, status)
VALUES 
    -- Japanese vehicles
    ('11111111-1111-1111-1111-111111111111', EXTRACT(EPOCH FROM NOW() - INTERVAL '30 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'JP', 'TEST-JP-001', '/data/vehicles/jp/001', 0, 1),  -- SEDAN, ACTIVE
    ('11111111-1111-1111-1111-111111111112', EXTRACT(EPOCH FROM NOW() - INTERVAL '25 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'JP', 'TEST-JP-002', '/data/vehicles/jp/002', 1, 1),  -- SUV, ACTIVE
    ('11111111-1111-1111-1111-111111111113', EXTRACT(EPOCH FROM NOW() - INTERVAL '20 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'JP', 'TEST-JP-003', '/data/vehicles/jp/003', 5, 2),  -- COMPACT, MAINTENANCE
    
    -- US vehicles
    ('11111111-1111-1111-1111-111111111114', EXTRACT(EPOCH FROM NOW() - INTERVAL '28 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'US', 'TEST-US-001', '/data/vehicles/us/001', 2, 1),  -- TRUCK, ACTIVE
    ('11111111-1111-1111-1111-111111111115', EXTRACT(EPOCH FROM NOW() - INTERVAL '22 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'US', 'TEST-US-002', '/data/vehicles/us/002', 1, 3),  -- SUV, TESTING
    
    -- German vehicles
    ('11111111-1111-1111-1111-111111111116', EXTRACT(EPOCH FROM NOW() - INTERVAL '15 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'DE', 'TEST-DE-001', '/data/vehicles/de/001', 0, 1),  -- SEDAN, ACTIVE
    ('11111111-1111-1111-1111-111111111117', EXTRACT(EPOCH FROM NOW() - INTERVAL '10 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'DE', 'TEST-DE-002', '/data/vehicles/de/002', 4, 4),  -- BUS, OFFLINE
    
    -- Chinese vehicles
    ('11111111-1111-1111-1111-111111111118', EXTRACT(EPOCH FROM NOW() - INTERVAL '18 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     'CN', 'TEST-CN-001', '/data/vehicles/cn/001', 3, 1),  -- VAN, ACTIVE
    
    -- Vehicle without country - experimental type
    ('11111111-1111-1111-1111-111111111119', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT, 
     NULL, 'TEST-GLOBAL-001', NULL, 99, 0)  -- EXPERIMENTAL, INACTIVE
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 2. MEASUREMENT TEST DATA
-- =====================================================
-- Insert test measurements for different vehicles and areas
INSERT INTO measurement (id, created_at, updated_at, vehicle_id, area_id, local_time, measured_at, name, data_path)
VALUES 
    -- Measurements for JP-001 (Tokyo area)
    ('22222222-2222-2222-2222-222222222221', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     NOW() - INTERVAL '7 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT,
     'Tokyo Highway Test Run 001', '/data/measurements/2025/01/tokyo_001'),
    
    ('22222222-2222-2222-2222-222222222222', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     NOW() - INTERVAL '6 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT,
     'Tokyo City Center Test 001', '/data/measurements/2025/01/tokyo_002'),
    
    ('22222222-2222-2222-2222-222222222223', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     NOW() - INTERVAL '5 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT,
     'Tokyo Rainy Day Test', '/data/measurements/2025/01/tokyo_003'),
    
    -- Measurements for JP-002 (Osaka area)
    ('22222222-2222-2222-2222-222222222224', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111112', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
     NOW() - INTERVAL '4 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT,
     'Osaka Urban Test 001', '/data/measurements/2025/01/osaka_001'),
    
    ('22222222-2222-2222-2222-222222222225', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111112', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
     NOW() - INTERVAL '3 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT,
     'Osaka Night Drive', '/data/measurements/2025/01/osaka_002'),
    
    -- Measurements for US-001 (California)
    ('22222222-2222-2222-2222-222222222226', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111114', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
     NOW() - INTERVAL '2 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT,
     'California Highway 101 Test', '/data/measurements/2025/01/california_001'),
    
    ('22222222-2222-2222-2222-222222222227', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111114', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
     NOW() - INTERVAL '1 day', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT,
     'San Francisco City Test', '/data/measurements/2025/01/sf_001'),
    
    -- Measurements for DE-001 (Berlin)
    ('22222222-2222-2222-2222-222222222228', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111116', 'dddddddd-dddd-dddd-dddd-dddddddddddd',
     NOW() - INTERVAL '12 hours', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 hours')::BIGINT,
     'Berlin Autobahn Test', '/data/measurements/2025/01/berlin_001'),
    
    ('22222222-2222-2222-2222-222222222229', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111116', 'dddddddd-dddd-dddd-dddd-dddddddddddd',
     NOW() - INTERVAL '6 hours', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 hours')::BIGINT,
     'Berlin Winter Conditions', '/data/measurements/2025/01/berlin_002'),
    
    -- Measurement without name
    ('22222222-2222-2222-2222-222222222230', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111118', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
     NOW() - INTERVAL '3 hours', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 hours')::BIGINT,
     NULL, '/data/measurements/2025/01/unnamed_001')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 3. DATASTREAM TEST DATA
-- =====================================================
-- Insert test datastreams for measurements
INSERT INTO datastream (id, created_at, updated_at, type, measurement_id, name, data_path, src_path)
VALUES 
    -- Datastreams for Tokyo Highway Test (multiple sensor types)
    ('33333333-3333-3333-3333-333333333331', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222221', 
     'Front Camera Stream', '/processed/camera/tokyo_001_front.mp4', '/raw/camera/tokyo_001_front.raw'),
    
    ('33333333-3333-3333-3333-333333333332', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222221', 
     'Rear Camera Stream', '/processed/camera/tokyo_001_rear.mp4', '/raw/camera/tokyo_001_rear.raw'),
    
    ('33333333-3333-3333-3333-333333333333', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     1, '22222222-2222-2222-2222-222222222221', 
     'LIDAR Point Cloud', '/processed/lidar/tokyo_001.pcd', '/raw/lidar/tokyo_001.bin'),
    
    ('33333333-3333-3333-3333-333333333334', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     2, '22222222-2222-2222-2222-222222222221', 
     'RADAR Data', '/processed/radar/tokyo_001.json', '/raw/radar/tokyo_001.dat'),
    
    ('33333333-3333-3333-3333-333333333335', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     3, '22222222-2222-2222-2222-222222222221', 
     'IMU Sensor Data', '/processed/imu/tokyo_001.csv', '/raw/imu/tokyo_001.bin'),
    
    ('33333333-3333-3333-3333-333333333336', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     4, '22222222-2222-2222-2222-222222222221', 
     'GPS Location Data', '/processed/gps/tokyo_001.kml', '/raw/gps/tokyo_001.nmea'),
    
    -- Datastreams for Tokyo City Center Test
    ('33333333-3333-3333-3333-333333333337', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222222', 
     'Multi-Camera Array', '/processed/camera/tokyo_002_multi.mp4', '/raw/camera/tokyo_002_multi.raw'),
    
    ('33333333-3333-3333-3333-333333333338', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     1, '22222222-2222-2222-2222-222222222222', 
     'High-Res LIDAR', '/processed/lidar/tokyo_002_hd.pcd', '/raw/lidar/tokyo_002_hd.bin'),
    
    ('33333333-3333-3333-3333-333333333339', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     5, '22222222-2222-2222-2222-222222222222', 
     'CAN Bus Data', '/processed/can/tokyo_002.log', '/raw/can/tokyo_002.can'),
    
    -- Datastreams for Osaka Urban Test
    ('33333333-3333-3333-3333-333333333340', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222224', 
     '360 Camera', '/processed/camera/osaka_001_360.mp4', '/raw/camera/osaka_001_360.raw'),
    
    ('33333333-3333-3333-3333-333333333341', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     6, '22222222-2222-2222-2222-222222222224', 
     'Ultrasonic Sensors', '/processed/ultrasonic/osaka_001.json', '/raw/ultrasonic/osaka_001.dat'),
    
    -- Datastreams for California Highway Test
    ('33333333-3333-3333-3333-333333333342', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222226', 
     '8K Front Camera', '/processed/camera/cal_001_8k.mp4', '/raw/camera/cal_001_8k.raw'),
    
    ('33333333-3333-3333-3333-333333333343', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     7, '22222222-2222-2222-2222-222222222226', 
     'Thermal Camera', '/processed/thermal/cal_001.tiff', '/raw/thermal/cal_001.raw'),
    
    -- Datastreams for Berlin tests
    ('33333333-3333-3333-3333-333333333344', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222228', 
     'HDR Camera Stream', '/processed/camera/berlin_001_hdr.mp4', '/raw/camera/berlin_001_hdr.raw'),
    
    ('33333333-3333-3333-3333-333333333345', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     8, '22222222-2222-2222-2222-222222222228', 
     'Microphone Array', '/processed/audio/berlin_001.wav', '/raw/audio/berlin_001.pcm'),
    
    -- Datastream without name
    ('33333333-3333-3333-3333-333333333346', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     99, '22222222-2222-2222-2222-222222222229', 
     NULL, '/processed/other/berlin_002.dat', NULL),
    
    -- Multiple datastreams for same measurement with same type
    ('33333333-3333-3333-3333-333333333347', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222227', 
     'Left Camera', '/processed/camera/sf_001_left.mp4', '/raw/camera/sf_001_left.raw'),
    
    ('33333333-3333-3333-3333-333333333348', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222227', 
     'Right Camera', '/processed/camera/sf_001_right.mp4', '/raw/camera/sf_001_right.raw'),
    
    ('33333333-3333-3333-3333-333333333349', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222227', 
     'Center Camera', '/processed/camera/sf_001_center.mp4', '/raw/camera/sf_001_center.raw')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 4. PIPELINE TEST DATA
-- =====================================================
-- Insert test pipelines with various configurations
INSERT INTO pipeline (id, created_at, updated_at, name, type, "group", is_available, version, options, params)
VALUES 
    -- Data Collection Pipelines
    ('44444444-4444-4444-4444-444444444441', EXTRACT(EPOCH FROM NOW() - INTERVAL '60 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Basic Data Collection Pipeline', 0, 1, 1, 1,
     '{"retry_count": 3, "timeout_seconds": 3600, "parallel_workers": 4}',
     '{"input_format": "raw", "output_format": "processed", "compression": "gzip", "batch_size": 100}'),
    
    ('44444444-4444-4444-4444-444444444442', EXTRACT(EPOCH FROM NOW() - INTERVAL '55 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'High-Speed Data Collection', 0, 1, 1, 2,
     '{"retry_count": 5, "timeout_seconds": 7200, "parallel_workers": 8, "priority": "high"}',
     '{"input_format": "raw", "output_format": "processed", "compression": "lz4", "batch_size": 500, "buffer_size": "2GB"}'),
    
    -- Data Processing Pipelines
    ('44444444-4444-4444-4444-444444444443', EXTRACT(EPOCH FROM NOW() - INTERVAL '50 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'LIDAR Point Cloud Processing', 1, 2, 1, 1,
     '{"gpu_required": true, "memory_limit": "32GB", "cpu_cores": 16}',
     '{"input_type": "point_cloud", "output_type": "segmented_cloud", "voxel_size": 0.05, "outlier_removal": true}'),
    
    ('44444444-4444-4444-4444-444444444444', EXTRACT(EPOCH FROM NOW() - INTERVAL '45 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Video Frame Extraction', 1, 2, 1, 1,
     '{"gpu_required": false, "memory_limit": "8GB"}',
     '{"input_type": "video", "output_type": "frames", "fps": 30, "format": "jpeg", "quality": 95}'),
    
    -- Data Validation Pipelines
    ('44444444-4444-4444-4444-444444444445', EXTRACT(EPOCH FROM NOW() - INTERVAL '40 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Sensor Data Validation', 2, 3, 1, 1,
     '{"parallel_validation": true, "fail_fast": false}',
     '{"validation_rules": ["timestamp_check", "range_check", "format_check"], "threshold": 0.95}'),
    
    ('44444444-4444-4444-4444-444444444446', EXTRACT(EPOCH FROM NOW() - INTERVAL '35 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'GPS Coordinate Validator', 2, 3, 1, 2,
     NULL,
     '{"coordinate_system": "WGS84", "boundary_check": true, "max_speed": 200, "min_accuracy": 10}'),
    
    -- ML Training Pipelines
    ('44444444-4444-4444-4444-444444444447', EXTRACT(EPOCH FROM NOW() - INTERVAL '30 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Object Detection Training', 3, 4, 1, 1,
     '{"gpu_required": true, "gpu_count": 4, "distributed": true}',
     '{"model": "yolov8", "epochs": 100, "batch_size": 32, "learning_rate": 0.001, "augmentation": true}'),
    
    ('44444444-4444-4444-4444-444444444448', EXTRACT(EPOCH FROM NOW() - INTERVAL '25 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Lane Detection Training', 3, 4, 1, 1,
     '{"gpu_required": true, "gpu_count": 2}',
     '{"model": "lanenet", "epochs": 50, "batch_size": 16, "optimizer": "adam"}'),
    
    -- ML Inference Pipelines
    ('44444444-4444-4444-4444-444444444449', EXTRACT(EPOCH FROM NOW() - INTERVAL '20 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Real-time Object Detection', 4, 5, 1, 1,
     '{"gpu_required": true, "latency_target": 100}',
     '{"model_path": "/models/yolov8_best.pt", "confidence_threshold": 0.5, "nms_threshold": 0.4}'),
    
    ('44444444-4444-4444-4444-444444444450', EXTRACT(EPOCH FROM NOW() - INTERVAL '18 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Semantic Segmentation Inference', 4, 5, 0, 1,  -- Unavailable pipeline
     '{"gpu_required": true, "batch_processing": true}',
     '{"model_path": "/models/segnet_v2.pt", "classes": 19, "input_size": [1024, 1024]}'),
    
    -- Data Export Pipelines
    ('44444444-4444-4444-4444-444444444451', EXTRACT(EPOCH FROM NOW() - INTERVAL '15 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Dataset Export to S3', 5, 6, 1, 1,
     '{"retry_count": 3, "multipart_threshold": "100MB"}',
     '{"destination": "s3://bucket/datasets/", "format": "parquet", "compression": "snappy"}'),
    
    ('44444444-4444-4444-4444-444444444452', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Report Generation Pipeline', 5, 6, 1, 2,
     '{"template": "standard_report_v2"}',
     '{"output_format": "pdf", "include_charts": true, "language": "en"}'),
    
    -- Data Import Pipelines
    ('44444444-4444-4444-4444-444444444453', EXTRACT(EPOCH FROM NOW() - INTERVAL '10 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'ROS Bag Import', 6, 7, 1, 1,
     '{"max_file_size": "10GB", "parallel_import": false}',
     '{"source_format": "rosbag", "topics": ["/camera/image", "/lidar/points", "/gps/fix"]}'),
    
    ('44444444-4444-4444-4444-444444444454', EXTRACT(EPOCH FROM NOW() - INTERVAL '8 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'CSV Sensor Data Import', 6, 7, 1, 1,
     NULL,
     '{"delimiter": ",", "has_header": true, "encoding": "utf-8", "datetime_format": "ISO8601"}'),
    
    -- Quality Check Pipelines
    ('44444444-4444-4444-4444-444444444455', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Image Quality Assessment', 7, 8, 1, 1,
     '{"gpu_required": false}',
     '{"metrics": ["blur_detection", "brightness", "contrast", "noise_level"], "threshold_config": "strict"}'),
    
    ('44444444-4444-4444-4444-444444444456', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Sensor Synchronization Check', 7, 8, 1, 3,
     '{"tolerance_ms": 50}',
     '{"reference_sensor": "gps", "check_sensors": ["camera", "lidar", "imu"], "report_format": "json"}'),
    
    -- Annotation Pipelines
    ('44444444-4444-4444-4444-444444444457', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Auto-labeling Pipeline', 8, 9, 1, 1,
     '{"gpu_required": true, "confidence_threshold": 0.8}',
     '{"annotation_format": "coco", "classes": ["car", "truck", "bus", "pedestrian", "cyclist"]}'),
    
    ('44444444-4444-4444-4444-444444444458', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Manual Annotation Export', 8, 9, 1, 1,
     NULL,
     '{"source": "label_studio", "format": "yolo", "split_ratio": [0.8, 0.1, 0.1]}'),
    
    -- Other/Custom Pipelines
    ('44444444-4444-4444-4444-444444444459', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Custom Data Transform', 99, 10, 1, 1,
     '{"custom_script": "/scripts/transform.py"}',
     '{"input_schema": "v1", "output_schema": "v2", "validation": true}'),
    
    ('44444444-4444-4444-4444-444444444460', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Experimental Pipeline', 99, 10, 0, 1,  -- Unavailable pipeline
     '{"experimental": true, "monitoring": "verbose"}',
     '{"algorithm": "proprietary_v1", "parameters": {"alpha": 0.5, "beta": 0.3}}')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 5. VERIFICATION QUERIES
-- =====================================================
-- Run these queries to verify the test data was inserted correctly

-- Check record counts
DO $$
DECLARE
    vehicle_count INTEGER;
    measurement_count INTEGER;
    datastream_count INTEGER;
    pipeline_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO vehicle_count FROM vehicle WHERE name LIKE 'TEST-%';
    SELECT COUNT(*) INTO measurement_count FROM measurement;
    SELECT COUNT(*) INTO datastream_count FROM datastream;
    SELECT COUNT(*) INTO pipeline_count FROM pipeline;
    
    RAISE NOTICE 'Test data insertion complete:';
    RAISE NOTICE '  Vehicles: % records', vehicle_count;
    RAISE NOTICE '  Measurements: % records', measurement_count;
    RAISE NOTICE '  Datastreams: % records', datastream_count;
    RAISE NOTICE '  Pipelines: % records', pipeline_count;
END $$;

-- =====================================================
-- End of Test Data Script
-- =====================================================