"""Contratos de datos: qué JSON acepta la API (validación con Pydantic)."""
from typing import Literal

from pydantic import BaseModel, Field


class EstudianteEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    carrera: str = Field(min_length=2, max_length=100)
    competencias: list[str] = Field(min_length=1)  # al menos una


class OfertaEntrada(BaseModel):
    titulo: str = Field(min_length=2, max_length=100)
    empresa: str = Field(min_length=2, max_length=100)
    requisitos_obligatorios: list[str] = Field(min_length=1)
    requisitos_deseables: list[str] = []


class CompatibilidadEntrada(BaseModel):
    estudiante_id: int
    oferta_id: int


class RecomendacionEntrada(BaseModel):
    resultado_id: int
    texto: str = Field(min_length=10, max_length=3000)
    modelo: str = "gemini"


class RevisionEntrada(BaseModel):
    estado: Literal["aprobada", "descartada"]


class ReporteEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=120)
    resumen: str = Field(min_length=3, max_length=3000)
    total_resultados: int = Field(ge=0)
    destacados: list[dict] = []
