# Rollback do CyberFlow

## Versionamento

As imagens seguem versionamento semântico (`MAJOR.MINOR.PATCH`), gerado a partir de tags Git no formato `vX.Y.Z`. Cada tag publica no Docker Hub a imagem `danilovf/cyberflow-backend:X.Y.Z`. Pushes na `main` publicam `latest` e `sha-<commit>`.

Para lançar uma versão nova: `git tag -a vX.Y.Z -m "descrição"` e depois `git push origin vX.Y.Z`.

## Quando acionar

- O deploy da `main` falhou no health check.
- Uma versão publicada apresentou erro em produção.

## Como executar

1. No GitHub, abra a aba **Actions**.
2. Selecione o workflow **Rollback**.
3. Clique em **Run workflow**.
4. Informe a versão estável anterior (ex: `1.0.0`, sem o `v`).
5. Marque **promover latest** se quiser que `latest` volte a apontar para essa versão.
6. Clique em **Run workflow** para confirmar.

## Como verificar o sucesso

- O job termina verde e o passo de verificação imprime `Rollback simulado OK`.
- A aba **Summary** da execução mostra a versão restaurada.

## Critérios de falha

- Formato de versão inválido (o workflow aceita apenas `X.Y.Z`).
- A tag informada não existe no Docker Hub.
- A API não responde em `/incidentes` após 10 tentativas com intervalo de 3 segundos.

Em qualquer falha o job fica vermelho e os logs do container são exibidos.

## Depois do rollback

1. Abra uma issue descrevendo o problema da versão com falha.
2. Corrija em uma branch `fix/...` e abra um PR.
3. Publique a correção como um novo PATCH (ex: `v1.0.2`). Nunca reutilize uma tag já publicada.
