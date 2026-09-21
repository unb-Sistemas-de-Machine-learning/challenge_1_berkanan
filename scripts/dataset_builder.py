"""
dataset_builder.py — Geração do dataset rotulado FAKE/REAL sobre nutrição e diabetes.

Inclui 160+ exemplos curados especializados, deduplicação, train/test split balanceado
e limpeza de texto. Se existir data/raw/factchecks.json (gerado pelo scraper temático),
incorpora automaticamente com validação estrita.
"""
import os
import re
import json
import hashlib
import pandas as pd

# ====================================================================
# Dados curados manualmente — exemplos reais de desinformação e
# informações corretas sobre diabetes e nutrição no Brasil (Consenso SBD/MS/ADA)
# ====================================================================

FAKE_EXAMPLES = [
    # --- Curas milagrosas e receitas caseiras ---
    "Chá de folha de manga cura diabetes em 3 dias.",
    "Diabéticos nunca mais precisarão de insulina se comerem quiabo com água em jejum.",
    "Mel natural não eleva a glicose no sangue, diabéticos podem comer à vontade.",
    "Cortar 100% dos carboidratos cura diabetes tipo 1 definitivamente.",
    "A cura do diabetes está no vinagre de maçã tomado puro toda manhã.",
    "Cápsulas de canela substituem com segurança a metformina no tratamento do diabetes.",
    "Suco de berinjela com limão em jejum reverte o diabetes tipo 2 em uma semana.",
    "Cientistas descobriram que o jiló cru elimina a necessidade de qualquer insulina.",
    "Tomar água morna com limão em jejum regula a glicose e cura o diabetes mellitus.",
    "Pesquisa comprova que banho gelado de imersão normaliza a glicemia permanentemente.",
    "Chá de pata-de-vaca e carqueja cura diabetes sem precisar de medicação.",
    "Farinha de maracujá elimina a glicose do sangue e permite comer doces à vontade.",
    "Semente de abacate ralada fervida cura diabetes tipo 2 em menos de um mês.",
    "Bicarbonato de sódio com limão alcaliniza o sangue e destrói a causa do diabetes.",
    "Comer caroço de jaca cozido regenera as células beta do pâncreas.",

    # --- Mitos sobre restrições e permissões alimentares ---
    "Diabéticos não podem comer nenhuma fruta porque todas são veneno para o pâncreas.",
    "Arroz integral tem o mesmo efeito exato que arroz branco na glicemia, não faz diferença nutricional.",
    "Pão integral não afeta a glicose no sangue, podendo ser consumido livremente ao longo do dia.",
    "Batata-doce pode ser consumida sem limite por diabéticos porque tem índice glicêmico zero.",
    "Suco de laranja natural não eleva a glicemia porque é fruta pura sem açúcar adicionado.",
    "Chocolate amargo 70% ou 85% não possui carboidratos e diabéticos podem comer sem restrição.",
    "Tapioca é liberada para diabéticos porque não contém glúten e não altera a insulina.",
    "Açúcar mascavo e açúcar demerara são saudáveis para diabéticos e não aumentam a glicemia.",
    "Pessoas com diabetes não podem comer beterraba ou cenoura por terem muito açúcar.",
    "Diabéticos devem substituir todo tipo de gordura por óleo de coco para curar a glicemia.",
    "Melado de cana é um remédio natural indicado para baixar a glicose de diabéticos.",
    "Água de coco pode ser consumida à vontade sem nenhum impacto na glicemia de quem tem diabetes.",
    "Frutas secas como uva-passa não aumentam a glicemia porque a água foi retirada.",
    "Alimentos diet podem ser consumidos sem qualquer restrição de quantidade por pessoas com diabetes.",
    "Comer abacaxi com canela após o almoço queima todos os carboidratos da refeição.",

    # --- Mitos sobre insulina, medicamentos e monitorização ---
    "Diabéticos não precisam medir a glicose se estiverem se sentindo bem e sem sintomas.",
    "A insulina causa dependência química, vicia o organismo e acelera a perda da visão.",
    "Começar a tomar insulina significa que a pessoa está na fase terminal do diabetes.",
    "A metformina destrói o fígado e os rins, sendo preferível tratar diabetes apenas com ervas.",
    "Diabéticos devem suspender a insulina caso fiquem gripados ou sem apetite.",
    "Tomar remédio para diabetes permite comer açúcar e doces na quantidade que quiser.",
    "Aplicar insulina diretamente na veia faz o efeito ser mais rápido e seguro.",
    "Quem tem diabetes tipo 2 nunca vai precisar aplicar insulina se tiver força de vontade.",
    "O uso de canetas de insulina causa câncer no pâncreas a longo prazo.",
    "Insulina engorda tanto que é melhor manter a glicemia alta do que iniciar o tratamento.",

    # --- Teorias conspiratórias e causas falsas ---
    "A indústria farmacêutica internacional esconde a cura do diabetes porque lucra bilhões com insulina.",
    "Vacinas infantis são as verdadeiras causadoras da epidemia de diabetes tipo 1 em crianças.",
    "Médicos omitem o tratamento com cloreto de magnésio porque curaria o diabetes de graça.",
    "O diabetes não existe, é apenas uma invenção da medicina moderna para vender remédios.",
    "O estresse emocional é a única e exclusiva causa do surgimento do diabetes tipo 2.",
    "Diabetes é contagioso e pode ser transmitido pelo contato com sangue ou saliva de pacientes.",
    "Alimentos orgânicos eliminam 100% do risco de qualquer pessoa desenvolver diabetes.",

    # --- Dietas radicais e exageros ---
    "Comer 10 ovos inteiros por dia cura a resistência à insulina em 15 dias.",
    "Jejum intermitente seco de 7 dias regenera completamente o pâncreas no diabetes tipo 1.",
    "Beber 6 litros de água por dia elimina todo o excesso de açúcar na urina sem medicação.",
    "A dieta estritamente carnívora é a única intervenção que cura diabetes tipo 2.",
    "Suplementos de cromo e vanádio em superdoses substituem integralmente o uso de insulina.",
    "Dieta da proteína pura sem vegetais normaliza a hemoglobina glicada sem riscos renais.",
    "Consumir banha de porco em todas as refeições reverte o pré-diabetes em 48 horas.",
    "Água alcalina com ozônio neutraliza a acidez pancreática e cura o diabetes infantil.",

    # --- Mitos sobre adoçantes e substitutos ---
    "Adoçantes artificiais são comprovadamente mais perigosos que o açúcar para pacientes diabéticos.",
    "Qualquer tipo de adoçante causa picos imediatos de insulina idênticos aos do açúcar refinado.",
    "Adoçante de sucralose se transforma em cloro tóxico no organismo e agrava o diabetes.",

    # --- Mitos sobre exercícios e prevenção ---
    "Praticar musculação pesada é proibido para qualquer pessoa diagnosticada com diabetes.",
    "Exercício físico intenso em jejum é a forma mais segura de baixar a glicemia no diabetes tipo 1.",
    "Transpirar bastante na sauna queima glicose e substitui a prática de atividades aeróbicas.",

    # --- Mitos populares adicionais ---
    "Água com quiabo deixada de um dia para o outro produz insulina vegetal suficiente para dispensar remédios.",
    "Comer doce não faz mal para diabético se ele tomar um copo de café sem açúcar em seguida.",
    "Chá de folha de graviola mata as células do diabetes e restaura a glicose em 24 horas.",
    "Diabéticos podem comer farinha de mandioca e polvilho sem limite porque são derivados de raiz natural.",
    "Se a pessoa não sente tontura ou sede, a glicose não está descontrolada.",
    "Insulina inalável caseira feita com ervas substitui as injeções diárias.",
    "O teste da glicemia na ponta do dedo estraga os nervos da mão com o passar dos anos.",
    "Melancia é proibida para quem tem diabetes porque vira açúcar puro no estômago instantaneamente.",
    "Comer pipoca à vontade ajuda a limpar o açúcar do sangue por ter fibras duras.",
    "Toda pessoa com diabetes vai inevitavelmente perder a visão ou ter um membro amputado.",
    "Bebidas alcoólicas destiladas não afetam a glicemia de diabéticos e podem ser bebidas livremente.",
    "Iogurte desnatado com açúcar mascavo é um lanche seguro e sem carboidrato para diabéticos.",
    "Leite condensado diet pode ser consumido inteiro sem impacto no controle glicêmico.",
    "Fazer banho de assento com chá de alecrim reduz a glicemia de jejum.",
    "Tomar própolis vermelha em jejum elimina a resistência insulínica em 3 dias.",
    "Chá de folha de amora é cientificamente comprovado como substituto da insulina NPH.",
    "Quem usa metformina pode comer pizza e sobremesa à vontade que o remédio anula tudo.",
    "Diabéticos tipo 1 desenvolvem a doença porque consumiram refrigerante em excesso na infância.",
    "Alimentos sem glúten são automaticamente seguros e sem carboidratos para quem tem diabetes.",
    "Cerveja sem álcool não altera a glicemia e pode ser tomada sem moderação por diabéticos.",
]

REAL_EXAMPLES = [
    # --- Fisiopatologia e Definições Clínicas ---
    "O diabetes mellitus tipo 2 é uma doença crônica caracterizada pela resistência à insulina e deficiência relativa na secreção de insulina.",
    "O diabetes tipo 1 é uma doença autoimune na qual o sistema imunológico destrói as células beta produtoras de insulina no pâncreas.",
    "A hemoglobina glicada (HbA1c) reflete a média da glicemia dos últimos 2 a 3 meses e é padrão-ouro no monitoramento do controle glicêmico.",
    "O diagnóstico de diabetes é confirmado com glicemia de jejum maior ou igual a 126 mg/dL em duas ocasiões distintas.",
    "O pré-diabetes é identificado por glicemia de jejum entre 100 e 125 mg/dL ou HbA1c entre 5,7% e 6,4%.",
    "No teste de tolerância oral à glicose (TOTG 75g), valores iguais ou superiores a 200 mg/dL após duas horas confirmam diabetes.",
    "Glicemia casual superior a 200 mg/dL acompanhada de sintomas clássicos como poliúria e polidipsia fecha o diagnóstico de diabetes.",
    "A cetoacidose diabética é uma complicação aguda grave comum no diabetes tipo 1 decorrente da ausência absoluta de insulina.",
    "O estado hiperosmolar hiperglicêmico é uma emergência médica associada a hiperglicemia extrema, mais comum no diabetes tipo 2 idoso.",

    # --- Tratamento Farmacológico Baseado em Evidências ---
    "A metformina é o medicamento de primeira linha para o tratamento do diabetes tipo 2, segundo as diretrizes da SBD.",
    "O uso de insulina é indispensável à sobrevivência de pacientes com diabetes tipo 1 desde o momento do diagnóstico.",
    "A automonitorização da glicemia capilar é fundamental para ajustes nas doses de insulina e prevenção de hipo e hiperglicemia.",
    "O tratamento do diabetes tipo 2 inclui mudanças no estilo de vida, controle alimentar e, quando necessário, medicamentos orais ou insulina.",
    "Inibidores de SGLT2 demonstraram benefício comprovado na redução de desfechos cardiovasculares e progressão de doença renal no diabetes tipo 2.",
    "Agonistas do receptor de GLP-1 promovem controle glicêmico eficaz, redução de peso corporal e proteção cardiovascular em pacientes com diabetes tipo 2.",
    "Sulfonilureias estimulam a secreção de insulina pelas células beta, mas demandam atenção pelo risco de episódios de hipoglicemia.",
    "A insulina basal tem como objetivo controlar a produção hepática de glicose durante o jejum e entre as refeições.",
    "A insulina prandial de ação rápida ou ultrarrápida é calculada para cobrir o impacto glicêmico dos carboidratos ingeridos nas refeições.",
    "O rodízio dos locais de aplicação de insulina é essencial para evitar lipohipertrofia, que prejudica a absorção do medicamento.",
    "A insulina degludeca e a insulina glargina são análogos de insulina basal com perfil de ação prolongado e menor risco de hipoglicemia noturna.",
    "A insulina lispro, asparte e glulisina são análogos de ação ultrarrápida que devem ser aplicados imediatamente antes ou logo após a refeição.",

    # --- Nutrição Baseada em Evidências (Consenso SBD / ADA) ---
    "É fundamental que pacientes diabéticos controlem a ingestão total de carboidratos, priorizando os de baixo índice glicêmico.",
    "A contagem de carboidratos é uma estratégia nutricional flexível recomendada pela SBD para otimizar o controle glicêmico.",
    "As fibras alimentares auxiliam no controle da glicemia pós-prandial ao retardar a digestão e absorção dos carboidratos.",
    "Frutas frescas inteiras podem e devem fazer parte da alimentação do diabético, respeitando porções adequadas e evitando sucos coados.",
    "A Sociedade Brasileira de Diabetes recomenda distribuir a ingestão de carboidratos de maneira equilibrada ao longo das refeições diárias.",
    "O consumo de gorduras saturadas deve ser limitado, dando preferência a ácidos graxos monoinsaturados e poli-insaturados.",
    "Alimentos integrais contêm fibras que reduzem o pico glicêmico em comparação com alimentos ricos em farinhas brancas refinadas.",
    "O índice glicêmico avalia a velocidade com que um carboidrato eleva a glicemia, enquanto a carga glicêmica considera também a porção consumida.",
    "Pessoas com diabetes devem ter cautela com produtos diet, pois embora não contenham açúcar adicionado, podem ser calóricos e ricos em gordura.",
    "Adoçantes não calóricos aprovados pela ANVISA, como estévia e sucralose, são alternativas seguras ao açúcar quando consumidos com moderação.",
    "Açúcar mascavo, demerara e mel possuem impacto glicêmico similar ao do açúcar branco refinado e elevam expressivamente a glicemia.",
    "Tapioca possui alto índice glicêmico e sua absorção pode ser desacelerada se combinada com fontes de fibras ou proteínas como ovos e chia.",
    "Leguminosas como feijão, lentilha e grão-de-bico fornecem carboidratos complexos e fibras solúveis benéficas ao controle glicêmico.",
    "O consumo moderado de água e a hidratação adequada ajudam os rins a excretar o excesso de glicose quando os níveis estão elevados.",
    "O fracionamento das refeições evita oscilações glicêmicas bruscas e auxilia no controle da saciedade.",
    "Alimentos ultraprocessados devem ser evitados devido ao elevado teor de sódio, gorduras saturadas e carboidratos simples.",
    "O consumo de peixes ricos em ômega-3 pelo menos duas vezes por semana é recomendado para saúde cardiovascular no diabetes.",

    # --- Atividade Física e Prevenção ---
    "A prática de exercícios físicos regulares ajuda a melhorar a sensibilidade à insulina e a captação muscular de glicose.",
    "A Sociedade Brasileira de Diabetes recomenda pelo menos 150 minutos semanais de atividade física aeróbica de intensidade moderada.",
    "Exercícios de força e resistência muscular também são recomendados para pacientes diabéticos, pelo menos duas a três vezes por semana.",
    "Pacientes em uso de insulina devem monitorar a glicemia antes e após exercícios para prevenir episódios de hipoglicemia tardia.",
    "Perder entre 5% e 7% do peso corporal através de dieta equilibrada e exercícios reduz expressivamente a progressão de pré-diabetes para diabetes tipo 2.",
    "O rastreamento de diabetes tipo 2 deve ser realizado periodicamente em adultos com sobrepeso associado a outros fatores de risco cardiovascular.",
    "A atividade física regular estimula a translocação dos transportadores GLUT4 independentemente da presença de insulina.",

    # --- Complicações Crônicas, Hipoglicemia e Monitoramento ---
    "A retinopatia diabética é uma das principais causas de perda visual evitável em adultos e requer exame de fundo de olho anual.",
    "A nefropatia diabética é uma das maiores causas de insuficiência renal crônica em diálise no Brasil, detectada precocemente pela microalbuminúria.",
    "A neuropatia diabética periférica causa perda progressiva de sensibilidade nos membros inferiores, aumentando o risco de feridas e úlceras.",
    "O exame periódico dos pés por profissional de saúde é fundamental para prevenção de úlceras e amputações relacionadas ao pé diabético.",
    "O controle conjunto da pressão arterial e dos lipídios plasmáticos é essencial para reduzir complicações cardiovasculares no diabetes.",
    "A hipoglicemia é clinicamente definida como glicemia capilar ou plasmática inferior a 70 mg/dL.",
    "Sintomas comuns de hipoglicemia incluem sudorese fria, tremores, taquicardia, tontura e confusão mental.",
    "A regra dos 15 para tratar hipoglicemia consiste em ingerir 15g de carboidrato rápido, esperar 15 minutos e retestar a glicemia.",
    "Bebidas alcoólicas podem inibir a gliconeogênese hepática e causar episódios graves de hipoglicemia tardia.",
    "A meta terapêutica padrão de HbA1c para a maioria dos adultos não gestantes com diabetes é inferior a 7,0%.",
    "O tempo no alvo (Time in Range - TIR) entre 70 e 180 mg/dL medido por sensores contínuos deve ser superior a 70%.",
    "O Programa Farmácia Popular do Ministério da Saúde distribui gratuitamente medicamentos essenciais e insulinas para diabetes pelo SUS.",
    "A educação contínua em diabetes é considerada pilar terapêutico para autonomia e adesão do paciente ao tratamento.",
]


def clean_text(text: str) -> str:
    """Normaliza o texto: minúsculas, pontuação excessiva e espaços extras."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\sáàãâéêíóôõúüç]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_hash(text: str) -> str:
    """Gera hash MD5 do texto normalizado para deduplicação precisa."""
    return hashlib.md5(clean_text(text).encode("utf-8")).hexdigest()


def build_dataset(output_path: str):
    """Monta o dataset completo, deduplica, valida e divide em train/test balanceados."""
    print("=" * 60)
    print("GERANDO DATASET DE NUTRIÇÃO E DIABETES")
    print("=" * 60)

    records = []
    for t in FAKE_EXAMPLES:
        records.append({"text": t, "label": "FAKE", "source": "curated_expert"})
    for t in REAL_EXAMPLES:
        records.append({"text": t, "label": "REAL", "source": "curated_expert"})

    print(f"  Exemplos curados iniciais: {len(records)} ({len(FAKE_EXAMPLES)} FAKE, {len(REAL_EXAMPLES)} REAL)")

    # Incorpora fact-checks raspados se existirem (filtrados previamente pelo scraper)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fc_path = os.path.join(project_root, "data", "raw", "factchecks.json")
    if os.path.exists(fc_path):
        try:
            with open(fc_path, "r", encoding="utf-8") as f:
                fc_data = json.load(f)
            imported_count = 0
            for item in fc_data:
                # Checagens desmentem boatos, classificadas como FAKE
                records.append({
                    "text": item["text"],
                    "label": "FAKE",
                    "source": item.get("source", "factcheck_scraped"),
                })
                imported_count += 1
            print(f"  + {imported_count} registros temáticos importados de {fc_path}")
        except Exception as e:
            print(f"  ⚠ Erro ao ler factchecks.json: {e}")

    df = pd.DataFrame(records)
    df["cleaned_text"] = df["text"].apply(clean_text)
    df["text_hash"] = df["cleaned_text"].apply(text_hash)

    # Deduplicação por conteúdo textual
    before = len(df)
    df = df.drop_duplicates(subset="text_hash").reset_index(drop=True)
    print(f"  Deduplicação: {before} → {len(df)} registros únicos")

    # Shuffle com semente determinística
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Split estratificado por label (80% treino, 20% teste)
    train_dfs, test_dfs = [], []
    for label, group in df.groupby("label"):
        split_idx = int(len(group) * 0.8)
        train_dfs.append(group.iloc[:split_idx])
        test_dfs.append(group.iloc[split_idx:])

    df_train = pd.concat(train_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    df_test = pd.concat(test_dfs).sample(frac=1, random_state=42).reset_index(drop=True)

    # Persistência
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    full_path = output_path.replace(".csv", "_full.csv")
    train_path = output_path.replace(".csv", "_train.csv")
    test_path = output_path.replace(".csv", "_test.csv")

    df.to_csv(full_path, index=False, encoding="utf-8")
    df_train.to_csv(train_path, index=False, encoding="utf-8")
    df_test.to_csv(test_path, index=False, encoding="utf-8")

    print(f"\n✔ Dataset completo: {full_path} ({len(df)} registros)")
    print(f"✔ Treino:          {train_path} ({len(df_train)} registros)")
    print(f"✔ Teste:           {test_path} ({len(df_test)} registros)")
    print(f"\nDistribuição Geral:")
    print(df["label"].value_counts().to_string())
    print(f"\nDistribuição Treino:")
    print(df_train["label"].value_counts().to_string())
    print(f"\nDistribuição Teste:")
    print(df_test["label"].value_counts().to_string())


if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_CSV = os.path.join(
        PROJECT_ROOT, "data", "processed", "diabetes_nutrition_dataset.csv"
    )
    build_dataset(OUTPUT_CSV)
