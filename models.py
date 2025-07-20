from sqlalchemy import Column, String, Integer, Boolean, Date, Time, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Paciente(Base):
    __tablename__ = 'paciente'
    cedula = Column(String(10), primary_key=True)
    nombres = Column(String(100), nullable=False)
    correo = Column(String(100))
    telefono = Column(String(15))

    citas = relationship("Cita", back_populates="paciente")
    consultas = relationship("Consulta", back_populates="paciente")
    facturas = relationship("Factura", back_populates="paciente")


class Cita(Base):
    __tablename__ = 'cita'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    motivo = Column(Text)
    cedula_paciente = Column(String(10), ForeignKey('paciente.cedula'), nullable=False)
    agendada_por_medico = Column(Boolean, default=False)

    paciente = relationship("Paciente", back_populates="citas")
    consultas = relationship("Consulta", back_populates="cita")


class Consulta(Base):
    __tablename__ = 'consulta'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    diagnostico = Column(Text)
    tratamiento = Column(Text)
    observaciones = Column(Text)
    cedula_paciente = Column(String(10), ForeignKey('paciente.cedula'), nullable=False)
    cita_id = Column(Integer, ForeignKey('cita.id'))

    paciente = relationship("Paciente", back_populates="consultas")
    cita = relationship("Cita", back_populates="consultas")
    factura = relationship("Factura", back_populates="consulta", uselist=False)


class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)


class Factura(Base):
    __tablename__ = 'factura'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(Text)
    cedula_paciente = Column(String(10), ForeignKey('paciente.cedula'), nullable=False)
    consulta_id = Column(Integer, ForeignKey('consulta.id'))

    paciente = relationship("Paciente", back_populates="facturas")
    consulta = relationship("Consulta", back_populates="factura")
