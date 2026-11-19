CREATE DATABASE IF NOT EXISTS sancugap
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sancugap;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role ENUM('admin', 'user') DEFAULT 'user',
    PRIMARY KEY (id),
    UNIQUE KEY ix_users_username (username),
    UNIQUE KEY ix_users_email (email)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS incidence_types (
    id INT NOT NULL AUTO_INCREMENT,
    slug VARCHAR(100) NOT NULL,
    description VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY ix_incidence_types_slug (slug)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS incidence_sub_types (
    id INT NOT NULL AUTO_INCREMENT,
    type_id INT NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    KEY ix_incidence_sub_types_type_id (type_id),
    CONSTRAINT fk_incidence_sub_types_type
        FOREIGN KEY (type_id) REFERENCES incidence_types (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS incidences (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    type_id INT NOT NULL,
    sub_type_id INT NULL,
    coordinate POINT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_incidences_user_id (user_id),
    KEY ix_incidences_type_id (type_id),
    KEY ix_incidences_sub_type_id (sub_type_id),
    CONSTRAINT fk_incidences_user
        FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_incidences_type
        FOREIGN KEY (type_id) REFERENCES incidence_types (id),
    CONSTRAINT fk_incidences_sub_type
        FOREIGN KEY (sub_type_id) REFERENCES incidence_sub_types (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
