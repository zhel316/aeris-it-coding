-- Seed data for the ordering system
-- Run AFTER the app has started once (to create tables):
--   sqlite3 orders.db < init.sql

PRAGMA foreign_keys = ON;

-- Tracking records (no foreign keys, insert first)
INSERT OR IGNORE INTO tracking (assigned_tracking, track_no, logistics_company) VALUES
    ('Track 1', '2FWZ50008569', 'StarTrack/Auspost'),
    ('Track 2', '2FWZ50008645', 'StarTrack/Auspost'),
    ('Track 3', '305506914',    'TNT');

-- Orders (no foreign keys)
INSERT OR IGNORE INTO orders (order_no, order_data, status, company_name, customer_name, phone, email, address) VALUES
    ('PO-20251130-00072', '2025-11-30', 'completed',  'V22 Dispensary',       'Jason Hu',   '0481 735 488', 'Jason@aerishealth.au', '125 Toorak Road, South Yarra VIC 3141'),
    ('PO-20251203-00046', '2025-12-03', 'in-transit', 'Cann Life Dispensary', 'Bella Dari', '0411 547 288', 'Bella@aerishealth.au', '381 Smith Street, Fitzroy VIC 3065');

-- SKUs (foreign keys → orders + tracking)
INSERT OR IGNORE INTO sku (sku_id, qty, assigned_tracking, order_no) VALUES
    ('TBAMET10',  3,  'Track 1', 'PO-20251130-00072'),
    ('TBAMET28',  1,  'Track 1', 'PO-20251130-00072'),
    ('TBOPAL28',  1,  'Track 1', 'PO-20251130-00072'),
    ('HARNIG',    4,  'Track 1', 'PO-20251130-00072'),
    ('LELCBD100', 6,  'Track 1', 'PO-20251130-00072'),
    ('AURPUR10',  10, 'Track 2', 'PO-20251203-00046'),
    ('HALGEO15',  1,  'Track 3', 'PO-20251203-00046'),
    ('MCMW10',    2,  'Track 3', 'PO-20251203-00046'),
    ('MCBO30',    3,  'Track 3', 'PO-20251203-00046');
