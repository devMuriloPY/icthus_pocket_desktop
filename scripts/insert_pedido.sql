--Variaveis a declarar
/*Pegar ultimo codigo pedido
SET @CodPedido = (SELECT TOP (1) 
  RIGHT('0000000000' + CAST(CAST([Código Pedido] AS INT) + 1 AS VARCHAR(7)), 7) 
  FROM Pedidos ORDER BY [Código Pedido] DESC);
  
  */
DECLARE @CodPedido varchar(10)
DECLARE @CodCliente varchar(7) = '0000358'
DECLARE @CodVendedor varchar(3) = '001'
DECLARE @ValorTotal decimal(13,2) = 100
DECLARE @ValorProdutos decimal(13,2) = 100
DECLARE @QuantidadeProdutos decimal(13, 3) = 1

--Variaveis Automaticas

DECLARE @DataEmissao datetime = CONVERT(DATETIME, CONVERT(DATE, GETDATE()));

DECLARE @HoraEmissao DATETIME = CONVERT(DATETIME, CONVERT(TIME, GETDATE()));

DECLARE @DocumentoVenda varchar(15) = '1 - Pedido'
DECLARE @OrigemVenda varchar(5) = '3 - Mobile'
DECLARE @FormaPagamento varchar(15) = '1 - À Prazo'
DECLARE @CodigoCC varchar(3) = '001'
DECLARE @DataCadastro datetime = CONVERT(DATETIME, CONVERT(DATE, GETDATE()));
DECLARE @Cadastrado varchar(10) = 'MOBILE'
DECLARE @DataAtualizacao datetime = GETDATE();
DECLARE @Atualizado varchar(10) = 'MOBILE'


INSERT INTO Pedidos (
  [Código Pedido], [Código Cliente], 
  [Data Emissão], [Hora Emissão], 
  [Documento Venda], [Código Vendedor], 
  [Valor Total], [Valor Produtos], [Valor Total Bruto], 
  [Origem Venda], [Forma Pagamento], 
  [Código CC], [Quantidade Produtos], 
  Ok, [Código Empresa], [Data Cadastro], 
  Cadastrado, [Data Atualização], 
  Atualizado
) 
Values 
  (
    @CodPedido, @CodCliente, @DataEmissao, 
    @HoraEmissao, @DocumentoVenda, @CodVendedor, 
    @ValorTotal, @ValorProdutos, @ValorTotal, 
    @OrigemVenda, @FormaPagamento, @CodigoCC, 
    @QuantidadeProdutos, 1, 1, @DataCadastro, 
    @Cadastrado, @DataAtualizacao, @Atualizado
  )



