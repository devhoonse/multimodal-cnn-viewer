-------------------------------------------------
-- 사용자 생성 : SYSTEM 계정으로 실행
-------------------------------------------------
-- 테이블스페이스 생성
CREATE TABLESPACE METAX
DATAFILE '/home/istream3/ora_tblspace/metax.dbf'
SIZE 1024M
AUTOEXTEND ON NEXT 10M ;

-- (필요시) 유저 삭제
DROP USER METAX ;

-- 유저 생성
CREATE USER METAX IDENTIFIED BY METAX1234
DEFAULT TABLESPACE METAX
QUOTA UNLIMITED ON METAX
TEMPORARY TABLESPACE TEMP ;

-- 권한
GRANT CREATE SESSION
    , CREATE VIEW
    , CREATE TABLE
    , CREATE SEQUENCE
    , CREATE PROCEDURE
TO METAX;