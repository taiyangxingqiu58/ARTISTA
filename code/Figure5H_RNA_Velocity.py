import scanpy as sc
import dynamo as dyn
import pandas as pd 
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 
from scipy.sparse import csr_matrix
import squidpy as sq
import sys
import time
import os
import matplotlib.pyplot as plt
import re
from pandas.core.frame import DataFrame

os.chdir('../data/Figure5_data/Figure5H')
involocito = 'Batch1_Injury_15DPI_C_rep1_FP200000266TR_E6_VWPV4.loom'
inh5ad = 'Batch1_Injury_15DPI_C_rep1_FP200000266TR_E6_Annotation_0306.h5ad'
outpath = 'your path'
idname = 'Injury_15DPI_C_rep1_FP200000266TR_E6'

## volocito count matrix
adata_spl = sc.read_loom(involocito)
ind = DataFrame(adata_spl.obs.index)
ind.columns = ['index']
ind['cellid'] = ind['index'].map(lambda x:x.split(':')[1]).astype(str)
adata_spl.obs.index = "CELL."+ind['cellid'].values

adata_sel = sc.read_h5ad(inh5ad)
adata_sel.obsm['X_spatial'] = adata_sel.obsm['X_spatial']/40
adata_sel.obsm['spatial'] = adata_sel.obsm['spatial']/40

final_match = adata_spl.obs.index & adata_sel.obs.index
adata_spl_sel = adata_spl[final_match]
adata_spl_sel.obs = adata_sel[final_match].obs.copy()
adata_spl_sel.obsm = adata_sel[final_match].obsm.copy()

os.chdir(outpath)
sc.pl.spatial(adata_spl_sel, color = 'Annotation_0306', basis="spatial", size=1.3, spot_size=1)
plt.savefig('Annotation_0306.png')

co={
"CCKIN":"#FF8C00",
"CMPN":"#FFE4E1",
"CP":"#0000A6",
"DPEX":"#1CE6FF",
"ENDO":"#F6CAE5",
"IMN":"#8983BF",
"MCG":"#808000",
"MPEX":"#FF4A46",
"MPIN":"#F5F5DC",
"MSN":"#927d85",
"NPTXEX":"#A30059",
"NPYIN":"#FF90C9",
"NTNG1EX":"#8FBC8F",
"OBNBL":"#004EB0",
"OLIGO":"#f5cac3",
"REAEGC":"#BA0900",
"RIBEGC":"#A52A2A",
"SCGNIN":"#8FB0FF",
"SFRPEGC":"#e14aec",
"SSTIN":"#63FFAC",
"TAC2IN":"#F0988C",
"RIPC1":"#e8612C",
"RIPC2":"#669bbc",
"RIPC3":"#FFD39B",
"RIPC4":"#FFBBFF",
"TLNBL":"#A1A9D0",
"UnKnown":"#84a59d",
"VLMC":"#FFFF00",
"WNTEGC":"#71c33a",
"WSN":"#00868B",
"Immature DPEX":"#edc092",
"Immature CCKIN":"#C4A5DE",
"Immature MSN":"#faf3dd",
"DNBL5":"#A98BC6",
"Immature MPEX":"#bc6c25",
"DNBL4":"#2F7FC1",
"Immature NPTXEX":"#faa307",
"DNBL2":"#F8AC8C",
"DEGC":"#9395E7",
"DNBL1":"#B1CE46",
"Immature DMIN":"#0f4c5c",
"DNBL3":"#63E398",
"Immature CMPN":"#06d6a0",
"REAEGC_1":"#FFD700",
"REAEGC_2":"#7FFF00",
"REAEGC_3":"#00FFFF",
"REAEGC_4":"#FA8072"}

#### removed ####
set(adata_spl_sel.obs['D_V'])
set(adata_spl_sel.obs['inj_uninj'])
adata_spl_sel1 = adata_spl_sel[(adata_spl_sel.obs['inj_uninj'] == 'inj')].copy()
adata_spl_sel2 = adata_spl_sel1[(adata_spl_sel1.obs['D_V'] == 'D')].copy()
set(adata_spl_sel2.obs['Annotation_0306'])
adata_spl_sel2 = adata_spl_sel2[(adata_spl_sel2.obs['Annotation_0306'] == 'REAEGC')| (adata_spl_sel2.obs['Annotation_0306'] == 'RIPC1') |(adata_spl_sel2.obs['Annotation_0306'] == 'IMN') |(adata_spl_sel2.obs['Annotation_0306'] == 'NPTXEX')].copy()

adata_spl_sel3 = adata_spl[adata_spl_sel2.obs.index]
adata_spl_sel3.obs = adata_spl_sel2.obs.copy()
adata_spl_sel3.obsm = adata_spl_sel2.obsm.copy()
#adata_spl_sel3.obs['section'] = inj['section']

os.chdir(outpath)
sc.pl.spatial(adata_spl_sel3,spot_size = 1.3)
plt.savefig('injury_D_removed.png')

sc.pp.calculate_qc_metrics(adata_spl_sel3, expr_type='unspliced', layer = "unspliced", inplace = True)
sc.pp.calculate_qc_metrics(adata_spl_sel3, expr_type='spliced', layer = "spliced", inplace = True)
sc.pl.violin(adata_spl_sel3, ["n_genes_by_spliced",  "n_genes_by_unspliced"])
plt.savefig('injury_D_violin.n_genes.png')

sc.pl.violin(adata_spl_sel3, ["log1p_total_spliced",  "log1p_total_unspliced"])
plt.savefig('injury_D_violin.log1p_total.png')
sc.pl.violin(adata_spl_sel3, ["total_spliced",  "total_unspliced"])
plt.savefig('injury_D_violin.total.png')


expressed_genes = (adata_spl_sel3.layers['spliced'].A + adata_spl_sel3.layers['unspliced'].A).sum(0) > 500 #(adata.layers['spliced'].A + adata.layers['unspliced'].A).sum(0) > 10000
expressed_genes = adata_spl_sel3.var_names[expressed_genes]
len(expressed_genes)

sq.gr.spatial_neighbors(
    adata_spl_sel3,
    n_neighs = 8
)

sq.gr.spatial_autocorr(
    adata_spl_sel3,
    mode = 'moran',
    genes=list(expressed_genes),
    n_perms=100,
    n_jobs=30,
)

moran_top_gene = adata_spl_sel3.uns["moranI"].head(2000).index
moran_top_gene = expressed_genes.intersection(moran_top_gene)
final_gene = (set(moran_top_gene) & set(expressed_genes))

len(final_gene)
dyn.pp.recipe_monocle(adata_spl_sel3,
                      num_dim=30,
                      #genes_to_use=final_gene,
                      genes_to_append = list(final_gene)
                      #n_top_genes=len(expressed_genes),
                     )

dyn.tl.reduceDimension(adata_spl_sel3, enforce = True)
dyn.pl.umap(adata_spl_sel3, color='Annotation_0306',show_legend= 'on data')

dyn.tl.dynamics(adata_spl_sel3, model='stochastic', cores=20)

dyn.tl.gene_wise_confidence(adata_spl_sel3, group='Annotation_0306', lineage_dict={'REAEGC': ['NPTXEX']})
dyn.pl.phase_portraits(adata_spl_sel3, genes=adata_spl_sel3.var_names[adata_spl_sel3.var.use_for_dynamics][:4], figsize=(6, 4), color='Annotation_0306')
plt.savefig('injury_D_umap_phase_portraits.svg')

dyn.tl.cell_velocities(adata_spl_sel3, method="fp", basis='spatial',enforce=True,  transition_genes = list(adata_spl_sel3.var_names[adata_spl_sel3.var.use_for_pca]))

dyn.tl.cell_wise_confidence(adata_spl_sel3)
dyn.tl.confident_cell_velocities(adata_spl_sel3, group='Annotation_0306', lineage_dict={'REAEGC': ['NPTXEX']},only_transition_genes=True,basis='spatial')

dyn.pl.cell_wise_vectors(adata_spl_sel3, color=['Annotation_0306'], basis='spatial', show_legend='on data', quiver_length=6, quiver_size=6, pointsize=0.1, show_arrowed_spines=False,color_key=co,figsize=(4, 4))
plt.savefig('injury_D.cell_wise_vectors.spatial.svg')

dyn.pl.streamline_plot(adata_spl_sel3, color=['Annotation_0306'], basis='spatial', show_legend='on data',color_key=co,
                       quiver_length=6, quiver_size=6,  show_arrowed_spines=True,background='black',pointsize=0.5,
                       figsize=(4, 4),calpha=1,
                      )
plt.savefig('injury_D.cell_wise_plot.spatial.svg')

