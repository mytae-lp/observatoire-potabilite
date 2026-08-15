# -*- coding: utf-8 -*-
"""La chloration varie-t-elle d'un bulletin a l'autre ?

Deux questions distinctes, souvent confondues :
  · variation d'un MEME point d'eau dans le temps  (intra-installation)
  · variation d'un point d'eau a l'autre           (inter-installation)
On les separe.
"""
import duckdb

con = duckdb.connect("data/eau.duckdb", read_only=True)

BASE = """
    SELECT p.code_installation_amont AS inst,
           p.code_prelevement        AS bull,
           p.date_prelevement        AS d,
           v.resultat_num            AS cl
    FROM v_mesures_verdict v
    JOIN prelevements p USING (code_prelevement)
    WHERE v.libelle_parametre = 'Chlore libre'
      AND v.est_quantifie AND v.resultat_num IS NOT NULL
      AND p.code_installation_amont IS NOT NULL
"""

print("=" * 76)
print("0. LE MATERIAU")
print("=" * 76)
r = con.execute(f"""
    SELECT COUNT(*), COUNT(DISTINCT inst), COUNT(DISTINCT bull),
           ROUND(MEDIAN(cl), 3), ROUND(MIN(cl), 3), ROUND(MAX(cl), 3)
    FROM ({BASE})
""").fetchone()
print("  %d mesures quantifiees | %d installations | %d bulletins" % r[:3])
print("  chlore libre : mediane %s, min %s, max %s" % (r[3], r[4], r[5]))

print()
print("=" * 76)
print("1. DECOMPOSITION DE LA VARIANCE — le point d'eau explique-t-il le chlore ?")
print("=" * 76)
r = con.execute(f"""
    WITH m AS ({BASE}),
    g AS (SELECT inst, AVG(cl) moy_inst, COUNT(*) n FROM m GROUP BY 1 HAVING COUNT(*) >= 3),
    j AS (SELECT m.cl, g.moy_inst FROM m JOIN g USING (inst))
    SELECT COUNT(*) n,
           ROUND(VAR_POP(cl), 5)                      AS var_totale,
           ROUND(VAR_POP(moy_inst), 5)                AS var_inter,
           ROUND(VAR_POP(cl) - VAR_POP(moy_inst), 5)  AS var_intra
    FROM j
""").fetchone()
n, tot, inter, intra = r
print("  sur %d mesures (installations a >= 3 mesures)" % n)
print("  variance totale                      : %s" % tot)
print("  variance INTER-installations         : %s" % inter)
print("  variance INTRA-installation (reste)  : %s" % intra)
if tot:
    print()
    print("  -> part expliquee par le POINT D'EAU  : %.1f %%" % (100.0*inter/tot))
    print("  -> part restant DANS un point d'eau   : %.1f %%" % (100.0*intra/tot))

print()
print("=" * 76)
print("2. LA DISPERSION A L'INTERIEUR D'UN MEME POINT D'EAU")
print("=" * 76)
rows = con.execute(f"""
    WITH m AS ({BASE}),
    s AS (SELECT inst, COUNT(*) n, AVG(cl) moy, STDDEV_POP(cl) et,
                 MIN(cl) mn, MAX(cl) mx
          FROM m GROUP BY 1 HAVING COUNT(*) >= 5)
    SELECT COUNT(*) installations,
           ROUND(MEDIAN(et / NULLIF(moy, 0)), 3)                   AS cv_median,
           ROUND(QUANTILE_CONT(et / NULLIF(moy,0), 0.25), 3)       AS cv_q1,
           ROUND(QUANTILE_CONT(et / NULLIF(moy,0), 0.75), 3)       AS cv_q3,
           ROUND(MEDIAN(mx - mn), 3)                               AS etendue_med,
           ROUND(MEDIAN(mx / NULLIF(mn, 0)), 1)                    AS rapport_med
    FROM s
""").fetchone()
print("  installations a >= 5 mesures : %d" % rows[0])
print("  coefficient de variation intra-installation :")
print("     Q1 %s | mediane %s | Q3 %s" % (rows[2], rows[1], rows[3]))
print("  etendue mediane (max - min) au sein d'un point d'eau : %s mg/L" % rows[4])
print("  rapport median max/min                               : x%s" % rows[5])

print()
print("=" * 76)
print("3. D'UN BULLETIN AU SUIVANT — l'ecart consecutif")
print("=" * 76)
r = con.execute(f"""
    WITH m AS ({BASE}),
    o AS (SELECT inst, d, cl,
                 LAG(cl) OVER (PARTITION BY inst ORDER BY d) prec
          FROM m)
    SELECT COUNT(*) paires,
           ROUND(MEDIAN(abs(cl - prec)), 3)                          AS ecart_abs_median,
           ROUND(MEDIAN(abs(cl - prec) / NULLIF((cl+prec)/2, 0)), 3) AS ecart_rel_median,
           ROUND(QUANTILE_CONT(abs(cl - prec), 0.9), 3)              AS ecart_abs_p90
    FROM o WHERE prec IS NOT NULL
""").fetchone()
print("  paires de bulletins consecutifs, meme point d'eau : %d" % r[0])
print("  ecart absolu median      : %s mg/L" % r[1])
print("  ecart RELATIF median     : %s  (soit %.0f %% de la valeur moyenne)"
      % (r[2], 100.0 * (r[2] or 0)))
print("  ecart absolu au 9e decile: %s mg/L" % r[3])
con.close()
