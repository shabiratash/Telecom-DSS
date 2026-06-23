-- ============================================================
-- Additive migration: prediction_log + recommendation_log
-- Safe to run on an existing database. Does NOT drop or alter
-- any existing tables. Backward compatible.
-- ============================================================

USE telecom_churn_db;

-- ----------------------------------------------------------
-- Table: prediction_log  (audit trail of every prediction)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediction_log (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    customer_id       INT          NULL,
    churn_probability FLOAT        NOT NULL,
    prediction        INT          NOT NULL DEFAULT 0,
    prediction_label  VARCHAR(40)  NULL,
    risk_level        VARCHAR(20)  NULL,
    health_score      INT          NULL,
    source            VARCHAR(30)  NOT NULL DEFAULT 'single',
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_predlog_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_predlog_customer (customer_id),
    INDEX idx_predlog_source (source),
    INDEX idx_predlog_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- Table: recommendation_log  (audit trail of every recommendation)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendation_log (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT          NULL,
    prediction_id INT          NULL,
    title         VARCHAR(120) NOT NULL,
    action        TEXT         NULL,
    severity      VARCHAR(20)  NULL,
    icon          VARCHAR(40)  NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reclog_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_reclog_prediction
        FOREIGN KEY (prediction_id) REFERENCES prediction_log(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_reclog_customer (customer_id),
    INDEX idx_reclog_prediction (prediction_id),
    INDEX idx_reclog_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
