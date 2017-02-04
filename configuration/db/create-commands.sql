CREATE TABLE tbldepartments (
    department_id SERIAL PRIMARY KEY,
    department_name character varying(50) NOT NULL
);


CREATE TABLE tblusers (
    user_id SERIAL PRIMARY KEY,
    user_firstname character varying(50) NOT NULL,
    user_surname character varying(50) NOT NULL,
    user_active smallint DEFAULT 1 NOT NULL,
    user_email character varying(70),
    user_extension character varying(20) NOT NULL,
    user_department_id integer REFERENCES tbldepartments
);


CREATE TABLE tblcallhistory (
    ch_call_id SERIAL PRIMARY KEY,
    ch_user_id integer REFERENCES tblusers,
    ch_calling_number character varying(128) NOT NULL,
    ch_called_number character varying(128) NOT NULL,
    ch_direction smallint NOT NULL,
    ch_internal_external smallint NOT NULL,
    ch_start_time timestamp without time zone NOT NULL,
    ch_end_time timestamp without time zone NOT NULL,
    ch_talk_time_seconds integer NOT NULL
);
