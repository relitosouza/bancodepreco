---
name: Banco de Preços PNCP
description: Painel de comparação de preços públicos baseado no PNCP e IBGE.
colors:
  primary: "#0058be"
  primary-container: "#2170e4"
  neutral-bg: "#f7f9fb"
  surface-lowest: "#ffffff"
  surface-low: "#f2f4f6"
  surface-container: "#eceef0"
  on-surface: "#191c1e"
  on-surface-variant: "#424754"
  outline-variant: "#c2c6d6"
  error: "#ba1a1a"
typography:
  display:
    fontFamily: "Inter, sans-serif"
    fontSize: "32px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Inter, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.33
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "Inter, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.43
  label:
    fontFamily: "Inter, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.33
    letterSpacing: "0.05em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  full: "9999px"
spacing:
  base: "8px"
  card-gap: "16px"
  gutter-grid: "20px"
  container-padding: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface-lowest}"
    rounded: "{rounded.md}"
    padding: "8px 24px"
  button-primary-hover:
    backgroundColor: "{colors.primary-container}"
  input-search:
    backgroundColor: "{colors.surface-lowest}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "16px 48px"
---

# Design System: Banco de Preços PNCP

## 1. Overview

**Creative North Star: "A Lanterna Pública (The Public Lantern)"**

Este sistema de design foi criado sob a metáfora da "Lanterna Pública", focando em iluminar dados de compras e contratações de forma transparente, estruturada e precisa. A interface destina-se a simplificar a carga cognitiva de compradores públicos, fornecendo respostas rápidas sobre a média de mercado e o impacto do porte populacional de municípios nas licitações.

O design afasta-se de excessos cromáticos ou elementos puramente decorativos. Em vez disso, baseia-se em um layout limpo com contraste otimizado, tipografia altamente legível e usabilidade impecável. Rejeitamos decorações desnecessárias, priorizando a utilidade analítica e a seriedade técnica.

**Key Characteristics:**
- Foco em legibilidade e contraste de dados.
- Layout limpo e arejado, diminuindo a complexidade visual.
- Tonal layering (divisão de áreas por cores de fundo) em vez de bordas ou sombras pesadas.
- Componentes refinados com feedbacks sutis e precisos.

## 2. Colors

O sistema de cores adota uma estratégia profissional baseada em tons de azul profundo como âncoras de destaque, aplicados sobre fundos cinza-azulados de alta clareza para manter a leitura confortável por longas horas de análise.

### Primary
- **Deep Royal Blue** (#0058be): O tom principal de marca e ações principais. Usado para CTAs principais, ícones de foco e destaque analítico primário.

### Secondary
- **Vibrant Blue** (#2170e4): Usado como cor de destaque secundário e em estados hover de botões primários.

### Neutral
- **Near Black Ink** (#191c1e): Usado para o texto principal do corpo e cabeçalhos, oferecendo excelente taxa de contraste.
- **Charcoal Gray** (#424754): Usado para textos secundários e rótulos de menor prioridade.
- **Soft Slate White** (#f7f9fb): O fundo padrão de páginas e telas, suave aos olhos.
- **Pure White** (#ffffff): Cor das áreas de conteúdo e cartões em primeiro plano.
- **Light Gray-Blue** (#f2f4f6): Fundo de barras laterais e cabeçalhos de tabela.
- **Border Gray** (#c2c6d6): Cor das divisórias e linhas de borda discretas.

### Named Rules
**The Accent Rarity Rule.** A cor de destaque primária (#0058be) é reservada para elementos de ação reais e marcadores cruciais de estado. Ela deve ocupar no máximo 10% da superfície de qualquer tela para que retenha seu poder de atração visual.

**The Contrasting Ink Rule.** Nenhum texto com papel informativo pode ser exibido com contraste inferior a 4.5:1. Textos em cinza-claro são estritamente proibidos em qualquer elemento de leitura.

## 3. Typography

**Display Font:** Inter, sans-serif
**Body Font:** Inter, sans-serif
**Label/Mono Font:** Inter, sans-serif
**Icon Font:** Material Symbols Outlined

A tipografia do sistema é baseada na família "Inter", garantindo excelente legibilidade em pequenas frações de dados e robustez geométrica nos títulos principais.

### Hierarchy
- **Display** (700, 32px, 1.25): Títulos principais de boas-vindas e análise geral.
- **Headline** (600, 24px, 1.33): Títulos de seções principais ou termos em foco.
- **Title** (600, 20px, 1.4): Títulos de cartões, métricas secundárias e rótulos de filtros.
- **Body** (400, 14px, 1.43): Corpo de texto geral, dados de tabelas e descrições curtas.
- **Label** (600, 12px, 1.33, uppercase): Identificadores de colunas, badges, e marcas com espaçamento de 0.05em.

## 4. Elevation

Este sistema é predominantemente bidimensional e limpo, adotando a filosofia **Flat-by-default**. A separação física entre seções é realizada através de contraste tonal de fundos (tonal layering) em vez de empilhamento com sombras pesadas.

### Shadow Vocabulary
- **Interactive Glow** (`box-shadow: 0 4px 12px rgba(0,0,0,0.05)`): Utilizado em cartões clicáveis ou elementos de foco interativos no estado `:hover`.
- **Active Overlay** (`box-shadow: 0 8px 24px rgba(0,0,0,0.08)`): Utilizado temporariamente em elementos suspensos como dropdowns de autocompletar e popovers.

### Named Rules
**The Flat Rest Rule.** Superfícies e cartões devem permanecer completamente planos e integrados ao plano de fundo no estado de repouso. Elevações e sombras são acionadas apenas como resposta direta a interações (hover/focus).

## 5. Components

### Buttons
- **Shape:** Cantos levemente suavizados (8px).
- **Primary:** Fundo em Deep Royal Blue (#0058be), texto em Pure White (#ffffff), padding lateral de 24px e vertical de 8px.
- **Hover / Focus:** Transição de cor de fundo para Vibrant Blue (#2170e4) em 200ms com redução de escala para 98% ao clique. Foco exibe anel outline azul de 2px.

### Inputs / Fields
- **Style:** Fundo em Pure White (#ffffff), contorno sutil em Border Gray (#c2c6d6), cantos suavizados (12px).
- **Focus:** Contorno é realçado em Deep Royal Blue (#0058be) com anel de brilho de 2px em opacidade reduzida.
- **Error:** Borda realçada em vermelho alerta (#ba1a1a) com mensagem de apoio logo abaixo do campo.

### Cards / Containers
- **Corner Style:** Cantos médios (12px).
- **Background:** Pure White (#ffffff).
- **Shadow Strategy:** Completamente plano em repouso. Ao hover, aplica `Interactive Glow` com transição suave.
- **Border:** Contorno sutil em Border Gray (#c2c6d6) para delimitação limpa.
- **Internal Padding:** Margens internas generosas de 24px para evitar compressão.

### Navigation
- **Sidebar:** Fundo em Light Gray-Blue (#f2f4f6), largura fixa de 280px. Links de navegação usam estados ativos com preenchimento em azul claro e texto com contraste acentuado.

## 6. Do's and Don'ts

### Do:
- **Do** manter a legibilidade máxima utilizando sempre textos contrastantes sobre fundos claros.
- **Do** utilizar o espaçamento padrão (base de 8px e gaps de 16px/24px) para manter a harmonia visual em grades.
- **Do** restringir o uso de cores vibrantes apenas a pontos de ação ou estados informativos relevantes.

### Don't:
- **Don't** aplicar listras ou barras laterais coloridas de destaque maiores do que 1px em cartões de dados (anti-pattern de side-stripe borders).
- **Don't** utilizar textos com gradientes multicoloridos ou efeitos de vidro decorativos (glassmorphism) fora do contexto do painel de cabeçalho.
- **Don't** amontoar elementos de dados ou tabelas sem o espaçamento e margem corretos de 16px/24px.
- **Don't** adicionar sombras fortes, escuras ou pixeladas em cartões estáticos (evitar visual carregado).
- **Don't** usar o tom neon ou contrastante excessivo como cor principal de grandes fundos ou seções.
