# Build do executável desktop (Windows)

Este projeto tem dois pontos de entrada:

- `main.py` — uso em desenvolvimento (Codespace/terminal), com `python main.py` ou `python main.py -p` (carrega a planilha de amostra).
- `desktop.py` — empacotado com PyInstaller para gerar um `.exe` standalone, que abre o app numa janela nativa via `pywebview`, sem precisar de Python instalado na máquina do usuário.

## Opção 1: gerar via GitHub Actions (recomendado)

Não é preciso ter uma máquina Windows: o workflow [`.github/workflows/build-desktop.yml`](.github/workflows/build-desktop.yml) builda o `.exe` numa VM Windows do próprio GitHub.

- **Build rápido/manual (não publica nada)**: na aba *Actions* do repositório no GitHub, escolha o workflow "Build Desktop (Windows)" → *Run workflow*. Ao terminar, baixe o `.exe` em *Artifacts* na página da execução (fica disponível por um tempo limitado e só para quem tem acesso ao repositório).
- **Gerar uma versão para distribuir de verdade**: crie e publique uma tag `v*`, por exemplo:

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

  Isso dispara o build e, ao final, cria automaticamente uma **Release** no GitHub com o `DashboardDMAE.exe` anexado — é esse link de Release que você compartilha com quem for usar o app (basta baixar o `.exe` e clicar duas vezes, sem instalar nada).

  > Se o repositório for privado, quem for baixar precisa ter acesso a ele (login no GitHub). Para distribuir para qualquer pessoa sem restrição, o repositório (ou ao menos a Release) precisa ser público.

## Opção 2: build manual (rodar em uma máquina Windows)

1. Criar e ativar um ambiente virtual, e instalar as dependências de runtime + build:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. Gerar o executável:

   ```powershell
   pyinstaller --onefile --noconsole --name DashboardDMAE --add-data "assets;assets" --collect-all pywebview desktop.py
   ```

   O executável final fica em `dist/DashboardDMAE.exe`.

### Por que `--add-data "assets;assets"`

O Dash resolve a pasta `assets/` (CSS servido pelo app) a partir do caminho do módulo `main.py` no momento em que `Dash(...)` é instanciado. Quando o PyInstaller empacota o app, ele ajusta o `__file__` do módulo `main` para apontar para dentro da pasta de extração em tempo de execução (`sys._MEIPASS`). Isso significa que **não foi necessário alterar `main.py`** — basta garantir que a pasta `assets/` seja extraída para o mesmo lugar, o que o flag `--add-data "assets;assets"` faz. Isso foi validado lendo o código-fonte do `PyInstaller` e do `Flask`/`Dash` (ver `PyInstaller/loader/pyimod02_importers.py` e `flask.helpers.get_root_path`).

No Windows o separador do `--add-data` é `;` (em Linux/Mac seria `:`).

### Por que `--collect-all pywebview`

`pywebview` carrega arquivos próprios (JS de injeção, bindings da engine) como dados do pacote. Sem esse flag, builds do PyInstaller costumam falhar silenciosamente ao abrir a janela porque esses arquivos não são coletados automaticamente.

### Caminhos que NÃO precisam de ajuste

- `testes/dados_teste/amostra_dados.xlsx`: só é lido quando `main.py` roda com o argumento `-p` (fluxo de desenvolvimento/teste). O `desktop.py` nunca passa esse argumento, então esse caminho relativo nunca é exercitado no executável — não precisa ser empacotado.
- Não há outros caminhos relativos "ingênuos" no projeto (verificado em `main.py`, `calculos.py`, `elementos_html.py`).

## `.gitignore`

Os diretórios gerados pelo PyInstaller (`build/`, `dist/`) e o arquivo `.spec` já estavam cobertos pelo `.gitignore` existente (template padrão do Python) — nenhuma alteração foi necessária.

## Caveat de distribuição: Microsoft Edge WebView2 Runtime

No Windows, o `pywebview` usa por padrão o WebView2 (Chromium/Edge) como engine de renderização. Ele já vem instalado por padrão no Windows 11 e na maioria das instalações atualizadas do Windows 10, mas **não é garantido** em todas as máquinas. Se a janela abrir em branco ou o app falhar ao iniciar em uma máquina do usuário final, instale o "WebView2 Runtime" (Evergreen Bootstrapper, gratuito, da Microsoft) nessa máquina.

## Testando localmente antes de distribuir

Depois de gerar o `.exe`, execute-o numa máquina limpa (sem o ambiente de desenvolvimento) para confirmar que:

- a janela abre e mostra o layout normalmente (CSS aplicado);
- upload de planilha `.xlsx`, associação de colunas e filtros funcionam;
- download de planilhas (botões "Aplicar Filtros" → export) funciona (o Windows pode perguntar onde salvar).
