from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Diretriz Oficial - Nutricao e Diabetes (MOCK)', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', '', 12)

text = """
1. RECOMENDACOES NUTRICIONAIS PARA DIABETES

O controle glicemico e um dos pilares mais importantes no tratamento do Diabetes Mellitus tipo 1 e tipo 2.
Estudos discutem diretrizes de orgaos internacionais focando na importancia do uso de alimentos com baixo indice glicemico e da fibra alimentar, alem de desmistificar condutas passadas que recomendavam restricoes severas, as quais podiam levar a desnutricao.

2. PREVENCAO PRIMARIA
Intervencoes nutricionais e de estilo de vida sao fundamentais na prevencao do Diabetes Mellitus tipo 2 e no manejo de complicacoes metabolicas. O exercicio fisico regular aliado a uma dieta equilibrada e a melhor prevencao.

3. FATORES SOCIODEMOGRAFICOS E LETRAMENTO
A adesao dos pacientes as recomendacoes dieteticas depende fortemente do letramento nutricional. E crucial que os profissionais de saude utilizem linguagem acessivel.
"""
pdf.multi_cell(0, 10, text)
os.makedirs('data/raw/guidelines', exist_ok=True)
pdf.output('data/raw/guidelines/diretriz_sbd_mock.pdf', 'F')
print('PDF criado!')
