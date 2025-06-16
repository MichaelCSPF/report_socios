WITH 
    /* ========== DADOS POR CURVA ========== */
    ESTOQUE_CURVA AS (
        SELECT 
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1)   AS MES,
            C.DS_CURVA_REDE								    AS CURVA,
            SUM(A.QTD_ESTOQUE_SALDO)					    AS QTD_ESTOQUE,
            SUM(A.VL_TOTAL_CUSTO)				            AS VL_ESTOQUE
        
		FROM FT_ESTOQUE A
        
		JOIN DIM_PERIODO B 
          ON B.SK_DATA = A.SK_DATA
		  AND B.DATA = CAST(GETDATE() -1 AS date)
        
		JOIN DIM_PRODUTO C 
          ON C.SK_PRODUTO = A.SK_PRODUTO 
         AND C.CD_GRUPO_PRODUTO <> '39'
       
	   GROUP BY 
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1),
            C.DS_CURVA_REDE
    ),
    CMV_CURVA AS (
        SELECT
            DATEFROMPARTS(YEAR(A.DATA), MONTH(A.DATA), 1)	AS MES,
            A.CURVA											AS CURVA,
            SUM(A.VL_CMV)									AS VL_CMV
       
	   FROM FT_EMAIL_DIRETORIA_VENDAS_IMPOSTOS A
       
       
	   WHERE
			A.DATA < CAST(GETDATE()-4 AS date)
       
	   GROUP BY
            DATEFROMPARTS(YEAR(A.DATA), MONTH(A.DATA), 1),
            A.CURVA
    ),
   
   DU_CMV_CURVA AS (
        SELECT 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1)		AS MES,
            SUM(NR_PESO_DIA)								AS DU_CMV
        
		FROM DIM_PERIODO
        
		WHERE 
			DATA < CAST(GETDATE()-4 AS date)
        
		GROUP BY 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1)
    ),
    
	DU_CURVA AS (
        SELECT 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1)		AS MES,
            COUNT(DISTINCT SK_DATA)							AS DC,
            SUM(NR_PESO_DIA)								AS DU
        
		FROM DIM_PERIODO
        
		GROUP BY 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1)
    ),
    PROJ_CMV_CURVA AS (
        SELECT
            c.MES,
            c.CURVA,
            C.VL_CMV,
            X.DU_CMV										AS CDU,
            Y.DU											AS BDU,
            (C.VL_CMV / X.DU_CMV) * Y.DU					AS PROJECAO_CMV
        
		FROM 
			CMV_CURVA C
        
		JOIN 
			DU_CMV_CURVA X  ON X.MES = C.MES
        
		JOIN 
			DU_CURVA     Y  ON Y.MES = C.MES
    ),
   
   DEMANDA_CURVA AS (
        SELECT
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1)	AS MES,
            C.DS_CURVA_REDE									AS CURVA,
            SUM(A.QTD_DEMANDA_DIA)							AS QTD_DEMANDA
        
		FROM FT_DEMANDA_DIA A
        
		JOIN DIM_PERIODO B 
			ON B.SK_DATA = A.SK_DATA
        
		JOIN DIM_PRODUTO C 
			ON C.SK_PRODUTO = A.SK_PRODUTO 
			AND C.CD_GRUPO_PRODUTO<>'39'

        GROUP BY 
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1),
            C.DS_CURVA_REDE
    ),

    /* ========== DADOS TOTAIS ========== */
    ESTOQUE_TOTAL AS (
        SELECT 
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1)	AS MES,
            SUM(A.QTD_ESTOQUE_SALDO)						AS QTD_ESTOQUE,
            SUM(A.VL_TOTAL_CUSTO)							AS VL_ESTOQUE
        
		FROM FT_ESTOQUE A
        
		JOIN DIM_PERIODO B 
          ON B.SK_DATA = A.SK_DATA
		  AND B.DATA  = CAST(GETDATE() -1 AS DATE)
        
		JOIN DIM_PRODUTO C 
			ON C.SK_PRODUTO = A.SK_PRODUTO 
			AND C.CD_GRUPO_PRODUTO <> '39'
        
		GROUP BY 
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1)
    ),
    
	CMV_TOTAL AS (
        SELECT
            DATEFROMPARTS(YEAR(A.DATA), MONTH(A.DATA), 1)   AS MES,
            SUM(A.VL_CMV)                                   AS VL_CMV
        
		FROM FT_EMAIL_DIRETORIA_VENDAS_IMPOSTOS A
        
		WHERE 
			A.DATA < CAST(GETDATE()-4 AS date)
        
		GROUP BY
            DATEFROMPARTS(YEAR(A.DATA), MONTH(A.DATA), 1)
    ),
    
	DU_CMV_TOTAL AS (
        SELECT 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1) AS MES,
            SUM(NR_PESO_DIA)                         AS DU_CMV
        
		FROM DIM_PERIODO
        
		WHERE 
			DATA < CAST(GETDATE()-4 AS date)
        
		GROUP BY 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1)
    ),

    DU_TOTAL AS (
        SELECT 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1) AS MES,
            COUNT(DISTINCT SK_DATA)                  AS DC,
            SUM(NR_PESO_DIA)                         AS DU
     
		FROM DIM_PERIODO
        
		GROUP BY 
            DATEFROMPARTS(YEAR(DATA), MONTH(DATA), 1)
    ),
    
	PROJ_CMV_TOTAL AS (
        SELECT
            C.MES,
            C.VL_CMV,
            X.DU_CMV      AS CDU,
            Y.DU          AS BDU,
            (C.VL_CMV / X.DU_CMV) * Y.DU AS PROJECAO_CMV
        
		FROM 
			CMV_TOTAL C
        
		JOIN DU_CMV_TOTAL X 
			ON X.MES = C.MES
        
		JOIN DU_TOTAL Y 
			ON Y.MES = C.MES
    ),
    
	DEMANDA_TOTAL AS (
        SELECT
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1) AS MES,
            SUM(A.QTD_DEMANDA_DIA)                       AS QTD_DEMANDA
		
		FROM FT_DEMANDA_DIA A
        
		JOIN DIM_PERIODO B 
			ON B.SK_DATA = A.SK_DATA
        
		JOIN DIM_PRODUTO C 
			ON C.SK_PRODUTO = A.SK_PRODUTO AND C.CD_GRUPO_PRODUTO<>'39'
        
		GROUP BY 
            DATEFROMPARTS(YEAR(B.DATA), MONTH(B.DATA), 1)
    )

/* ========== SELECT FINAL UNIFICADO ========== */
SELECT
    'CURVA'											AS Nivel,
    CAST(FORMAT(GETDATE()-1, 'yyyy-MM-dd') AS date)	AS Periodo,
    C.CURVA											AS CURVA,
    C.QTD_ESTOQUE / D.QTD_DEMANDA					AS COBERTURA_DIAS,
    (C.VL_ESTOQUE / P.PROJECAO_CMV) * U.DC			AS DIAS_CMV,
    C.VL_ESTOQUE									AS R$_ESTOQUE

FROM ESTOQUE_CURVA C

LEFT JOIN PROJ_CMV_CURVA P 
	ON P.MES = C.MES AND P.CURVA = C.CURVA

LEFT JOIN DU_CURVA U 
	ON U.MES = C.MES

LEFT JOIN DEMANDA_CURVA D 
	ON D.MES = C.MES AND D.CURVA = C.CURVA


UNION ALL


SELECT
    'TOTAL'											AS Nivel,
    CAST(FORMAT(GETDATE()-1, 'yyyy-MM-dd') AS date)	AS Periodo,
    'VENANCIO'										AS CURVA,
    T.QTD_ESTOQUE / D.QTD_DEMANDA					AS COBERTURA_DIAS,
    (T.VL_ESTOQUE / P.PROJECAO_CMV) * U.DC			AS DIAS_CMV,
    T.VL_ESTOQUE									AS R$_ESTOQUE

FROM ESTOQUE_TOTAL T

LEFT JOIN PROJ_CMV_TOTAL P 
	ON P.MES = T.MES

LEFT JOIN DU_TOTAL U 
	ON U.MES = T.MES

LEFT JOIN DEMANDA_TOTAL D 
	ON D.MES = T.MES

ORDER BY 
	Nivel desc , CURVA asc
