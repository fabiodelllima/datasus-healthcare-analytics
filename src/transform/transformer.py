"""
Transform: Limpeza, validação e enriquecimento de dados
"""

import logging
from typing import cast

import pandas as pd

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforma dados brutos do DataSUS"""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica pipeline de transformação

        Args:
            df: DataFrame bruto

        Returns:
            DataFrame processado
        """
        try:
            logger.info(f"[TRANSFORM] Iniciado: {len(df):,} registros")

            # 1. Conversão de tipos
            df = self._convert_types(df)

            # 2. Limpeza
            df = self._clean_data(df)

            # 3. Validações
            df = self._validate_data(df)

            # 4. Enriquecimento
            df = self._enrich_data(df)

            logger.info(f"[TRANSFORM] Concluído: {len(df):,} registros")

            return df

        except Exception as e:
            logger.error(f"[TRANSFORM] Erro: {e}")
            raise

    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converte tipos de dados"""
        logger.info("[CONVERT] Convertendo tipos...")

        # Campos numéricos
        numeric_fields = ["IDADE", "VAL_TOT", "VAL_UTI", "VAL_SH", "VAL_SP", "VAL_SADT"]
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors="coerce")

        # Campos de data
        date_fields = ["DT_INTER", "DT_SAIDA"]
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], format="%Y%m%d", errors="coerce")

        logger.info("[CONVERT] Tipos convertidos")
        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicatas e dados inválidos"""
        logger.info("[CLEAN] Iniciando limpeza...")

        initial_count = len(df)

        # Remove duplicatas completas
        df = df.drop_duplicates()
        logger.info(f"[CLEAN] Duplicatas removidas: {initial_count - len(df)}")

        # Remove registros com campos críticos nulos
        critical_fields = ["N_AIH", "DT_INTER", "DT_SAIDA"]
        df = df.dropna(subset=critical_fields)
        logger.info(f"[CLEAN] Registros válidos: {len(df):,}")

        return df

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida tipos e ranges de dados"""
        logger.info("[VALIDATE] Iniciando validações...")

        initial_count = len(df)

        # Validar datas (DT_INTER <= DT_SAIDA)
        if "DT_INTER" in df.columns and "DT_SAIDA" in df.columns:
            df = cast(pd.DataFrame, df[df["DT_INTER"] <= df["DT_SAIDA"]])

        # Validar idade (0-120)
        if "IDADE" in df.columns:
            df = cast(pd.DataFrame, df[(df["IDADE"] >= 0) & (df["IDADE"] <= 120)])

        # Validar valores monetários (>= 0)
        value_cols = ["VAL_TOT", "VAL_UTI", "VAL_SH", "VAL_SP", "VAL_SADT"]
        for col in value_cols:
            if col in df.columns:
                df = cast(pd.DataFrame, df[df[col] >= 0])

        removed = initial_count - len(df)
        logger.info(f"[VALIDATE] Registros inválidos removidos: {removed}")
        logger.info(f"[VALIDATE] Taxa validação: {(len(df) / initial_count) * 100:.2f}%")

        return df

    def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona campos calculados"""
        logger.info("[ENRICH] Iniciando enriquecimento...")

        # Calcular tempo de permanência (dias)
        if "DT_INTER" in df.columns and "DT_SAIDA" in df.columns:
            df["stay_days"] = (df["DT_SAIDA"] - df["DT_INTER"]).dt.days  # type: ignore[attr-defined]

        # Calcular custo por dia
        if "VAL_TOT" in df.columns and "stay_days" in df.columns:
            df["daily_cost"] = df["VAL_TOT"] / df["stay_days"].replace(0, 1)

        # Criar faixa etária
        if "IDADE" in df.columns:
            df["age_group"] = pd.cut(
                df["IDADE"],
                bins=[0, 18, 30, 45, 60, 120],
                labels=["0-17", "18-29", "30-44", "45-59", "60+"],
            )

        # Flag óbito
        if "MORTE" in df.columns:
            df["death"] = df["MORTE"] == 1

        # Especialidade (simplificado - requer tabela SIGTAP)
        if "ESPEC" in df.columns:
            df["specialty_name"] = df["ESPEC"].astype(str)

        logger.info(
            "[ENRICH] Campos adicionados: stay_days, daily_cost, age_group, death, specialty_name"
        )

        return df
