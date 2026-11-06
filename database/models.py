import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

os.makedirs("database", exist_ok=True)
engine = create_engine("sqlite:///database/f1manager.db")
Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    team_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    nationality = Column(String)

class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    driver_id = Column(String, unique=True, nullable=False)
    code = Column(String)
    permanent_number = Column(Integer)
    given_name = Column(String)
    family_name = Column(String)
    nationality = Column(String)
    date_of_birth = Column(String)

class Circuit(Base):
    __tablename__ = 'circuits'
    id = Column(Integer, primary_key=True)
    circuit_id = Column(String, unique=True, nullable=False)
    name = Column(String)
    locality = Column(String)
    country = Column(String)
    lat = Column(Float)
    lng = Column(Float)

class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    round = Column(Integer)
    race_name = Column(String)
    circuit_id = Column(String, ForeignKey('circuits.circuit_id'))
    date = Column(String)

class RaceResult(Base):
    __tablename__ = 'race_results'
    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    driver_id = Column(String, ForeignKey('drivers.driver_id'))
    team_id = Column(String, ForeignKey('teams.team_id'))
    position = Column(Integer)
    points = Column(Float)
    grid = Column(Integer)
    laps = Column(Integer)
    status = Column(String)

class DriverStanding(Base):
    __tablename__ = 'driver_standings'
    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    position = Column(Integer)
    driver_id = Column(String, ForeignKey('drivers.driver_id'))
    team_id = Column(String, ForeignKey('teams.team_id'))
    points = Column(Float)
    wins = Column(Integer)

class ConstructorStanding(Base):
    __tablename__ = 'constructor_standings'
    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    position = Column(Integer)
    team_id = Column(String, ForeignKey('teams.team_id'))
    points = Column(Float)
    wins = Column(Integer)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")