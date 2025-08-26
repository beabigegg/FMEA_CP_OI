-- SQL Schema for FMEA-CP-OI Analysis Platform
-- Target Database: A060
-- All tables are prefixed with 'fmcp_' to avoid conflicts.

-- Make sure we are using the correct database.
-- USE A060;

-- Table to store metadata of uploaded documents
CREATE TABLE IF NOT EXISTS `fmcp_documents` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `file_name` VARCHAR(255) NOT NULL,
  `document_type` ENUM('FMEA', 'CP', 'OI') NOT NULL,
  `version` VARCHAR(50) DEFAULT '1.0',
  `uploaded_by` VARCHAR(100) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store individual items parsed from documents (e.g., a single failure mode row)
CREATE TABLE IF NOT EXISTS `fmcp_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL,
  `row_index` INT COMMENT 'Original row number from the source file for reference',
  `content` JSON NOT NULL COMMENT 'Stores the structured data of the row, e.g., {
"failure_mode": "...", "failure_cause": "..."}',
  `edited_by` VARCHAR(100),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`document_id`) REFERENCES `fmcp_documents`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store the associations between FMEA items and CP items
CREATE TABLE IF NOT EXISTS `fmcp_associations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `fmea_item_id` INT NOT NULL,
  `cp_item_id` INT NOT NULL,
  `created_by` VARCHAR(100) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_association` (`fmea_item_id`, `cp_item_id`), -- Prevent duplicate links
  FOREIGN KEY (`fmea_item_id`) REFERENCES `fmcp_items`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`cp_item_id`) REFERENCES `fmcp_items`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

