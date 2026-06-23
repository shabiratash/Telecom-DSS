-- ============================================================
-- Afghanistan Telecom Churn Prediction and Retention System
-- MySQL schema for database: telecom_churn_db
-- ============================================================

CREATE DATABASE IF NOT EXISTS telecom_churn_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE telecom_churn_db;

-- ----------------------------------------------------------
-- Table: provinces  (One province has many customers)
-- ----------------------------------------------------------
DROP TABLE IF EXISTS recommendation_log;
DROP TABLE IF EXISTS prediction_log;
DROP TABLE IF EXISTS customer_risk_history;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS provinces;

CREATE TABLE provinces (
    province_id    INT AUTO_INCREMENT PRIMARY KEY,
    province_name  VARCHAR(100) NOT NULL UNIQUE,
    security_level VARCHAR(20)  NOT NULL DEFAULT 'Medium'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- Table: customers
-- ----------------------------------------------------------
CREATE TABLE customers (
    customer_id               INT AUTO_INCREMENT PRIMARY KEY,
    age                       INT          NOT NULL,
    gender                    VARCHAR(10)  NOT NULL,
    province_id               INT          NOT NULL,
    area_type                 VARCHAR(20)  NOT NULL DEFAULT 'Urban',
    network_quality           VARCHAR(20)  NOT NULL DEFAULT 'Good',
    internet_type             VARCHAR(20)  NOT NULL DEFAULT '4G',
    call_drop_rate            FLOAT        NOT NULL DEFAULT 0,
    recharge_amount           FLOAT        NOT NULL DEFAULT 0,
    recharge_frequency        INT          NOT NULL DEFAULT 0,
    payment_method            VARCHAR(20)  NOT NULL DEFAULT 'Cash',
    tenure_months             INT          NOT NULL DEFAULT 0,
    inactive_days             INT          NOT NULL DEFAULT 0,
    complaint_count           INT          NOT NULL DEFAULT 0,
    tower_availability        VARCHAR(20)  NOT NULL DEFAULT 'High',
    competitor_offer_exposure VARCHAR(10)  NOT NULL DEFAULT 'No',
    discount_usage            VARCHAR(10)  NOT NULL DEFAULT 'No',
    churn                     TINYINT      NOT NULL DEFAULT 0,
    CONSTRAINT fk_customer_province
        FOREIGN KEY (province_id) REFERENCES provinces(province_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_customers_province (province_id),
    INDEX idx_customers_churn (churn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- Table: customer_risk_history
-- ----------------------------------------------------------
CREATE TABLE customer_risk_history (
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

-- ----------------------------------------------------------
-- Table: prediction_log  (audit trail of every prediction)
-- ----------------------------------------------------------
CREATE TABLE prediction_log (
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
CREATE TABLE recommendation_log (
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
