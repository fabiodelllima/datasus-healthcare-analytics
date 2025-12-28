"""
Testes unitários para módulo de KPIs.

Referência: docs/DATA_GUIDE.md seção "KPIs Implementados"
"""

import pandas as pd
import pytest

from src.analytics.kpis import KPICalculator


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """DataFrame de exemplo para testes."""
    return pd.DataFrame(
        {
            "N_AIH": ["001", "002", "003", "004", "005"],
            "stay_days": [5, 3, 7, 2, 3],
            "VAL_TOT": [1000.0, 1500.0, 2000.0, 800.0, 1200.0],
            "ESPEC": ["01", "01", "03", "03", "08"],
            "specialty_name": ["1", "1", "3", "3", "8"],
            "age_group": pd.Categorical(
                ["0-17", "18-29", "30-44", "45-59", "60+"],
                categories=["0-17", "18-29", "30-44", "45-59", "60+"],
            ),
            "DT_INTER": pd.to_datetime(
                ["2024-01-05", "2024-01-10", "2024-01-15", "2024-02-01", "2024-02-10"]
            ),
        }
    )


@pytest.fixture
def calculator() -> KPICalculator:
    """Instância do calculador de KPIs."""
    return KPICalculator()


class TestOccupancyRate:
    """Testes para Taxa de Ocupação."""

    def test_occupancy_rate_basic(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Taxa de ocupação com valores válidos."""
        # stay_days.sum() = 5+3+7+2+3 = 20 pacientes-dia
        # ocupação = 20 / (10 leitos * 30 dias) * 100 = 6.67%
        result = calculator.occupancy_rate(sample_df, beds=10, days=30)
        assert result == pytest.approx(6.67, rel=0.01)

    def test_occupancy_rate_full(self, calculator: KPICalculator) -> None:
        """Taxa de ocupação 100%."""
        df = pd.DataFrame({"stay_days": [30, 30, 30]})  # 3 pacientes, 30 dias cada
        result = calculator.occupancy_rate(df, beds=3, days=30)
        assert result == pytest.approx(100.0, rel=0.01)

    def test_occupancy_rate_empty_df(self, calculator: KPICalculator) -> None:
        """Taxa de ocupação com DataFrame vazio."""
        df = pd.DataFrame({"stay_days": []})
        result = calculator.occupancy_rate(df, beds=10, days=30)
        assert result == 0.0

    def test_occupancy_rate_zero_beds_raises(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        """Erro ao calcular com zero leitos."""
        with pytest.raises(ValueError, match="leitos"):
            calculator.occupancy_rate(sample_df, beds=0, days=30)

    def test_occupancy_rate_zero_days_raises(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        """Erro ao calcular com zero dias."""
        with pytest.raises(ValueError, match="dias"):
            calculator.occupancy_rate(sample_df, beds=10, days=0)


class TestAverageLengthOfStay:
    """Testes para Tempo Médio de Permanência (TMP)."""

    def test_alos_basic(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """TMP com valores válidos."""
        # mean([5, 3, 7, 2, 3]) = 4.0
        result = calculator.average_length_of_stay(sample_df)
        assert result == 4.0

    def test_alos_empty_df(self, calculator: KPICalculator) -> None:
        """TMP com DataFrame vazio retorna 0."""
        df = pd.DataFrame({"stay_days": []})
        result = calculator.average_length_of_stay(df)
        assert result == 0.0

    def test_alos_by_specialty(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """TMP agrupado por especialidade."""
        result = calculator.average_length_of_stay(sample_df, group_by="specialty_name")
        assert isinstance(result, dict)
        # specialty "1": mean([5, 3]) = 4.0
        # specialty "3": mean([7, 2]) = 4.5
        # specialty "8": mean([3]) = 3.0
        assert result["1"] == 4.0
        assert result["3"] == 4.5
        assert result["8"] == 3.0

    def test_alos_by_invalid_column_raises(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        """Erro ao agrupar por coluna inexistente."""
        with pytest.raises(KeyError):
            calculator.average_length_of_stay(sample_df, group_by="invalid_column")


class TestVolume:
    """Testes para Volume de Atendimentos."""

    def test_volume_total(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Volume total de internações."""
        result = calculator.volume(sample_df)
        assert result == 5

    def test_volume_empty_df(self, calculator: KPICalculator) -> None:
        """Volume com DataFrame vazio."""
        df = pd.DataFrame()
        result = calculator.volume(df)
        assert result == 0

    def test_volume_by_month(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Volume agrupado por mês."""
        result = calculator.volume(sample_df, group_by="month")
        assert isinstance(result, dict)
        # Janeiro: 3 internações, Fevereiro: 2 internações
        assert result[1] == 3
        assert result[2] == 2

    def test_volume_by_specialty(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Volume agrupado por especialidade."""
        result = calculator.volume(sample_df, group_by="specialty_name")
        assert isinstance(result, dict)
        assert result["1"] == 2
        assert result["3"] == 2
        assert result["8"] == 1


class TestRevenue:
    """Testes para Receita Total."""

    def test_revenue_total(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Receita total."""
        # sum([1000, 1500, 2000, 800, 1200]) = 6500
        result = calculator.revenue(sample_df)
        assert result == 6500.0

    def test_revenue_empty_df(self, calculator: KPICalculator) -> None:
        """Receita com DataFrame vazio."""
        df = pd.DataFrame({"VAL_TOT": []})
        result = calculator.revenue(df)
        assert result == 0.0

    def test_revenue_by_specialty(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Receita agrupada por especialidade."""
        result = calculator.revenue(sample_df, group_by="specialty_name")
        assert isinstance(result, dict)
        # specialty "1": 1000 + 1500 = 2500
        # specialty "3": 2000 + 800 = 2800
        # specialty "8": 1200
        assert result["1"] == 2500.0
        assert result["3"] == 2800.0
        assert result["8"] == 1200.0

    def test_average_ticket(self, calculator: KPICalculator, sample_df: pd.DataFrame) -> None:
        """Ticket médio."""
        # mean([1000, 1500, 2000, 800, 1200]) = 1300
        result = calculator.average_ticket(sample_df)
        assert result == 1300.0

    def test_average_ticket_empty_df(self, calculator: KPICalculator) -> None:
        """Ticket médio com DataFrame vazio."""
        df = pd.DataFrame({"VAL_TOT": []})
        result = calculator.average_ticket(df)
        assert result == 0.0


class TestDemographics:
    """Testes para Distribuição Demográfica."""

    def test_demographics_distribution(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        """Distribuição por faixa etária."""
        result = calculator.demographics(sample_df)
        assert isinstance(result, dict)
        # Cada faixa tem 1 registro no sample_df
        assert result["0-17"] == 1
        assert result["18-29"] == 1
        assert result["30-44"] == 1
        assert result["45-59"] == 1
        assert result["60+"] == 1

    def test_demographics_empty_df(self, calculator: KPICalculator) -> None:
        """Demografia com DataFrame vazio."""
        df = pd.DataFrame({"age_group": pd.Categorical([])})
        result = calculator.demographics(df)
        assert isinstance(result, dict)
        assert all(v == 0 for v in result.values())

    def test_demographics_missing_column(self, calculator: KPICalculator) -> None:
        """Erro com coluna age_group ausente."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})
        with pytest.raises(KeyError):
            calculator.demographics(df)


class TestKPISummary:
    """Testes para resumo consolidado de KPIs."""

    def test_summary_returns_all_kpis(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        """Resumo contém todos os KPIs."""
        result = calculator.summary(sample_df, beds=10, days=30)
        assert "occupancy_rate" in result
        assert "average_length_of_stay" in result
        assert "volume" in result
        assert "revenue" in result
        assert "average_ticket" in result
        assert "demographics" in result

    def test_summary_values_correct(
        self, calculator: KPICalculator, sample_df: pd.DataFrame
    ) -> None:
        """Valores do resumo estão corretos."""
        result = calculator.summary(sample_df, beds=10, days=30)
        assert result["volume"] == 5
        assert result["revenue"] == 6500.0
        assert result["average_ticket"] == 1300.0
        assert result["average_length_of_stay"] == 4.0
