"""
Transform: Limpeza, validação e enriquecimento de dados
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Pipeline de transformação ETL para dados SIH/DataSUS.

    USO NORMAL:
        Use transform() para processamento completo e automático.

    USO AVANÇADO:
        Use métodos individuais para:
        - Debug granular de etapas
        - Pipelines customizados
        - Análise exploratória
        - Testes unitários específicos

    EXEMPLO NORMAL:
        >>> transformer = DataTransformer()
        >>> df_clean = transformer.transform(df_raw)

    EXEMPLO AVANÇADO:
        >>> df = transformer.convert_types(df_raw)
        >>> print(f"Registros após conversão: {len(df)}")
        >>> df = transformer.clean_data(df)
        >>> print(f"Registros após limpeza: {len(df)}")
    """

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline ETL completo (USE ESTE MÉTODO NA MAIORIA DOS CASOS).

        Executa 4 etapas sequencialmente:
        1. convert_types: String → tipos corretos
        2. clean_data: Remove duplicatas e nulos
        3. validate_data: Valida regras de negócio
        4. enrich_data: Adiciona campos calculados

        Args:
            df: DataFrame bruto extraído do DataSUS

        Returns:
            DataFrame transformado e validado
        """
        try:
            logger.info(f"[TRANSFORM] Iniciado: {len(df):,} registros")

            # 1. Conversão de tipos
            df = self.convert_types(df)

            # 2. Limpeza
            df = self.clean_data(df)

            # 3. Validações
            df = self.validate_data(df)

            # 4. Enriquecimento
            df = self.enrich_data(df)

            logger.info(f"[TRANSFORM] Concluído: {len(df):,} registros")

            return df

        except Exception as e:
            logger.error(f"[TRANSFORM] Erro: {e}")
            raise

    def convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Etapa 1: Converte tipos de dados.

        USO AVANÇADO: Para pipeline customizado ou debug.
        USO NORMAL: Chamado automaticamente por transform().

        Conversões:
        - Numéricos: String → int64/float64
        - Datas: YYYYMMDD (str) → datetime64

        Args:
            df: DataFrame com tipos originais (strings)

        Returns:
            DataFrame com tipos corretos
        """
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

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida tipos e ranges de dados"""
        logger.info("[VALIDATE] Iniciando validações...")

        initial_count = len(df)

        # Validar datas (DT_INTER <= DT_SAIDA)
        if "DT_INTER" in df.columns and "DT_SAIDA" in df.columns:
            df = df[df["DT_INTER"] <= df["DT_SAIDA"]]

        # Validar idade (0-120)
        if "IDADE" in df.columns:
            df = df[(df["IDADE"] >= 0) & (df["IDADE"] <= 120)]

        # Validar valores monetários (>= 0)
        value_cols = ["VAL_TOT", "VAL_UTI", "VAL_SH", "VAL_SP", "VAL_SADT"]
        for col in value_cols:
            if col in df.columns:
                df = df[df[col] >= 0]

        removed = initial_count - len(df)
        logger.info(f"[VALIDATE] Registros inválidos removidos: {removed}")
        logger.info(f"[VALIDATE] Taxa validação: {(len(df) / initial_count) * 100:.2f}%")

        return df

    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
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
