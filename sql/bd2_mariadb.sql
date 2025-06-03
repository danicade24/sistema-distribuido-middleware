CREATE TABLE IF NOT EXISTS personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(8) UNIQUE NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    apellidos VARCHAR(30) NOT NULL,
    lugar_nacimiento VARCHAR(30) NOT NULL,
    ubigeo VARCHAR(6) NOT NULL,
    direccion VARCHAR(50) NOT NULL
);

INSERT INTO personas (dni,nombre,apellidos,lugar_nacimiento,ubigeo,direccion) VALUES
('78542139','Laura','Pérez Díaz','Lima','150101','Av. Siempre Viva 123'),
('12345678','Pedro','Ramírez Soto','Cusco','080101','Jr. Los Andes 567'),
('33445566','Carla','Valverde Núñez','Tacna','230101','Av. Gregorio Albarracín 210'),
('22334455','Andrés','Mendoza Farfán','Iquitos','160101','Av. La Marina 320'),
('11223344','María','Lopez Huamán','Huancayo','120101','Psje. Los Eucaliptos 102'),
('77889900','José','Cáceres Medina','Lima','210101','Urb. Santa Rosa Mz C Lt 5'),
('44556677','Natalia','Reyes Cárdenas','Moquegua','180101','Urb. Los Jardines 302'),
('11002233','Diego','Zevallos Paredes','Cajamarca','060101','Calle San José 15'),
('55667788','Jorge','Sánchez Ríos','Chiclayo','140101','Jr. San Martín 87'),
('99001122','Camila','Oré Gutiérrez','Tumbes','240101','Av. Grau 65');