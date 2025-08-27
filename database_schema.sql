-- Version 2 schema for FMEA‑CP‑OI Analysis Platform
-- This schema normalises FMEA and Control Plan records into dedicated
-- tables rather than storing the entire row in a JSON blob.  It
-- retains the existing `fmcp_documents` table for uploaded file
-- metadata and the `fmcp_associations` table for linking FMEA and CP
-- items.

-- Use the target database before running these statements (e.g. USE A060;)

-- Table to store metadata of uploaded documents (unchanged from v1)
CREATE TABLE IF NOT EXISTS `fmcp_documents` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `file_name` VARCHAR(255) NOT NULL,
  `document_type` ENUM('FMEA', 'CP', 'OI') NOT NULL,
  `version` VARCHAR(50) DEFAULT '1.0',
  `uploaded_by` VARCHAR(100) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store header information for FMEA documents.  These fields
-- correspond to the preamble (rows 0–6) in the FMEA workbook.  When
-- uploading a new FMEA the user should supply values for these
-- columns via the UI.
CREATE TABLE IF NOT EXISTS `fmcp_fmea_header` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL,
  `company_name` VARCHAR(255) DEFAULT NULL,
  `customer_name` VARCHAR(255) DEFAULT NULL,
  `model_year_platform` VARCHAR(255) DEFAULT NULL,
  `plant_location` VARCHAR(255) DEFAULT NULL,
  `subject` VARCHAR(255) DEFAULT NULL,
  `pfmea_start_date` DATE DEFAULT NULL,
  `pfmea_revision_date` DATE DEFAULT NULL,
  `pfmea_id` VARCHAR(50) DEFAULT NULL,
  `process_responsibility` VARCHAR(255) DEFAULT NULL,
  `cross_functional_team` VARCHAR(255) DEFAULT NULL,
  `confidentiality_level` VARCHAR(100) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`document_id`) REFERENCES `fmcp_documents`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store individual FMEA items parsed from the 00 sheet.  Each
-- record corresponds to a single failure mode and its associated
-- attributes.
CREATE TABLE IF NOT EXISTS `fmcp_fmea_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL,
  `row_index` INT COMMENT 'Original row number from the source file for reference',
  `process_step` TEXT,
  `failure_mode` TEXT,
  `failure_cause` TEXT,
  `detection_controls` TEXT,
  `severity` TINYINT,
  `occurrence` TINYINT,
  `detection` TINYINT,
  `ap` ENUM('H','M','L') COMMENT 'Action Priority',
  `issue_no` TEXT,
  `history_change_authorization` TEXT,
  `process_item` TEXT,
  `process_work_element` TEXT,
  `function_of_process_item` TEXT,
  `function_of_process_step_and_product_characteristic` TEXT,
  `function_of_process_work_element_and_process_characteristic` TEXT,
  `failure_effects_description` TEXT,
  `prevention_controls_description` TEXT,
  `special_characteristics` TEXT,
  `filter_code` TEXT,
  `prevention_action` TEXT,
  `detection_action` TEXT,
  `responsible_person_name` TEXT,
  `target_completion_date` TEXT,
  `status` TEXT,
  `action_taken` TEXT,
  `completion_date` TEXT,
  `severity_opt` TINYINT,
  `occurrence_opt` TINYINT,
  `detection_opt` TINYINT,
  `ap_opt` ENUM('H','M','L'),
  `remarks` TEXT,
  `special_characteristics_opt` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`document_id`) REFERENCES `fmcp_documents`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store Failure Effect (FE) options from the LIST sheet of an FMEA file.
CREATE TABLE IF NOT EXISTS `fmcp_fmea_fe_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL,
  `failure_effect` TEXT,
  `severity` TINYINT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`document_id`) REFERENCES `fmcp_documents`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store individual Control Plan items parsed from the REV.04
-- sheet.  Each record corresponds to a single characteristic and its
-- monitoring plan.
CREATE TABLE IF NOT EXISTS `fmcp_cp_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL,
  `row_index` INT COMMENT 'Original row number from the source file for reference',
  `process_name` TEXT,
  `product_characteristic` TEXT,
  `process_characteristic` TEXT,
  `evaluation_technique` TEXT,
  `control_method` TEXT,
  `spec_tolerance` TEXT,
  `sample_size` VARCHAR(50),
  `sample_freq` VARCHAR(50),
  `special_character_class` VARCHAR(100),
  `equipment` TEXT,
  `reaction_plan` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`document_id`) REFERENCES `fmcp_documents`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store associations between FMEA items and CP items (unchanged)
CREATE TABLE IF NOT EXISTS `fmcp_associations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `fmea_item_id` INT NOT NULL,
  `cp_item_id` INT NOT NULL,
  `created_by` VARCHAR(100) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_association` (`fmea_item_id`, `cp_item_id`),
  FOREIGN KEY (`fmea_item_id`) REFERENCES `fmcp_fmea_items`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`cp_item_id`) REFERENCES `fmcp_cp_items`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for user authentication and authorization
CREATE TABLE IF NOT EXISTS `fmcp_users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(100) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `role` VARCHAR(50) DEFAULT 'editor',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;