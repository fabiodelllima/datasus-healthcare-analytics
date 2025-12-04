"""
Transform: Limpeza, validação e enriquecimento de dados
"""

import logging
import pandas as pd
import numpy as np
from src.config import MAX_IDADE, MAX_DIAS_PERM, MAX_VAL_TOT, MIN_VAL_TOT

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforma dados brutos em dados limpos e enriquecidos"""
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo de transformação
        
        Args:
            df: DataFrame bruto
        
        Returns:
            DataFrame transformado
        """
        logger.info("[TRANSFORM] Iniciando pipeline")
        initial_count = len(df)
        
        df = self._convert_types(df)
        df = self._clean(df)
        df = self._validate(df)
        df = self._enrich(df)
        
        final_count = len(df)
        loss_pct = ((initial_count - final_count) / initial_count) * 100
        
        logger.info(f"[TRANSFORM] Concluído: {final_count} registros ({loss_pct:.2f}% perda)")
        
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Etapa 1: Conversão de tipos"""
        logger.info("[TRANSFORM] Etapa 1: Conversão de tipos")
        
        # Datas
        df['DT_INTER'] = pd.to_datetime(df['DT_INTER'], format='%Y%m%d', errors='coerce')
        df['DT_SAIDA'] = pd.to_datetime(df['DT_SAIDA'], format='%Y%m%d', errors='coerce')
        
        # Numéricos
        numeric_cols = ['IDADE', 'DIAS_PERM', 'VAL_TOT', 'VAL_SH', 'VAL_SP', 
                        'VAL_SADT', 'MORTE']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Categóricos
        categorical_cols = ['SEXO', 'ESPEC', 'CAR_INT', 'UF_ZI']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df
    
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Etapa 2: Limpeza"""
        logger.info("[TRANSFORM] Etapa 2: Limpeza")
        
        initial = len(df)
        
        # Duplicatas
        df = df.drop_duplicates(subset=['N_AIH'], keep='first')
        
        # Nulos críticos
        df = df.dropna(subset=['N_AIH', 'DT_INTER', 'DT_SAIDA', 'VAL_TOT'])
        
        removed = initial - len(df)
        logger.info(f"[TRANSFORM] Limpeza: {removed} registros removidos")
        
        return df
    
    def _validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Etapa 3: Validação"""
        logger.info("[TRANSFORM] Etapa 3: Validação")
        
        initial = len(df)
        
        # Datas válidas
        df = df[df['DT_INTER'] <= df['DT_SAIDA']]
        df = df[df['DT_INTER'] >= pd.Timestamp('2008-01-01')]
        df = df[df['DT_SAIDA'] <= pd.Timestamp.now()]
        
        # Permanência válida
        df = df[df['DIAS_PERM'] >= 0]
        df = df[df['DIAS_PERM'] <= MAX_DIAS_PERM]
        
        # Valores válidos
        df = df[(df['VAL_TOT'] > MIN_VAL_TOT) & (df['VAL_TOT'] < MAX_VAL_TOT)]
        
        # Idade válida
        df = df[(df['IDADE'] >= 0) & (df['IDADE'] <= MAX_IDADE)]
        
        removed = initial - len(df)
        logger.info(f"[TRANSFORM] Validação: {removed} registros inválidos removidos")
        
        return df
    
    def _enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Etapa 4: Enriquecimento"""
        logger.info("[TRANSFORM] Etapa 4: Enriquecimento")
        
        # Faixa etária
        df['faixa_etaria'] = df['IDADE'].apply(self._categorizar_idade)
        
        # Especialidade nome
        especialidades_map = {
            '01': 'Cirurgia', '02': 'Obstetrícia', '03': 'Clínica Médica',
            '04': 'Crônico', '05': 'Psiquiatria', '06': 'Pneumologia',
            '07': 'Pediatria', '08': 'Reabilitação', '09': 'Psiquiatria (HD)',
            '10': 'Geriatria', '11': 'Desintoxicação', '12': 'AIDS'
        }
        df['especialidade_nome'] = df['ESPEC'].map(especialidades_map)
        
        # Custo diário
        df['custo_dia'] = df['VAL_TOT'] / df['DIAS_PERM'].replace(0, 1)
        
        # Óbito
        df['obito'] = df['MORTE'].isin([1, '1'])
        
        logger.info(f"[TRANSFORM] Enriquecimento: {len(df.columns)} colunas totais")
        
        return df
    
    @staticmethod
    def _categorizar_idade(idade):
        """Categoriza idade em faixas"""
        if pd.isna(idade):
            return 'Não informado'
        elif idade < 1:
            return 'Recém-nascido'
        elif idade < 12:
            return 'Criança (1-11 anos)'
        elif idade < 18:
            return 'Adolescente (12-17 anos)'
        elif idade < 60:
            return 'Adulto (18-59 anos)'
        else:
            return 'Idoso (60+ anos)'
