-- Active: 1768781977508@@127.0.0.1@3306@seoul_urban_lab
-- 1. 데이터베이스 생성 (이미 있으면 생략)
CREATE DATABASE IF NOT EXISTS seoul_urban_lab 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE seoul_urban_lab;

-- 2. 테이블 생성
-- 요청하신 9개 컬럼 + 관리용 id, 등록일자 포함

CREATE TABLE IF NOT EXISTS subway_traffic_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 식별자',
    UserGroup VARCHAR(50) NOT NULL COMMENT '파생변수: 일반, 학생/청소년, 노인/약자, 기타',
    pasngDe VARCHAR(20) NOT NULL COMMENT '통행일자 (YYYYMMDD)',
    pasngHr INT NOT NULL COMMENT '통행시간 (0~23)',
    lineNm VARCHAR(50) NOT NULL COMMENT '호선명',
    stnCd VARCHAR(20) NOT NULL COMMENT '역코드',
    stnNm VARCHAR(50) NOT NULL COMMENT '역명',
    trnscdUserSeCd VARCHAR(10) NOT NULL COMMENT '사용자 구분 코드 (예: 01, 100)',
    rideNope INT DEFAULT 0 COMMENT '승차인원',
    gffNope INT DEFAULT 0 COMMENT '하차인원',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 적재 시각',
    UNIQUE KEY uk_subway_log (pasngDe, pasngHr, stnCd, trnscdUserSeCd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='서울교통공사 원본 유지 테이블';

