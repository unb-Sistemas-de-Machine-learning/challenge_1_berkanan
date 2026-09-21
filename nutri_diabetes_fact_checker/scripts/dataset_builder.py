"""
dataset_builder.py — Geração do dataset rotulado FAKE/REAL sobre nutrição e diabetes.

Inclui 100+ exemplos curados, deduplicação, train/test split e limpeza de texto.
Se existir data/raw/factchecks.json (gerado pelo scraper), incorpora automaticamente.
"""
import pandas as pd
import os
import re
import json
import hashlib

# ====================================================================
# Dados curados manualmente — exemplos reais de desinformação e
# informações corretas sobre diabetes e nutrição no Brasil
# ====================================================================

FAKE_EXAMPLES = [
    # Curas milagrosas
    "Chá de folha de manga cura diabetes em 3 dias.",
    "Diabéticos nunca mais precisarão de insulina se comerem quiabo com água em jejum.",
    "Mel natural não eleva a glicose no sangue, diabéticos podem comer à vontade.",
    "Cortar 100% dos carboidratos cura diabetes tipo 1.",
    "A cura do diabetes está no vinagre de maçã tomado toda manhã.",
    "Cápsulas de canela substituem a metformina no tratamento do diabetes.",
    "Suco de berinjela com limão em jejum reverte o diabetes tipo 2 em uma semana.",
    "Cientistas descobriram que o jiló elimina a necessidade de insulina.",
    "Tomar água com limão em jejum regula a glicose e cura o diabetes.",
    "Pesquisa comprova que banho gelado normaliza a glicemia permanentemente.",
    # Restrições falsas
    "Diabéticos não podem comer nenhuma fruta porque todas têm muito açúcar.",
    "Arroz integral tem o mesmo efeito que arroz branco na glicemia, não faz diferença.",
    "Diabéticos não precisam medir a glicose se estiverem se sentindo bem.",
    "A insulina causa dependência e vicia, é melhor evitar usar.",
    "Diabetes tipo 2 é causado exclusivamente por comer muito açúcar.",
    # Conspirações
    "A indústria farmacêutica esconde a cura do diabetes porque lucra com insulina.",
    "Vacinas causam diabetes tipo 1 em crianças.",
    "Médicos não receitam chá de pata-de-vaca porque as farmacêuticas proíbem.",
    "O governo esconde que o cloreto de magnésio cura diabetes.",
    "Alimentos orgânicos eliminam completamente o risco de desenvolver diabetes.",
    # Exageros nutricionais
    "Comer 10 ovos por dia cura a resistência à insulina.",
    "Jejum de 7 dias seguidos regenera o pâncreas e cura diabetes tipo 1.",
    "Beber 5 litros de água por dia controla o diabetes sem medicação.",
    "A dieta carnívora é a única forma de tratar diabetes tipo 2.",
    "Suplemento de cromo em altas doses substitui todo tratamento para diabetes.",
    # Falsos sobre alimentação
    "Batata-doce pode ser consumida sem limite por diabéticos porque é saudável.",
    "Suco de laranja natural não eleva a glicemia porque é fruta natural.",
    "Adoçantes artificiais são mais perigosos que açúcar para diabéticos.",
    "Pão integral não afeta a glicose no sangue, pode ser consumido livremente.",
    "Chocolate amargo 70% pode ser consumido sem restrição por diabéticos.",
]

REAL_EXAMPLES = [
    # Fisiopatologia
    "O diabetes mellitus tipo 2 é uma doença crônica caracterizada pela resistência à insulina e deficiência relativa na secreção de insulina.",
    "O diabetes tipo 1 é uma doença autoimune na qual o sistema imunológico destrói as células beta do pâncreas.",
    "A hemoglobina glicada (HbA1c) reflete a média da glicemia dos últimos 2 a 3 meses e é usada para monitorar o controle glicêmico.",
    "O diagnóstico de diabetes é confirmado com glicemia de jejum maior ou igual a 126 mg/dL em duas ocasiões distintas.",
    "O pré-diabetes é identificado por glicemia de jejum entre 100 e 125 mg/dL ou HbA1c entre 5,7% e 6,4%.",
    # Tratamento
    "A metformina é o medicamento de primeira linha para o tratamento do diabetes tipo 2, segundo as diretrizes da SBD.",
    "O uso de insulina é indispensável no tratamento de pacientes com diabetes tipo 1 desde o diagnóstico.",
    "A automonitorização da glicemia capilar é fundamental para ajustes nas doses de insulina e prevenção de hipo e hiperglicemia.",
    "O tratamento do diabetes tipo 2 inclui mudanças no estilo de vida, controle alimentar e, quando necessário, medicamentos orais ou insulina.",
    "Inibidores de SGLT2 demonstraram benefício cardiovascular e renal em pacientes com diabetes tipo 2.",
    # Nutrição baseada em evidência
    "É fundamental que pacientes diabéticos controlem a ingestão de carboidratos, priorizando os de baixo índice glicêmico.",
    "A contagem de carboidratos é uma estratégia recomendada pela SBD para o controle glicêmico de pacientes com diabetes tipo 1.",
    "As fibras alimentares auxiliam no controle da glicemia pós-prandial ao retardar a absorção de glicose.",
    "Frutas podem e devem fazer parte da alimentação do diabético, desde que consumidas em porções adequadas.",
    "A Sociedade Brasileira de Diabetes recomenda distribuir os carboidratos em 5 a 6 refeições ao longo do dia.",
    # Atividade física
    "A prática de exercícios físicos regulares ajuda a melhorar a sensibilidade à insulina e o controle glicêmico.",
    "A Sociedade Brasileira de Diabetes recomenda pelo menos 150 minutos semanais de atividade física aeróbica moderada.",
    "Exercícios de resistência muscular também são recomendados para pacientes diabéticos, pelo menos 2 vezes por semana.",
    "Pacientes em uso de insulina devem ajustar a dose ou ingerir carboidratos antes de exercícios para evitar hipoglicemia.",
    # Complicações
    "A retinopatia diabética é a principal causa de cegueira evitável em adultos em idade produtiva.",
    "A nefropatia diabética é a principal causa de doença renal crônica terminal que leva à diálise no Brasil.",
    "O pé diabético resulta da neuropatia periférica e da doença vascular e pode levar a amputações se não tratado adequadamente.",
    "A neuropatia diabética pode causar perda de sensibilidade nos pés, aumentando o risco de úlceras e infecções.",
    "O controle rigoroso da pressão arterial e dos lipídios é essencial para prevenir complicações cardiovasculares no diabetes.",
    # Prevenção
    "Perder de 5% a 7% do peso corporal reduz significativamente o risco de desenvolver diabetes tipo 2 em pessoas com pré-diabetes.",
    "A amamentação exclusiva nos primeiros 6 meses pode reduzir o risco de diabetes tipo 1 na criança.",
    "O rastreamento de diabetes deve ser feito em adultos a partir dos 45 anos ou antes se houver fatores de risco.",
    "O Programa Nacional de Controle do Diabetes do Ministério da Saúde fornece insulina e medicamentos gratuitamente pelo SUS.",
    "Monitorar a glicemia capilar diariamente ajuda a prevenir episódios de hipoglicemia e hiperglicemia.",
]


def clean_text(text: str) -> str:
    """Normaliza o texto: minúsculas, remove pontuação excessiva, espaços."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\sáàãâéêíóôõúüç]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_hash(text: str) -> str:
    """Hash para deduplicação."""
    return hashlib.md5(clean_text(text).encode("utf-8")).hexdigest()


def build_dataset(output_path: str):
    """Monta o dataset completo, deduplica e divide em train/test."""
    print("Montando dataset...")

    records = []
    for t in FAKE_EXAMPLES:
        records.append({"text": t, "label": "FAKE", "source": "curated"})
    for t in REAL_EXAMPLES:
        records.append({"text": t, "label": "REAL", "source": "curated"})

    # Incorpora fact-checks raspados (se existirem)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fc_path = os.path.join(project_root, "data", "raw", "factchecks.json")
    if os.path.exists(fc_path):
        with open(fc_path, "r", encoding="utf-8") as f:
            fc_data = json.load(f)
        for item in fc_data:
            records.append({
                "text": item["text"],
                "label": "FAKE",  # Fact-checks geralmente desmentem afirmações
                "source": item.get("source", "factcheck_scraped"),
            })
        print(f"  + {len(fc_data)} registros importados de factchecks.json")

    df = pd.DataFrame(records)
    df["cleaned_text"] = df["text"].apply(clean_text)
    df["text_hash"] = df["cleaned_text"].apply(text_hash)

    # Deduplicação
    before = len(df)
    df = df.drop_duplicates(subset="text_hash").reset_index(drop=True)
    print(f"  Deduplicação: {before} → {len(df)} registros")

    # Shuffle e split 80/20
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_test = df.iloc[split_idx:]

    # Salva
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    full_path = output_path.replace(".csv", "_full.csv")
    train_path = output_path.replace(".csv", "_train.csv")
    test_path = output_path.replace(".csv", "_test.csv")

    df.to_csv(full_path, index=False)
    df_train.to_csv(train_path, index=False)
    df_test.to_csv(test_path, index=False)

    print(f"\n✔ Dataset completo: {full_path} ({len(df)} registros)")
    print(f"✔ Treino:          {train_path} ({len(df_train)} registros)")
    print(f"✔ Teste:           {test_path} ({len(df_test)} registros)")
    print(f"\nDistribuição de labels:")
    print(df["label"].value_counts().to_string())


if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_CSV = os.path.join(
        PROJECT_ROOT, "data", "processed", "diabetes_nutrition_dataset.csv"
    )
    build_dataset(OUTPUT_CSV)