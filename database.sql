CREATE TABLE employees (
    employee_id int NOT NULL AUTO_INCREMENT,
    first_name varchar(30),
    last_name varchar(30),
    username varchar(20),
    password varchar(128),
    PRIMARY KEY (employee_id)
);

CREATE TABLE leaves (
    leave_id int NOT NULL AUTO_INCREMENT,
    employee_id int NOT NULL,
    leave_reason varchar(1000),
    leave_date date,
    PRIMARY KEY (leave_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);