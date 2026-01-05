SET XACT_ABORT ON;
SET NOCOUNT ON;

------------------------------------------------------------
-- PARÂMETROS DE ENTRADA (exemplo; no seu loop você troca)
------------------------------------------------------------
DECLARE @CodPedido      VARCHAR(10) = '0000000004';
DECLARE @CodItem        VARCHAR(7)  = '0000001';
DECLARE @Quantidade     DECIMAL(13,3) = 2;
DECLARE @ValorUnitario  DECIMAL(14,4) = 10;
DECLARE @ValorTotal     DECIMAL(13,2) = 20;
DECLARE @CodVendedor    VARCHAR(3)  = '001';
DECLARE @Estacao        VARCHAR(50) = NULL; -- se vier nulo, uso HOST_NAME()

------------------------------------------------------------
-- VARIÁVEIS AUTOMÁTICAS
------------------------------------------------------------
DECLARE @DataCadastro     DATETIME = CONVERT(DATETIME, CONVERT(DATE, GETDATE())); -- data com hora zerada
DECLARE @Cadastrado       VARCHAR(10) = 'MOBILE';
DECLARE @DataAtualizacao  DATETIME = GETDATE();
DECLARE @Atualizado       VARCHAR(10) = 'MOBILE';

------------------------------------------------------------
-- CONTROLE / SEQUÊNCIA
------------------------------------------------------------
DECLARE @SeqInt INT, @Seq CHAR(7);

SET @Estacao = COALESCE(@Estacao, HOST_NAME());

BEGIN TRAN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 1) Garante a linha de controle do pedido (sem NULL em ValorAnterior)
IF NOT EXISTS (
    SELECT 1
    FROM [SYS~Sequencial] WITH (UPDLOCK, HOLDLOCK)
    WHERE [SYS~Chave]  = @CodPedido
      AND [SYS~Tabela] = 'Pedidos Itens'
      AND [SYS~Campo]  = 'SEQ'
)
BEGIN
    INSERT INTO [SYS~Sequencial]
        ([SYS~BD], [SYS~Tabela], [SYS~Campo], [SYS~Chave],
         [SYS~Valor], [SYS~ValorAnterior], [SYS~Estacao],
         [SYS~Identificacao], [SYS~Pendentes])
    VALUES
        ('WM', 'Pedidos Itens', 'SEQ', @CodPedido,
         0, 0, @Estacao, '1671179755,29169', 0);
END

-- 2) Incrementa e captura o novo valor de sequência
DECLARE @out TABLE (ValorSqlSqlVariant SQL_VARIANT);

UPDATE S WITH (UPDLOCK, HOLDLOCK)
   SET [SYS~ValorAnterior] = TRY_CAST(S.[SYS~Valor] AS INT),
       [SYS~Valor]         = TRY_CAST(S.[SYS~Valor] AS INT) + 1,
       [SYS~Pendentes]     = TRY_CAST(S.[SYS~Valor] AS INT) + 1,
       [SYS~Estacao]       = @Estacao,
       [SYS~Identificacao] = '1671179755,29169'
OUTPUT inserted.[SYS~Valor] INTO @out(ValorSqlSqlVariant)
FROM [SYS~Sequencial] AS S
WHERE S.[SYS~Chave]  = @CodPedido
  AND S.[SYS~Tabela] = 'Pedidos Itens'
  AND S.[SYS~Campo]  = 'SEQ';

-- 3) Prepara o SEQ formatado
SELECT @SeqInt = TRY_CAST(ValorSqlSqlVariant AS INT) FROM @out;
SET @Seq = RIGHT('0000000' + CONVERT(VARCHAR(7), @SeqInt), 7);

-- 4) Insere o item já com o SEQ calculado
INSERT INTO [Pedidos Itens] (
  [Código Pedido], SEQ, [Código Item],
  Quantidade, [Valor Unitário], [Valor Total],
  [Tipo Item], [Preço Sugerido], [Valor Unitário Bruto],
  [Valor Total Bruto], Pendente, Ok,
  Item, [Quantidade Atacado], [Data Cadastro],
  Cadastrado, [Data Atualização], Atualizado
)
VALUES (
  @CodPedido, @Seq, @CodItem,
  @Quantidade, @ValorUnitario, @ValorTotal,
  'P', @ValorUnitario, @ValorUnitario,
  @ValorTotal, 1, 1,
  @CodItem, @Quantidade, @DataCadastro,
  @Cadastrado, @DataAtualizacao, @Atualizado
);

COMMIT;
