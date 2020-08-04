create table PROCESS
(
    PRJ_ID     VARCHAR2(50) not null,
    WORK_ID    VARCHAR2(50) not null,
    STEP       VARCHAR2(50) not null,
    STATUS     VARCHAR2(50) not null,
    DATE_REQ   VARCHAR2(14) not null,
    DATE_START VARCHAR2(14),
    DATE_END   VARCHAR2(14),
    USER_ID    VARCHAR2(50) not null,
    HID_PNAME  VARCHAR2(50),
    constraint PROCESS_PK
        primary key (PRJ_ID, WORK_ID, STEP)
)
/

create table PARAMS
(
    PRJ_ID       VARCHAR2(50),
    WORK_ID      VARCHAR2(50),
    STEP         VARCHAR2(50),
    PARAM_OBJECT BLOB,
    constraint TABLE_NAME_PK
        unique (PRJ_ID, WORK_ID, STEP)
)
/

