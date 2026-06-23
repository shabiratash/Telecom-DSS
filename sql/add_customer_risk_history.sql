-- ============================================================
-- Add customer_risk_history table to existing database
-- Run this to add the new table without dropping existing data
-- ============================================================

USE telecom_churn_db;

-- ----------------------------------------------------------
-- Table: customer_risk_history
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS customer_risk_history (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT          NOT NULL,
    risk_score    FLOAT        NOT NULL,
    recorded_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_risk_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_risk_customer (customer_id),
    INDEX idx_risk_recorded (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
