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
-- 2. DRIVER TEST DATA
-- =====================================================
-- Insert test drivers with various certification levels and statuses
INSERT INTO driver (id, created_at, updated_at, email, name, name_kana, 
    license_number, license_type, license_expiry_date, 
    certification_level, certification_date, training_completed_date,
    status, employment_type, department, team, supervisor_id,
    total_drives, total_distance, total_duration, last_drive_date,
    safety_score, efficiency_score, data_quality_score,
    phone_number, emergency_contact, notes, metadata)
VALUES
    -- Expert drivers
    ('d1111111-1111-1111-1111-111111111111', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 years')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'tanaka.taro@example.com', 'Tanaka Taro', 'タナカ タロウ',
     '123456789012', 'Large Vehicle', '2026-05-15',
     3, '2022-06-01', '2022-03-01',  -- EXPERT level
     1, 0, 'Operations', 'Team A', NULL,  -- ACTIVE, FULL_TIME, no supervisor
     250, 12500.5, 900000, CURRENT_DATE - INTERVAL '1 day',
     0.95, 0.88, 0.92,
     '090-1234-5678', '090-8765-4321 (Wife)', 'Senior driver, team leader', 
     '{"languages": ["jp", "en"], "special_qualifications": ["night_driving", "bad_weather"]}'),
    
    -- Advanced drivers
    ('d1111111-1111-1111-1111-111111111112', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 year')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'yamada.hanako@example.com', 'Yamada Hanako', 'ヤマダ ハナコ',
     '234567890123', 'Standard', '2025-08-20',
     2, '2023-09-15', '2023-06-01',  -- ADVANCED level
     1, 0, 'Operations', 'Team A', 'd1111111-1111-1111-1111-111111111111',  -- Reports to Tanaka
     180, 8200.3, 648000, CURRENT_DATE - INTERVAL '2 days',
     0.92, 0.85, 0.88,
     '090-2345-6789', '090-7654-3210 (Husband)', 'Experienced driver',
     '{"languages": ["jp"], "special_qualifications": ["highway"]}'),
    
    ('d1111111-1111-1111-1111-111111111113', EXTRACT(EPOCH FROM NOW() - INTERVAL '18 months')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'suzuki.ichiro@example.com', 'Suzuki Ichiro', 'スズキ イチロウ',
     '345678901234', 'Large Vehicle', '2027-03-10',
     2, '2023-03-20', '2022-12-01',  -- ADVANCED level
     1, 1, 'Operations', 'Team B', NULL,  -- ACTIVE, CONTRACT
     200, 9500.0, 720000, CURRENT_DATE - INTERVAL '3 days',
     0.90, 0.87, 0.85,
     '090-3456-7890', '090-6543-2109', 'Contract driver, night shift specialist',
     '{"languages": ["jp", "en"], "shift": "night"}'),
    
    -- Basic drivers
    ('d1111111-1111-1111-1111-111111111114', EXTRACT(EPOCH FROM NOW() - INTERVAL '8 months')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'sato.jiro@example.com', 'Sato Jiro', 'サトウ ジロウ',
     '456789012345', 'Standard', '2025-11-30',
     1, '2024-03-01', '2024-01-15',  -- BASIC level
     1, 0, 'Operations', 'Team B', 'd1111111-1111-1111-1111-111111111113',  -- Reports to Suzuki
     80, 3200.0, 288000, CURRENT_DATE - INTERVAL '5 days',
     0.88, 0.82, 0.86,
     '090-4567-8901', '090-5432-1098', 'Recently certified',
     '{"languages": ["jp"]}'),
    
    ('d1111111-1111-1111-1111-111111111115', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 months')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'takahashi.yuki@example.com', 'Takahashi Yuki', 'タカハシ ユキ',
     '567890123456', 'Standard', '2026-02-28',
     1, '2024-05-10', '2024-03-01',  -- BASIC level
     1, 2, 'Operations', 'Team C', NULL,  -- ACTIVE, PART_TIME
     45, 1800.5, 162000, CURRENT_DATE - INTERVAL '7 days',
     0.85, 0.80, 0.83,
     '090-5678-9012', '090-4321-0987', 'Part-time driver, weekends only',
     '{"languages": ["jp"], "availability": "weekends"}'),
    
    -- Trainee drivers
    ('d1111111-1111-1111-1111-111111111116', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 months')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'ito.kenji@example.com', 'Ito Kenji', 'イトウ ケンジ',
     '678901234567', 'Standard', '2024-12-15',
     0, NULL, NULL,  -- TRAINEE level, not yet certified
     1, 0, 'Training', 'Training Group', 'd1111111-1111-1111-1111-111111111111',  -- Under Tanaka's supervision
     12, 480.0, 43200, CURRENT_DATE - INTERVAL '10 days',
     0.78, 0.75, 0.77,
     '090-6789-0123', '090-3210-9876', 'In training program',
     '{"languages": ["jp"], "training_progress": 65}'),
    
    ('d1111111-1111-1111-1111-111111111117', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 month')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'watanabe.mari@example.com', 'Watanabe Mari', 'ワタナベ マリ',
     '789012345678', 'Standard', '2025-06-30',
     0, NULL, NULL,  -- TRAINEE level
     0, 3, 'Training', 'Training Group', 'd1111111-1111-1111-1111-111111111112',  -- Under Yamada's supervision
     5, 200.0, 18000, CURRENT_DATE - INTERVAL '15 days',
     0.72, 0.70, 0.74,
     '090-7890-1234', '090-2109-8765', 'New trainee, external contractor',
     '{"languages": ["jp", "en"], "training_progress": 30, "company": "ABC Contractors"}'),
    
    -- Inactive/On leave drivers
    ('d1111111-1111-1111-1111-111111111118', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 years')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'nakamura.shin@example.com', 'Nakamura Shin', 'ナカムラ シン',
     '890123456789', 'Large Vehicle', '2024-09-20',
     2, '2022-12-01', '2022-09-01',  -- ADVANCED level
     2, 0, 'Operations', 'Team A', 'd1111111-1111-1111-1111-111111111111',  -- ON_LEAVE
     150, 7500.0, 540000, '2024-10-01',
     0.91, 0.86, 0.89,
     '090-8901-2345', '090-1098-7654', 'On paternity leave',
     '{"languages": ["jp"], "leave_reason": "paternity", "expected_return": "2025-03-01"}'),
    
    -- Retired driver
    ('d1111111-1111-1111-1111-111111111119', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 years')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'kobayashi.retired@example.com', 'Kobayashi Takeshi', 'コバヤシ タケシ',
     '901234567890', 'Large Vehicle', '2023-12-31',
     3, '2021-01-15', '2020-10-01',  -- EXPERT level
     3, 0, 'Operations', 'Team A', NULL,  -- RETIRED
     500, 25000.0, 1800000, '2024-06-30',
     0.96, 0.90, 0.94,
     NULL, NULL, 'Retired after 3 years of service',
     '{"languages": ["jp", "en", "cn"], "retirement_date": "2024-06-30"}'),
    
    -- Driver without scores (new)
    ('d1111111-1111-1111-1111-111111111120', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 week')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'yoshida.new@example.com', 'Yoshida Kazuya', 'ヨシダ カズヤ',
     '012345678901', 'Standard', '2026-07-15',
     0, NULL, NULL,  -- TRAINEE level
     1, 0, 'Training', 'Training Group', 'd1111111-1111-1111-1111-111111111113',
     0, 0, 0, NULL,  -- No drives yet
     NULL, NULL, NULL,  -- No scores yet
     '090-9012-3456', '090-0987-6543', 'Just started training',
     '{"languages": ["jp"], "training_progress": 5, "start_date": "' || (CURRENT_DATE - INTERVAL '7 days')::TEXT || '"}')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 3. MEASUREMENT TEST DATA (Updated with driver_id)
-- =====================================================
-- Insert test measurements for different vehicles and areas
INSERT INTO measurement (id, created_at, updated_at, vehicle_id, area_id, driver_id, local_time, measured_at, name, data_path, distance, duration, start_location, end_location, weather_condition, road_condition)
VALUES 
    -- Measurements for JP-001 (Tokyo area) - Driven by Tanaka (Expert)
    ('22222222-2222-2222-2222-222222222221', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'd1111111-1111-1111-1111-111111111111',
     NOW() - INTERVAL '7 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT,
     'Tokyo Highway Test Run 001', '/data/measurements/2025/01/tokyo_001',
     85.3, 5400, '{"lat": 35.6762, "lng": 139.6503}', '{"lat": 35.4437, "lng": 139.6380}', 'Clear', 'Dry'),
    
    ('22222222-2222-2222-2222-222222222222', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'd1111111-1111-1111-1111-111111111112',  -- Yamada (Advanced)
     NOW() - INTERVAL '6 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT,
     'Tokyo City Center Test 001', '/data/measurements/2025/01/tokyo_002',
     42.1, 3600, '{"lat": 35.6895, "lng": 139.6917}', '{"lat": 35.6762, "lng": 139.6503}', 'Clear', 'Dry'),
    
    ('22222222-2222-2222-2222-222222222223', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'd1111111-1111-1111-1111-111111111113',  -- Suzuki (Advanced)
     NOW() - INTERVAL '5 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT,
     'Tokyo Rainy Day Test', '/data/measurements/2025/01/tokyo_003',
     68.5, 7200, '{"lat": 35.6762, "lng": 139.6503}', '{"lat": 35.5494, "lng": 139.7798}', 'Rainy', 'Wet'),
    
    -- Measurements for JP-002 (Osaka area) - Driven by Sato (Basic)
    ('22222222-2222-2222-2222-222222222224', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111112', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'd1111111-1111-1111-1111-111111111114',
     NOW() - INTERVAL '4 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT,
     'Osaka Urban Test 001', '/data/measurements/2025/01/osaka_001',
     35.8, 2700, '{"lat": 34.6937, "lng": 135.5023}', '{"lat": 34.6690, "lng": 135.5190}', 'Cloudy', 'Dry'),
    
    ('22222222-2222-2222-2222-222222222225', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111112', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'd1111111-1111-1111-1111-111111111113',  -- Suzuki (Advanced)
     NOW() - INTERVAL '3 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT,
     'Osaka Night Drive', '/data/measurements/2025/01/osaka_002',
     52.3, 4500, '{"lat": 34.6937, "lng": 135.5023}', '{"lat": 34.7055, "lng": 135.4959}', 'Clear', 'Dry'),
    
    -- Measurements for US-001 (California) - Driven by Tanaka and Yamada
    ('22222222-2222-2222-2222-222222222226', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111114', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'd1111111-1111-1111-1111-111111111111',  -- Tanaka (Expert)
     NOW() - INTERVAL '2 days', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT,
     'California Highway 101 Test', '/data/measurements/2025/01/california_001',
     120.5, 6300, '{"lat": 37.7749, "lng": -122.4194}', '{"lat": 37.3352, "lng": -121.8811}', 'Sunny', 'Dry'),
    
    ('22222222-2222-2222-2222-222222222227', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111114', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'd1111111-1111-1111-1111-111111111112',  -- Yamada (Advanced)
     NOW() - INTERVAL '1 day', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT,
     'San Francisco City Test', '/data/measurements/2025/01/sf_001',
     28.7, 2400, '{"lat": 37.7749, "lng": -122.4194}', '{"lat": 37.7749, "lng": -122.4194}', 'Foggy', 'Damp'),
    
    -- Measurements for DE-001 (Berlin) - Driven by Takahashi (Basic, Part-time)
    ('22222222-2222-2222-2222-222222222228', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111116', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'd1111111-1111-1111-1111-111111111115',
     NOW() - INTERVAL '12 hours', EXTRACT(EPOCH FROM NOW() - INTERVAL '12 hours')::BIGINT,
     'Berlin Autobahn Test', '/data/measurements/2025/01/berlin_001',
     95.2, 3900, '{"lat": 52.5200, "lng": 13.4050}', '{"lat": 52.3906, "lng": 13.0644}', 'Cloudy', 'Dry'),
    
    ('22222222-2222-2222-2222-222222222229', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111116', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'd1111111-1111-1111-1111-111111111115',  -- Takahashi again
     NOW() - INTERVAL '6 hours', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 hours')::BIGINT,
     'Berlin Winter Conditions', '/data/measurements/2025/01/berlin_002',
     45.6, 4800, '{"lat": 52.5200, "lng": 13.4050}', '{"lat": 52.4597, "lng": 13.5264}', 'Snowy', 'Icy'),
    
    -- Measurement without driver (autonomous test?)
    ('22222222-2222-2222-2222-222222222230', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '11111111-1111-1111-1111-111111111118', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', NULL,  -- No driver assigned
     NOW() - INTERVAL '3 hours', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 hours')::BIGINT,
     NULL, '/data/measurements/2025/01/unnamed_001',
     15.3, 1800, '{"lat": 31.2304, "lng": 121.4737}', '{"lat": 31.2304, "lng": 121.4737}', NULL, NULL)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 3. DATASTREAM TEST DATA
-- =====================================================
-- Insert test datastreams for measurements
-- Note: Each measurement can have multiple 30-minute datastream segments
INSERT INTO datastream (id, created_at, updated_at, type, measurement_id, name, data_path, src_path, sequence_number, start_time, end_time, duration, video_url, has_data_loss, data_loss_duration, processing_status)
VALUES 
    -- Datastreams for Tokyo Highway Test (90 min drive = 3 segments)
    -- Segment 1 (0-30 min)
    ('33333333-3333-3333-3333-333333333331', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222221', 
     'Tokyo Highway Segment 1', '/processed/camera/tokyo_001_seg1.mp4', '/raw/camera/tokyo_001_seg1.raw',
     1, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '30 minutes', 1800000,
     'https://video.example.com/tokyo_001_seg1.mp4', false, 0, 2),
    
    -- Segment 2 (30-60 min)
    ('33333333-3333-3333-3333-333333333332', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222221', 
     'Tokyo Highway Segment 2', '/processed/camera/tokyo_001_seg2.mp4', '/raw/camera/tokyo_001_seg2.raw',
     2, NOW() - INTERVAL '7 days' + INTERVAL '30 minutes', NOW() - INTERVAL '7 days' + INTERVAL '60 minutes', 1800000,
     'https://video.example.com/tokyo_001_seg2.mp4', false, 0, 2),
    
    -- Segment 3 (60-90 min) - with data loss
    ('33333333-3333-3333-3333-333333333333', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222221', 
     'Tokyo Highway Segment 3', '/processed/camera/tokyo_001_seg3.mp4', '/raw/camera/tokyo_001_seg3.raw',
     3, NOW() - INTERVAL '7 days' + INTERVAL '60 minutes', NOW() - INTERVAL '7 days' + INTERVAL '90 minutes', 1800000,
     'https://video.example.com/tokyo_001_seg3.mp4', true, 45000, 2),
    
    -- Datastreams for Tokyo City Center Test (60 min = 2 segments)
    -- Segment 1
    ('33333333-3333-3333-3333-333333333337', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222222', 
     'Tokyo City Segment 1', '/processed/camera/tokyo_002_seg1.mp4', '/raw/camera/tokyo_002_seg1.raw',
     1, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '30 minutes', 1800000,
     'https://video.example.com/tokyo_002_seg1.mp4', false, 0, 2),
    
    -- Segment 2
    ('33333333-3333-3333-3333-333333333338', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222222', 
     'Tokyo City Segment 2', '/processed/camera/tokyo_002_seg2.mp4', '/raw/camera/tokyo_002_seg2.raw',
     2, NOW() - INTERVAL '6 days' + INTERVAL '30 minutes', NOW() - INTERVAL '6 days' + INTERVAL '60 minutes', 1800000,
     'https://video.example.com/tokyo_002_seg2.mp4', false, 0, 2),
    
    -- Datastreams for Osaka Urban Test (single segment - short drive)
    ('33333333-3333-3333-3333-333333333340', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222224', 
     'Osaka Urban Full', '/processed/camera/osaka_001.mp4', '/raw/camera/osaka_001.raw',
     1, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '45 minutes', 2700000,
     'https://video.example.com/osaka_001.mp4', false, 0, 2),
    
    -- Additional example with processing status variations
    ('33333333-3333-3333-3333-333333333341', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222226', 
     'California Highway Seg 1', '/processed/camera/cal_001_seg1.mp4', '/raw/camera/cal_001_seg1.raw',
     1, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '30 minutes', 1800000,
     'https://video.example.com/cal_001_seg1.mp4', false, 0, 2),
    
    -- Example with processing in progress
    ('33333333-3333-3333-3333-333333333342', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222226', 
     'California Highway Seg 2', '/processed/camera/cal_001_seg2.mp4', '/raw/camera/cal_001_seg2.raw',
     2, NOW() - INTERVAL '2 days' + INTERVAL '30 minutes', NOW() - INTERVAL '2 days' + INTERVAL '60 minutes', 1800000,
     'https://video.example.com/cal_001_seg2.mp4', false, 0, 1),  -- Status: PROCESSING
    
    -- Example with failed processing
    ('33333333-3333-3333-3333-333333333343', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222228', 
     'Berlin Autobahn Segment', '/processed/camera/berlin_001.mp4', '/raw/camera/berlin_001.raw',
     1, NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours' + INTERVAL '30 minutes', 1800000,
     NULL, true, 120000, 3),  -- Status: FAILED, with data loss
    
    -- Example pending processing
    ('33333333-3333-3333-3333-333333333344', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     0, '22222222-2222-2222-2222-222222222227', 
     'SF City Drive', '/processed/camera/sf_001.mp4', '/raw/camera/sf_001.raw',
     1, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '40 minutes', 2400000,
     NULL, false, 0, 0)  -- Status: PENDING
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 4. SCENE TEST DATA
-- =====================================================
-- Insert sample scenes within existing datastreams
INSERT INTO scene (id, created_at, updated_at, name, type, state, datastream_id, start_idx, end_idx, data_path)
VALUES
    -- Scenes within Tokyo Highway Segment 1
    ('88888888-8888-8888-8888-888888888801', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Crosswalk', 0, 0, '33333333-3333-3333-3333-333333333331', 100, 250, '/scenes/tokyo_001_seg1/crosswalk.json'),
    ('88888888-8888-8888-8888-888888888802', EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Traffic Light Red', 1, 0, '33333333-3333-3333-3333-333333333331', 400, 450, '/scenes/tokyo_001_seg1/traffic_light_red.json'),

    -- Scenes within Tokyo City Segment 1
    ('88888888-8888-8888-8888-888888888803', EXTRACT(EPOCH FROM NOW() - INTERVAL '6 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Pedestrian', 2, 1, '33333333-3333-3333-3333-333333333337', 50, 70, '/scenes/tokyo_002_seg1/pedestrian.json'),

    -- Scene within Osaka Urban Full
    ('88888888-8888-8888-8888-888888888804', EXTRACT(EPOCH FROM NOW() - INTERVAL '4 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Construction', 3, 2, '33333333-3333-3333-3333-333333333340', 700, 900, '/scenes/osaka_001/construction.json')
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
-- 5. PIPELINEDATA TEST DATA
-- =====================================================
INSERT INTO pipelinedata (id, created_at, updated_at, name, type, datastream_id, scene_id, source, data_path, params)
VALUES
    -- Raw data entries
    ('55555555-5555-5555-5555-555555555501', EXTRACT(EPOCH FROM NOW() - INTERVAL '30 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Raw Camera Data Batch 001', 0, '33333333-3333-3333-3333-333333333331', NULL, 
     'vehicle_001_camera', '/data/raw/camera/batch_001/', 
     '{"format": "h264", "resolution": "1920x1080", "fps": 30}'),
    
    ('55555555-5555-5555-5555-555555555502', EXTRACT(EPOCH FROM NOW() - INTERVAL '29 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Raw LiDAR Data Batch 001', 0, '33333333-3333-3333-3333-333333333332', NULL,
     'vehicle_001_lidar', '/data/raw/lidar/batch_001/',
     '{"point_cloud_format": "pcd", "points_per_second": 700000}'),
    
    -- Processed data entries
    ('55555555-5555-5555-5555-555555555503', EXTRACT(EPOCH FROM NOW() - INTERVAL '28 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Processed Camera Features', 1, '33333333-3333-3333-3333-333333333331', NULL,
     'feature_extraction_v2', '/data/processed/features/camera_001/',
     '{"feature_type": "semantic_segmentation", "model": "deeplabv3"}'),
    
    ('55555555-5555-5555-5555-555555555504', EXTRACT(EPOCH FROM NOW() - INTERVAL '27 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Point Cloud Segmentation', 1, '33333333-3333-3333-3333-333333333332', NULL,
     'pointnet_processor', '/data/processed/pointcloud/segmented_001/',
     '{"segmentation_classes": 10, "downsampling_ratio": 0.5}'),
    
    -- Annotated data entries
    ('55555555-5555-5555-5555-555555555505', EXTRACT(EPOCH FROM NOW() - INTERVAL '25 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Annotated Traffic Signs', 2, '33333333-3333-3333-3333-333333333333', NULL,
     'annotation_team_alpha', '/data/annotated/traffic_signs/',
     '{"annotation_tool": "labelbox", "classes": ["stop", "yield", "speed_limit"]}'),
    
    -- Training data entries
    ('55555555-5555-5555-5555-555555555506', EXTRACT(EPOCH FROM NOW() - INTERVAL '20 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Object Detection Training Set', 4, NULL, NULL,
     'training_pipeline', '/data/training/object_detection_v3/',
     '{"dataset_size": 50000, "augmentation": true, "split": {"train": 0.8, "val": 0.2}}'),
    
    -- Test data entries
    ('55555555-5555-5555-5555-555555555507', EXTRACT(EPOCH FROM NOW() - INTERVAL '15 days')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     'Model Validation Dataset', 5, NULL, NULL,
     'validation_pipeline', '/data/test/validation_set_001/',
     '{"test_scenarios": ["urban", "highway", "rural"], "metrics": ["mAP", "IoU"]}')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 6. PIPELINESTATE TEST DATA (Jobs)
-- =====================================================
INSERT INTO pipelinestate (id, created_at, updated_at, pipeline_data_id, pipeline_id, input, output, state)
VALUES
    -- Completed jobs
    ('66666666-6666-6666-6666-666666666601', EXTRACT(EPOCH FROM NOW() - INTERVAL '25 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '24 days')::BIGINT,
     '55555555-5555-5555-5555-555555555501', '44444444-4444-4444-4444-444444444441',
     '{"source_path": "/data/raw/camera/batch_001/", "target_path": "/data/collection/"}',
     '{"files_processed": 150, "total_size": "45GB", "duration_seconds": 3600}', 2),
    
    ('66666666-6666-6666-6666-666666666602', EXTRACT(EPOCH FROM NOW() - INTERVAL '24 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '23 days')::BIGINT,
     '55555555-5555-5555-5555-555555555502', '44444444-4444-4444-4444-444444444441',
     '{"source_path": "/data/raw/lidar/batch_001/", "target_path": "/data/collection/"}',
     '{"files_processed": 100, "total_size": "120GB", "duration_seconds": 5400}', 2),
    
    -- Running jobs
    ('66666666-6666-6666-6666-666666666603', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '55555555-5555-5555-5555-555555555503', '44444444-4444-4444-4444-444444444442',
     '{"input_data": "/data/processed/features/camera_001/", "processing_params": {"batch_size": 32}}',
     '{"progress": 0.65, "estimated_completion": "2 hours"}', 1),
    
    -- Pending jobs
    ('66666666-6666-6666-6666-666666666604', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 hour')::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT,
     '55555555-5555-5555-5555-555555555504', '44444444-4444-4444-4444-444444444443',
     '{"validation_set": "/data/test/validation_set_001/", "model_path": "/models/latest/"}',
     '{}', 0),
    
    -- Failed jobs
    ('66666666-6666-6666-6666-666666666605', EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '5 days')::BIGINT,
     '55555555-5555-5555-5555-555555555505', '44444444-4444-4444-4444-444444444444',
     '{"training_data": "/data/annotated/traffic_signs/", "model_config": "resnet50"}',
     '{"error": "Out of memory", "error_code": "OOM", "last_checkpoint": "epoch_15"}', 3),
    
    -- Jobs with dependencies (for testing pipelinedependency)
    ('66666666-6666-6666-6666-666666666606', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT,
     '55555555-5555-5555-5555-555555555506', '44444444-4444-4444-4444-444444444445',
     '{"input": "/data/training/object_detection_v3/", "epochs": 100}',
     '{"model_path": "/models/object_detection_v3.pt", "final_loss": 0.023}', 2),
    
    ('66666666-6666-6666-6666-666666666607', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT,
     '55555555-5555-5555-5555-555555555507', '44444444-4444-4444-4444-444444444446',
     '{"model": "/models/object_detection_v3.pt", "test_data": "/data/test/validation_set_001/"}',
     '{"mAP": 0.85, "inference_time_ms": 45, "false_positives": 12}', 2),
    
    -- Cancelled job
    ('66666666-6666-6666-6666-666666666608', EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '1 day')::BIGINT,
     '55555555-5555-5555-5555-555555555501', '44444444-4444-4444-4444-444444444447',
     '{"dataset": "/data/raw/camera/batch_001/", "target_format": "tfrecord"}',
     '{"cancelled_by": "admin", "reason": "Duplicate job"}', 4)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 7. PIPELINEDEPENDENCY TEST DATA
-- =====================================================
INSERT INTO pipelinedependency (id, created_at, updated_at, parent_id, child_id)
VALUES
    -- Training must complete before inference
    ('77777777-7777-7777-7777-777777777701', EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '3 days')::BIGINT,
     '66666666-6666-6666-6666-666666666606', '66666666-6666-6666-6666-666666666607'),
    
    -- Raw data collection must complete before processing
    ('77777777-7777-7777-7777-777777777702', EXTRACT(EPOCH FROM NOW() - INTERVAL '25 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '25 days')::BIGINT,
     '66666666-6666-6666-6666-666666666601', '66666666-6666-6666-6666-666666666603'),
    
    ('77777777-7777-7777-7777-777777777703', EXTRACT(EPOCH FROM NOW() - INTERVAL '24 days')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '24 days')::BIGINT,
     '66666666-6666-6666-6666-666666666602', '66666666-6666-6666-6666-666666666604'),
    
    -- Multiple dependencies - both camera and lidar processing must complete before validation
    ('77777777-7777-7777-7777-777777777704', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')::BIGINT, EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')::BIGINT,
     '66666666-6666-6666-6666-666666666603', '66666666-6666-6666-6666-666666666604')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 8. VERIFICATION QUERIES
-- =====================================================
-- Run these queries to verify the test data was inserted correctly

-- Check record counts
DO $$
DECLARE
    vehicle_count INTEGER;
    driver_count INTEGER;
    measurement_count INTEGER;
    datastream_count INTEGER;
    scene_count INTEGER;
    pipeline_count INTEGER;
    pipelinedata_count INTEGER;
    pipelinestate_count INTEGER;
    pipelinedependency_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO vehicle_count FROM vehicle WHERE name LIKE 'TEST-%';
    SELECT COUNT(*) INTO driver_count FROM driver;
    SELECT COUNT(*) INTO measurement_count FROM measurement;
    SELECT COUNT(*) INTO datastream_count FROM datastream;
    SELECT COUNT(*) INTO scene_count FROM scene;
    SELECT COUNT(*) INTO pipeline_count FROM pipeline;
    SELECT COUNT(*) INTO pipelinedata_count FROM pipelinedata;
    SELECT COUNT(*) INTO pipelinestate_count FROM pipelinestate;
    SELECT COUNT(*) INTO pipelinedependency_count FROM pipelinedependency;
    
    RAISE NOTICE 'Test data insertion complete:';
    RAISE NOTICE '  Vehicles: % records', vehicle_count;
    RAISE NOTICE '  Drivers: % records', driver_count;
    RAISE NOTICE '  Measurements: % records', measurement_count;
    RAISE NOTICE '  Datastreams: % records', datastream_count;
    RAISE NOTICE '  Scenes: % records', scene_count;
    RAISE NOTICE '  Pipelines: % records', pipeline_count;
    RAISE NOTICE '  Pipeline Data: % records', pipelinedata_count;
    RAISE NOTICE '  Pipeline States (Jobs): % records', pipelinestate_count;
    RAISE NOTICE '  Pipeline Dependencies: % records', pipelinedependency_count;
END $$;

-- =====================================================
-- End of Test Data Script
-- =====================================================
