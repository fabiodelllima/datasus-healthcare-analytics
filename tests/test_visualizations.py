"""Testes para o módulo de visualizações."""

from pathlib import Path

import pandas as pd
import pytest

from src.visualizations.charts import ChartGenerator


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Cria DataFrame de exemplo para testes."""
    return pd.DataFrame(
        {
            "age_group": pd.Categorical(["0-10", "11-20", "21-30", "31-40", "41-50"] * 20),
            "ESPEC": ["01", "02", "03", "04", "05"] * 20,
            "VAL_TOT": [1000.0, 2000.0, 1500.0, 3000.0, 2500.0] * 20,
            "stay_days": [3, 5, 2, 7, 4] * 20,
            "DIAG_PRINC": ["A00", "B01", "C02", "D03", "E04"] * 20,
            "DT_INTER": pd.date_range("2024-01-01", periods=100, freq="D"),
            "SEXO": [1, 3, 1, 3, 1] * 20,
        }
    )


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Cria diretório temporário para outputs."""
    output_dir = tmp_path / "charts"
    output_dir.mkdir()
    return output_dir


class TestChartGeneratorInit:
    """Testes para inicialização do ChartGenerator."""

    def test_init_creates_output_dir(self, tmp_path: Path) -> None:
        """Verifica se o diretório de output é criado."""
        output_dir = tmp_path / "new_charts"
        generator = ChartGenerator(output_dir=output_dir)

        assert output_dir.exists()
        assert generator.output_dir == output_dir

    def test_init_with_string_path(self, tmp_path: Path) -> None:
        """Verifica se aceita string como path."""
        output_dir = str(tmp_path / "string_charts")
        generator = ChartGenerator(output_dir=output_dir)

        assert Path(output_dir).exists()
        assert generator.output_dir == Path(output_dir)


class TestDemographicsByAge:
    """Testes para gráfico de distribuição por faixa etária."""

    def test_generates_png_file(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera arquivo PNG."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.demographics_by_age(sample_dataframe)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "demographics_age" in filepath.name

    def test_returns_correct_path(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se retorna o caminho correto."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.demographics_by_age(sample_dataframe)

        assert filepath == temp_output_dir / "01_demographics_age.png"


class TestRevenueBySpecialty:
    """Testes para gráfico de receita por especialidade."""

    def test_generates_png_file(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera arquivo PNG."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.revenue_by_specialty(sample_dataframe)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "revenue_specialty" in filepath.name


class TestAvgStayBySpecialty:
    """Testes para gráfico de tempo médio de permanência."""

    def test_generates_png_file(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera arquivo PNG."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.avg_stay_by_specialty(sample_dataframe)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "avg_stay_specialty" in filepath.name


class TestTopDiagnoses:
    """Testes para gráfico dos diagnósticos mais frequentes."""

    def test_generates_png_file(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera arquivo PNG."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.top_diagnoses(sample_dataframe)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "top_diagnoses" in filepath.name

    def test_respects_top_n_parameter(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se respeita parâmetro top_n."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        # Deve funcionar sem erros mesmo com top_n menor
        filepath = generator.top_diagnoses(sample_dataframe, top_n=3)

        assert filepath.exists()


class TestVolumeByDay:
    """Testes para gráfico de volume diário."""

    def test_generates_png_file(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera arquivo PNG."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.volume_by_day(sample_dataframe)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "volume_daily" in filepath.name


class TestGenderDistribution:
    """Testes para gráfico de distribuição por sexo."""

    def test_generates_png_file(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera arquivo PNG."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        filepath = generator.gender_distribution(sample_dataframe)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "gender_distribution" in filepath.name


class TestGenerateAll:
    """Testes para geração de todos os gráficos."""

    def test_generates_all_six_charts(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se gera todos os 6 gráficos."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        charts = generator.generate_all(sample_dataframe)

        assert len(charts) == 6
        for chart in charts:
            assert chart.exists()
            assert chart.suffix == ".png"

    def test_returns_paths_in_correct_order(
        self, sample_dataframe: pd.DataFrame, temp_output_dir: Path
    ) -> None:
        """Verifica se retorna paths na ordem correta."""
        generator = ChartGenerator(output_dir=temp_output_dir)
        charts = generator.generate_all(sample_dataframe)

        expected_names = [
            "01_demographics_age.png",
            "02_revenue_specialty.png",
            "03_avg_stay_specialty.png",
            "04_top_diagnoses.png",
            "05_volume_daily.png",
            "06_gender_distribution.png",
        ]

        for chart, expected in zip(charts, expected_names, strict=False):
            assert chart.name == expected
