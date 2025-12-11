"""
Testes para DataTransformer seguindo especificações BDD
"""

import pandas as pd

from src.transform.transformer import DataTransformer


class TestConvertTypes:
    """
    FEATURE: Conversão de tipos de dados
    COMO: Sistema ETL
    QUERO: Converter strings para tipos corretos (numéricos, datas)
    """

    def test_convert_numeric_fields(self):
        """Deve converter campos numéricos de string para float/int"""
        df = pd.DataFrame({"IDADE": ["25", "30", "abc"], "VAL_TOT": ["1500.50", "2000.00", "xyz"]})

        transformer = DataTransformer()
        result = transformer.convert_types(df)

        assert pd.api.types.is_numeric_dtype(result["IDADE"])
        assert pd.api.types.is_numeric_dtype(result["VAL_TOT"])
        assert result["VAL_TOT"].iloc[0] == 1500.50

    def test_convert_date_fields(self):
        """Deve converter datas de YYYYMMDD string para datetime64"""
        df = pd.DataFrame(
            {"DT_INTER": ["20240101", "20240115"], "DT_SAIDA": ["20240105", "20240120"]}
        )

        transformer = DataTransformer()
        result = transformer.convert_types(df)

        assert pd.api.types.is_datetime64_any_dtype(result["DT_INTER"])
        assert pd.api.types.is_datetime64_any_dtype(result["DT_SAIDA"])

    def test_handle_invalid_numeric_values(self):
        """Deve converter valores inválidos em NaN com errors='coerce'"""
        df = pd.DataFrame({"IDADE": ["25", "abc", "30"]})

        transformer = DataTransformer()
        result = transformer.convert_types(df)

        assert pd.isna(result["IDADE"].iloc[1])


class TestCleanData:
    """
    FEATURE: Limpeza de dados
    COMO: Sistema ETL
    QUERO: Remover duplicatas e registros com campos críticos nulos
    """

    def test_remove_duplicates(self):
        """Deve remover registros duplicados completos"""
        df = pd.DataFrame(
            {
                "N_AIH": ["123", "123", "456"],
                "DT_INTER": ["20240101", "20240101", "20240102"],
                "DT_SAIDA": ["20240105", "20240105", "20240106"],
            }
        )

        transformer = DataTransformer()
        result = transformer.clean_data(df)

        assert len(result) == 2
        assert list(result["N_AIH"]) == ["123", "456"]

    def test_remove_null_critical_fields(self):
        """Deve remover registros com nulos em campos críticos"""
        df = pd.DataFrame(
            {
                "N_AIH": ["123", None, "456"],
                "DT_INTER": ["20240101", "20240102", "20240103"],
                "DT_SAIDA": ["20240105", "20240106", None],
            }
        )

        transformer = DataTransformer()
        result = transformer.clean_data(df)

        assert len(result) == 1
        assert result["N_AIH"].iloc[0] == "123"


class TestValidateData:
    """
    FEATURE: Validação de regras de negócio
    COMO: Sistema ETL
    QUERO: Garantir dados dentro de ranges válidos
    """

    def test_reject_invalid_date_logic(self):
        """Deve rejeitar DT_SAIDA < DT_INTER"""
        df = pd.DataFrame(
            {
                "DT_INTER": pd.to_datetime(["2024-01-20", "2024-01-10"]),
                "DT_SAIDA": pd.to_datetime(["2024-01-15", "2024-01-15"]),
            }
        )

        transformer = DataTransformer()
        result = transformer.validate_data(df)

        assert len(result) == 1
        assert result["DT_INTER"].iloc[0] == pd.Timestamp("2024-01-10")

    def test_reject_negative_age(self):
        """Deve rejeitar IDADE < 0"""
        df = pd.DataFrame({"IDADE": [-5.0, 25.0, 30.0]})

        transformer = DataTransformer()
        result = transformer.validate_data(df)

        assert len(result) == 2
        assert -5.0 not in result["IDADE"].values

    def test_reject_age_above_120(self):
        """Deve rejeitar IDADE > 120"""
        df = pd.DataFrame({"IDADE": [25.0, 150.0, 30.0]})

        transformer = DataTransformer()
        result = transformer.validate_data(df)

        assert len(result) == 2
        assert 150.0 not in result["IDADE"].values

    def test_reject_negative_monetary_values(self):
        """Deve rejeitar VAL_TOT < 0"""
        df = pd.DataFrame({"VAL_TOT": [100.0, -50.0, 200.0]})

        transformer = DataTransformer()
        result = transformer.validate_data(df)

        assert len(result) == 2
        assert -50.0 not in result["VAL_TOT"].values


class TestEnrichData:
    """
    FEATURE: Enriquecimento de dados
    COMO: Sistema ETL
    QUERO: Adicionar campos calculados e categorizações
    """

    def test_calculate_stay_days(self):
        """Deve calcular stay_days = (DT_SAIDA - DT_INTER).days"""
        df = pd.DataFrame(
            {
                "DT_INTER": pd.to_datetime(["2024-01-10", "2024-01-15"]),
                "DT_SAIDA": pd.to_datetime(["2024-01-15", "2024-01-20"]),
            }
        )

        transformer = DataTransformer()
        result = transformer.enrich_data(df)

        assert "stay_days" in result.columns
        assert result["stay_days"].iloc[0] == 5
        assert result["stay_days"].iloc[1] == 5

    def test_calculate_daily_cost(self):
        """Deve calcular daily_cost = VAL_TOT / stay_days"""
        df = pd.DataFrame(
            {
                "DT_INTER": pd.to_datetime(["2024-01-10"]),
                "DT_SAIDA": pd.to_datetime(["2024-01-15"]),
                "VAL_TOT": [1500.0],
            }
        )

        transformer = DataTransformer()
        result = transformer.enrich_data(df)

        assert "daily_cost" in result.columns
        assert result["daily_cost"].iloc[0] == 300.0

    def test_daily_cost_avoid_division_by_zero(self):
        """Deve evitar divisão por zero usando replace(0, 1)"""
        df = pd.DataFrame(
            {
                "DT_INTER": pd.to_datetime(["2024-01-10"]),
                "DT_SAIDA": pd.to_datetime(["2024-01-10"]),  # mesmo dia
                "VAL_TOT": [1000.0],
            }
        )

        transformer = DataTransformer()
        result = transformer.enrich_data(df)

        assert result["stay_days"].iloc[0] == 0
        assert result["daily_cost"].iloc[0] == 1000.0

    def test_categorize_age_groups(self):
        """Deve categorizar idades em faixas corretas"""
        df = pd.DataFrame({"IDADE": [10.0, 18.0, 25.0, 30.0, 45.0, 60.0, 85.0]})

        transformer = DataTransformer()
        result = transformer.enrich_data(df)

        assert "age_group" in result.columns
        assert str(result["age_group"].iloc[0]) == "0-17"
        assert str(result["age_group"].iloc[1]) == "0-17"  # 18 está em (0,18]
        assert str(result["age_group"].iloc[2]) == "18-29"
        assert str(result["age_group"].iloc[3]) == "18-29"  # 30 está em (18,30]
        assert str(result["age_group"].iloc[4]) == "30-44"  # 45 está em (30,45]
        assert str(result["age_group"].iloc[5]) == "45-59"  # 60 está em (45,60]
        assert str(result["age_group"].iloc[6]) == "60+"

    def test_flag_death_true(self):
        """Deve marcar death=True quando MORTE=1"""
        df = pd.DataFrame({"MORTE": [1, 0, 1]})

        transformer = DataTransformer()
        result = transformer.enrich_data(df)

        assert "death" in result.columns
        assert result["death"].iloc[0]
        assert not result["death"].iloc[1]
        assert result["death"].iloc[2]


class TestTransformPipeline:
    """
    Feature: Pipeline completo de transformação
    Como: Sistema ETL
    Quero: Executar todas etapas em sequência
    """

    def test_full_pipeline_valid_data(self):
        """Pipeline completo deve processar dados válidos"""
        df = pd.DataFrame(
            {
                "N_AIH": ["123"],
                "IDADE": ["25"],
                "DT_INTER": ["20240101"],
                "DT_SAIDA": ["20240105"],
                "VAL_TOT": ["1500.00"],
                "MORTE": [0],
            }
        )

        transformer = DataTransformer()
        result = transformer.transform(df)

        assert len(result) == 1
        assert "stay_days" in result.columns
        assert "age_group" in result.columns
        assert "death" in result.columns

    def test_full_pipeline_reject_invalid_data(self):
        """Pipeline completo deve rejeitar dados inválidos"""
        df = pd.DataFrame(
            {
                "N_AIH": ["123", "456"],
                "IDADE": ["-5", "25"],
                "DT_INTER": ["20240101", "20240101"],
                "DT_SAIDA": ["20240105", "20240105"],
                "VAL_TOT": ["1500.00", "2000.00"],
            }
        )

        transformer = DataTransformer()
        result = transformer.transform(df)

        assert len(result) == 1
        assert result["IDADE"].iloc[0] == 25.0
