-- ================================================
-- Chin Hin - Dummy Data for Testing
-- Run after 001_initial_schema.sql
-- ================================================

-- ================================================
-- 1. USERS (10 employees)
-- ================================================
INSERT INTO users (id, email, full_name, department, role, phone) VALUES
    ('11111111-1111-1111-1111-111111111111'::UUID, 'ahmad@chinhin.com', 'Ahmad bin Hassan', 'Engineering', 'employee', '012-3456789'),
    ('22222222-2222-2222-2222-222222222222'::UUID, 'siti@chinhin.com', 'Siti Nurhaliza', 'HR', 'hr', '013-4567890'),
    ('33333333-3333-3333-3333-333333333333'::UUID, 'raj@chinhin.com', 'Raj Kumar', 'Finance', 'employee', '014-5678901'),
    ('44444444-4444-4444-4444-444444444444'::UUID, 'mei.ling@chinhin.com', 'Tan Mei Ling', 'Marketing', 'manager', '015-6789012'),
    ('55555555-5555-5555-5555-555555555555'::UUID, 'farid@chinhin.com', 'Farid Abdullah', 'Engineering', 'manager', '016-7890123'),
    ('66666666-6666-6666-6666-666666666666'::UUID, 'priya@chinhin.com', 'Priya Devi', 'HR', 'employee', '017-8901234'),
    ('77777777-7777-7777-7777-777777777777'::UUID, 'wei.chen@chinhin.com', 'Lee Wei Chen', 'Finance', 'employee', '018-9012345'),
    ('88888888-8888-8888-8888-888888888888'::UUID, 'aishah@chinhin.com', 'Aishah Zainal', 'Marketing', 'employee', '019-0123456'),
    ('99999999-9999-9999-9999-999999999999'::UUID, 'muthu@chinhin.com', 'Muthu Samy', 'Operations', 'employee', '011-1234567'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::UUID, 'admin@chinhin.com', 'System Admin', 'IT', 'admin', '010-9876543');

-- ================================================
-- 2. LEAVE TYPES
-- ================================================
INSERT INTO leave_types (name, description, default_days) VALUES
    ('Annual Leave', 'Cuti tahunan', 14),
    ('Medical Leave', 'MC - sakit', 14),
    ('Emergency Leave', 'Cuti kecemasan', 3),
    ('Compassionate Leave', 'Cuti ihsan (kematian, etc)', 3),
    ('Maternity Leave', 'Cuti bersalin', 60),
    ('Paternity Leave', 'Cuti bapa', 7);

-- ================================================
-- 3. LEAVE BALANCES (for 2026)
-- ================================================
INSERT INTO leave_balances (user_id, leave_type_id, year, total_days, used_days, pending_days)
SELECT 
    u.id,
    lt.id,
    2026,
    lt.default_days,
    FLOOR(RANDOM() * 5)::INTEGER,
    FLOOR(RANDOM() * 2)::INTEGER
FROM users u
CROSS JOIN leave_types lt
WHERE lt.name IN ('Annual Leave', 'Medical Leave', 'Emergency Leave');

-- ================================================
-- 4. SAMPLE LEAVE REQUESTS
-- ================================================
INSERT INTO leave_requests (user_id, leave_type_id, start_date, end_date, total_days, reason, status)
SELECT '11111111-1111-1111-1111-111111111111'::UUID, id, '2026-02-01'::DATE, '2026-02-03'::DATE, 3, 'Family vacation', 'approved'
FROM leave_types WHERE name = 'Annual Leave'
UNION ALL
SELECT '33333333-3333-3333-3333-333333333333'::UUID, id, '2026-01-20'::DATE, '2026-01-21'::DATE, 2, 'Demam dan batuk', 'approved'
FROM leave_types WHERE name = 'Medical Leave'
UNION ALL
SELECT '66666666-6666-6666-6666-666666666666'::UUID, id, '2026-03-10'::DATE, '2026-03-14'::DATE, 5, 'Balik kampung Raya', 'pending'
FROM leave_types WHERE name = 'Annual Leave'
UNION ALL
SELECT '88888888-8888-8888-8888-888888888888'::UUID, id, '2026-01-25'::DATE, '2026-01-25'::DATE, 1, 'Personal emergency', 'pending'
FROM leave_types WHERE name = 'Emergency Leave';

-- ================================================
-- 5. ROOMS
-- ================================================
INSERT INTO rooms (name, location, capacity, amenities) VALUES
    ('Boardroom A', 'Level 3', 20, ARRAY['projector', 'whiteboard', 'video_conference', 'tv']),
    ('Meeting Room B', 'Level 2', 8, ARRAY['whiteboard', 'tv']),
    ('Huddle Space 1', 'Level 1', 4, ARRAY['whiteboard']),
    ('Training Room', 'Level 3', 30, ARRAY['projector', 'whiteboard', 'microphone']),
    ('Creative Studio', 'Level 2', 10, ARRAY['whiteboard', 'tv', 'standing_desk']);

-- ================================================
-- 6. SAMPLE ROOM BOOKINGS
-- ================================================
INSERT INTO room_bookings (room_id, user_id, title, start_time, end_time, description)
SELECT r.id, '44444444-4444-4444-4444-444444444444'::UUID, 'Marketing Q1 Review', '2026-01-27 09:00:00+08'::TIMESTAMPTZ, '2026-01-27 11:00:00+08'::TIMESTAMPTZ, 'Quarterly marketing review'
FROM rooms r WHERE r.name = 'Boardroom A'
UNION ALL
SELECT r.id, '55555555-5555-5555-5555-555555555555'::UUID, 'Engineering Standup', '2026-01-26 10:00:00+08'::TIMESTAMPTZ, '2026-01-26 10:30:00+08'::TIMESTAMPTZ, 'Daily standup'
FROM rooms r WHERE r.name = 'Meeting Room B'
UNION ALL
SELECT r.id, '11111111-1111-1111-1111-111111111111'::UUID, '1-on-1 with Manager', '2026-01-28 14:00:00+08'::TIMESTAMPTZ, '2026-01-28 15:00:00+08'::TIMESTAMPTZ, NULL
FROM rooms r WHERE r.name = 'Huddle Space 1';

-- ================================================
-- 7. CLAIM CATEGORIES
-- ================================================
INSERT INTO claim_categories (name, description, max_amount) VALUES
    ('Transport', 'Petrol, toll, parking, grab', 500.00),
    ('Meals', 'Client meetings, team lunches', 200.00),
    ('Parking', 'Daily parking claims', 100.00),
    ('Office Supplies', 'Stationery, equipment', 300.00),
    ('Others', 'Miscellaneous claims', 500.00);

-- ================================================
-- 8. SAMPLE CLAIMS
-- ================================================
INSERT INTO claims (user_id, category_id, amount, description, claim_date, status)
SELECT '11111111-1111-1111-1111-111111111111'::UUID, id, 45.50, 'Grab ke client meeting Bangsar', '2026-01-20'::DATE, 'approved'
FROM claim_categories WHERE name = 'Transport'
UNION ALL
SELECT '33333333-3333-3333-3333-333333333333'::UUID, id, 120.00, 'Team lunch - 4 pax', '2026-01-22'::DATE, 'pending'
FROM claim_categories WHERE name = 'Meals'
UNION ALL
SELECT '77777777-7777-7777-7777-777777777777'::UUID, id, 15.00, 'KLCC parking 3 hours', '2026-01-23'::DATE, 'pending'
FROM claim_categories WHERE name = 'Parking'
UNION ALL
SELECT '88888888-8888-8888-8888-888888888888'::UUID, id, 89.00, 'Petrol claim - outstation Ipoh', '2026-01-24'::DATE, 'pending'
FROM claim_categories WHERE name = 'Transport';

-- ================================================
-- DONE! 🎉
-- ================================================
