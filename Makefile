.PHONY: setup test dashboard requirements check-requirements

REQ_TMP := $(shell mktemp -u)

# requirements.txt é artefato derivado do lock; existe só porque o Streamlit
# Cloud não lê pyproject.toml. Gerado sempre pela mesma receita, para que a
# verificação de sincronia compare conteúdo e não formatação.
define gerar_req
printf '# ARQUIVO GERADO — não edite à mão.\n# Existe apenas porque o Streamlit Cloud lê requirements.txt, não pyproject.toml.\n# Regenerar com:  make requirements\n' > $(1) && uv export --no-dev --no-hashes --no-emit-project >> $(1)
endef

# Ambiente a partir do lockfile — mesma versão de tudo em qualquer máquina e no CI.
setup:
	uv sync

test:
	uv run pytest

# Mesmo entrypoint que o Streamlit Cloud usa.
dashboard:
	uv run streamlit run dashboard/app.py

requirements:
	@$(call gerar_req,requirements.txt)
	@echo "requirements.txt regenerado a partir de uv.lock"

# Gera numa cópia temporária e compara: regenerar sobre o próprio arquivo
# apagaria justamente a divergência que este alvo precisa detectar.
check-requirements:
	@$(call gerar_req,$(REQ_TMP))
	@diff -u requirements.txt $(REQ_TMP) \
		|| { rm -f $(REQ_TMP); echo "ERRO: requirements.txt está fora de sincronia com uv.lock. Rode 'make requirements'."; exit 1; }
	@rm -f $(REQ_TMP)
	@echo "requirements.txt está em sincronia com uv.lock"
